"""
CareerCompass AI — backend API.

Run locally:
    cd backend
    pip install -r requirements.txt
    cp .env.example .env          # then paste your Gemini key into .env
    python app.py

In production (Render):
    gunicorn "app:create_app()"
"""

import json
import logging
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from flask import Flask, Response, g, jsonify, request
from flask_cors import CORS
import segno

import auth
import config
import db
import gemini
import interview
import matching
from careers_data import ACADEMIC_SUBJECTS, DIMS
from dashboards import bp as dashboards_bp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("careercompass")

MAX_ANSWER_CHARS = 1200
MAX_TRANSCRIPT_TURNS = 40


# ------------------------------------------------------------ rate limiting --

_hits = defaultdict(deque)


def _client_key() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    return (forwarded.split(",")[0].strip() or request.remote_addr or "unknown")


def rate_limited(limit_per_minute: int) -> bool:
    """Simple in-process sliding window. Good enough for one Render instance."""
    now = time.time()
    bucket = _hits[(_client_key(), request.path)]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= limit_per_minute:
        return True
    bucket.append(now)
    return False


# ---------------------------------------------------------------- helpers --

def json_body() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def clean_lang(value) -> str:
    return "ta" if str(value or "").lower().startswith("ta") else "en"


def clean_academics(raw):
    """Marks out of 100 for the five subjects. Anything else is dropped."""
    if not isinstance(raw, dict):
        return None
    out = {}
    for subject in ACADEMIC_SUBJECTS:
        if subject not in raw or raw[subject] in (None, ""):
            continue
        try:
            value = float(raw[subject])
        except (TypeError, ValueError):
            continue
        out[subject] = max(0.0, min(100.0, value))
    return out or None


def clean_scale(value):
    """A 1-5 rating, or None."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if 1 <= number <= 5 else None


def clean_transcript(raw):
    if not isinstance(raw, list):
        return []
    out = []
    for turn in raw[:MAX_TRANSCRIPT_TURNS]:
        if not isinstance(turn, dict):
            continue
        role = "ai" if turn.get("role") == "ai" else "student"
        text = str(turn.get("text", ""))[:MAX_ANSWER_CHARS].strip()
        if text:
            entry = {"role": role, "text": text}
            if turn.get("qid"):
                entry["qid"] = str(turn["qid"])[:40]
            out.append(entry)
    return out


# ------------------------------------------------------------------ scoring --

def score_interview(transcript, academics, lang, user_row=None):
    """Shared by /api/interview/finish and /api/match."""
    profile = interview.build_profile(transcript, lang)

    career_rows = db.get_db().execute(
        "SELECT name, name_ta, category, blurb, blurb_ta, vector, academic FROM careers"
    ).fetchall()

    result = matching.rank_careers(profile["vector"], academics, career_rows, top_n=3)
    top_df, combined = result["top"], result["combined_vector"]

    gap_rows = matching.skill_gap(combined, top_df.iloc[0], lang)
    plan = matching.roadmap(gap_rows, top_df.iloc[0]["name"], lang)

    to_explain = []
    for _, row in top_df.iterrows():
        strong = [d for d in DIMS if float(row[d]) >= 4]
        to_explain.append({
            "name": row["name"],
            "needs": ", ".join(strong),
            "strong_dims": strong,
        })
    reasons = interview.explain(transcript, to_explain, combined, lang)

    matches = []
    for _, row in top_df.iterrows():
        matches.append({
            "name": row["name_ta"] if lang == "ta" else row["name"],
            "nameEn": row["name"],
            "category": row["category"],
            "blurb": row["blurb_ta"] if lang == "ta" else row["blurb"],
            "similarity": round(float(row["similarity"]) * 100),
            "fit": round(float(row["fit"]) * 100),
            "academicFit": round(float(row["academic_fit"]) * 100),
            "why": reasons.get(row["name"], ""),
        })

    engine = "gemini" if (profile.get("engine") == "gemini") else "fallback"

    payload = {
        "summary": profile.get("summary", ""),
        "evidence": profile.get("evidence", {}),
        "consistency": profile.get("consistency"),
        "topSkills": matching.top_skills(combined, 3, lang),
        "matches": matches,
        "gap": {
            "careerName": matches[0]["name"],
            "rows": gap_rows,
        },
        "roadmap": plan,
        "engine": engine,
        "usedAcademics": bool(academics),
        "scoring": {
            "interestWeight": config.INTEREST_WEIGHT,
            "academicWeight": config.ACADEMIC_WEIGHT,
        },
    }

    vectors = {
        "interest": [round(float(v), 3) for v in result["interest_vector"]],
        "academic": [round(float(v), 3) for v in result["academic_vector"]],
        "combined": [round(float(v), 3) for v in combined],
    }
    return payload, vectors, top_df


def save_submission(payload, vectors, top_df, transcript, academics, lang,
                    user_row=None, session_id=None):
    database = db.get_db()
    database.execute(
        """INSERT INTO submissions
           (created_at, user_id, session_id, language, engine, interest_vector,
            academic_vector, combined_vector, top_career, top_similarity,
            top_fit, result)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (datetime.now(timezone.utc).isoformat(),
         user_row["id"] if user_row is not None else None,
         session_id, lang, payload["engine"],
         json.dumps(vectors["interest"]), json.dumps(vectors["academic"]),
         json.dumps(vectors["combined"]),
         top_df.iloc[0]["name"], float(top_df.iloc[0]["similarity"]),
         float(top_df.iloc[0]["fit"]), json.dumps(payload)),
    )
    database.commit()


# -------------------------------------------------------------- app factory --

def create_app():
    app = Flask(__name__)
    CORS(app, origins=config.ALLOWED_ORIGINS, supports_credentials=False)
    app.teardown_appcontext(db.close_db)
    app.register_blueprint(dashboards_bp)

    db.init_db()

    @app.errorhandler(auth.AuthError)
    def handle_auth_error(exc):
        return jsonify({"error": exc.message}), exc.status

    @app.errorhandler(500)
    def handle_500(exc):
        log.exception("unhandled error")
        return jsonify({"error": "Something broke on our side. Try again."}), 500

    @app.before_request
    def guard():
        if request.method == "OPTIONS":
            return None
        if not request.path.startswith("/api/"):
            return None
        limit = (config.AUTH_RATE_LIMIT_PER_MINUTE
                 if request.path.startswith("/api/auth/")
                 else config.RATE_LIMIT_PER_MINUTE)
        if rate_limited(limit):
            return jsonify({"error": "Too many requests. Wait a minute and try again."}), 429
        return None

    # ------------------------------------------------------------- health --

    @app.get("/api/health")
    def health():
        status = gemini.probe()
        return jsonify({
            "status": "ok",
            "service": "CareerCompass AI backend",
            "geminiConfigured": status["configured"],
            # True only if a real call just succeeded — a key can exist and still fail.
            "geminiReachable": status["reachable"],
            "geminiModel": status["model"] if status["configured"] else None,
            "geminiError": status["error"],
            "languages": ["en", "ta"],
        })

    @app.get("/api/careers")
    def list_careers():
        lang = clean_lang(request.args.get("lang"))
        rows = db.get_db().execute(
            "SELECT name, name_ta, category, blurb, blurb_ta FROM careers ORDER BY category, name"
        ).fetchall()
        return jsonify([{
            "name": r["name_ta"] if lang == "ta" else r["name"],
            "nameEn": r["name"],
            "category": r["category"],
            "blurb": r["blurb_ta"] if lang == "ta" else r["blurb"],
        } for r in rows])

    @app.get("/api/stats")
    def stats():
        database = db.get_db()
        total = database.execute("SELECT COUNT(*) AS n FROM submissions").fetchone()["n"]
        top = database.execute(
            "SELECT top_career, COUNT(*) AS n FROM submissions "
            "GROUP BY top_career ORDER BY n DESC LIMIT 1"
        ).fetchone()
        students = database.execute(
            "SELECT COUNT(*) AS n FROM users WHERE role = 'student'"
        ).fetchone()["n"]
        fb = database.execute(
            """SELECT COUNT(*) AS n, AVG(f.rating) AS rating,
                      AVG(CASE WHEN f.confidence_after IS NOT NULL
                                AND s.confidence_before IS NOT NULL
                               THEN f.confidence_after - s.confidence_before END) AS lift,
                      AVG(CASE WHEN f.would_act = 'yes' THEN 1.0
                               WHEN f.would_act IS NULL THEN NULL ELSE 0.0 END) AS act
               FROM feedback f JOIN sessions s ON s.id = f.session_id"""
        ).fetchone()
        return jsonify({
            "totalSubmissions": total,
            "mostCommonTopMatch": top["top_career"] if top else None,
            "registeredStudents": students,
            "feedbackCount": fb["n"],
            "averageRating": round(fb["rating"], 2) if fb["rating"] is not None else None,
            "averageConfidenceChange": round(fb["lift"], 2) if fb["lift"] is not None else None,
            "shareWhoWouldActOnTop3": round(fb["act"], 2) if fb["act"] is not None else None,
        })

    # --------------------------------------------------- feedback + share --

    @app.post("/api/feedback")
    def feedback():
        """The three post-launch measures on slide 23, captured per session."""
        body = json_body()
        session_id = str(body.get("sessionId") or "")[:64]
        rating = clean_scale(body.get("rating"))
        if rating is None:
            return jsonify({"error": "Choose a rating from 1 to 5."}), 400

        database = db.get_db()
        session = database.execute(
            "SELECT id, state, user_id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if session is None:
            return jsonify({"error": "That interview session was not found."}), 404
        if session["state"] != "done":
            return jsonify({"error": "Finish the interview before rating it."}), 409

        would_act = str(body.get("wouldAct") or "").lower()
        if would_act not in {"yes", "maybe", "no"}:
            would_act = None
        comment = str(body.get("comment") or "").strip()[:500] or None

        database.execute(
            """INSERT INTO feedback (created_at, session_id, user_id, rating,
                                     confidence_after, would_act, comment)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(session_id) DO UPDATE SET
                   rating=excluded.rating, confidence_after=excluded.confidence_after,
                   would_act=excluded.would_act, comment=excluded.comment""",
            (datetime.now(timezone.utc).isoformat(), session_id, session["user_id"],
             rating, clean_scale(body.get("confidenceAfter")), would_act, comment),
        )
        database.commit()
        return jsonify({"saved": True})

    @app.get("/api/qr")
    def qr_code():
        """
        A QR code so a classroom can put the site on a projector and students
        scan it. Only encodes URLs on an allowed origin, so this can't be used
        as a free QR service for arbitrary links.
        """
        url = (request.args.get("url") or "").strip()
        if not url or len(url) > 300:
            return jsonify({"error": "Provide a url."}), 400
        if not any(url == o or url.startswith(o.rstrip("/") + "/") for o in config.ALLOWED_ORIGINS):
            return jsonify({"error": "That address isn't one this site serves."}), 400

        import io
        buffer = io.BytesIO()
        segno.make(url, error="m").save(buffer, kind="svg", scale=8, border=2,
                                        dark="#1F2A37", light="#FFFFFF")
        return Response(buffer.getvalue(), mimetype="image/svg+xml",
                        headers={"Cache-Control": "public, max-age=86400"})

    # --------------------------------------------------------------- auth --

    @app.post("/api/auth/register")
    def register():
        clean = auth.validate_registration(json_body())
        user_id = auth.create_user(clean)
        row = db.get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return jsonify({
            "token": auth.issue_token(user_id, clean["role"]),
            "user": auth.public_user(row),
        }), 201

    @app.post("/api/auth/login")
    def login():
        body = json_body()
        row = auth.verify_login(body.get("email"), body.get("password"))
        return jsonify({
            "token": auth.issue_token(row["id"], row["role"]),
            "user": auth.public_user(row),
        })

    @app.get("/api/auth/me")
    @auth.login_required()
    def me():
        user = dict(auth.public_user(g.user))
        user["academics"] = json.loads(g.user["academics"]) if g.user["academics"] else None
        return jsonify(user)

    @app.post("/api/auth/academics")
    @auth.login_required("student")
    def save_academics():
        academics = clean_academics(json_body().get("academics"))
        if academics is None:
            return jsonify({"error": "Enter marks out of 100 for at least one subject."}), 400
        database = db.get_db()
        database.execute("UPDATE users SET academics = ? WHERE id = ?",
                         (json.dumps(academics), g.user["id"]))
        database.commit()
        return jsonify({"academics": academics})

    @app.post("/api/auth/language")
    @auth.login_required()
    def set_language():
        lang = clean_lang(json_body().get("language"))
        database = db.get_db()
        database.execute("UPDATE users SET language = ? WHERE id = ?", (lang, g.user["id"]))
        database.commit()
        return jsonify({"language": lang})

    # ---------------------------------------------------------- interview --

    @app.post("/api/interview/start")
    def interview_start():
        body = json_body()
        lang = clean_lang(body.get("language"))
        user = auth.current_user(required=False)
        if user is not None:
            lang = clean_lang(body.get("language") or user["language"])

        first = interview.opening_question(lang)
        session_id = secrets.token_urlsafe(12)
        now = datetime.now(timezone.utc).isoformat()
        transcript = [{"role": "ai", "text": first["question"], "qid": "subjects"}]
        engine = "gemini" if gemini.probe()["reachable"] else "fallback"
        confidence_before = clean_scale(body.get("confidenceBefore"))

        database = db.get_db()
        database.execute(
            """INSERT INTO sessions (id, user_id, language, engine, transcript,
                                     state, created_at, updated_at, confidence_before)
               VALUES (?, ?, ?, ?, ?, 'open', ?, ?, ?)""",
            (session_id, user["id"] if user is not None else None, lang, engine,
             json.dumps(transcript), now, now, confidence_before),
        )
        database.commit()

        return jsonify({
            "sessionId": session_id,
            "question": first["question"],
            "done": False,
            "turn": 1,
            "minTurns": interview.MIN_TURNS,
            "maxTurns": interview.MAX_TURNS,
            "engine": engine,
        })

    @app.post("/api/interview/reply")
    def interview_reply():
        body = json_body()
        session_id = str(body.get("sessionId") or "")[:64]
        answer = str(body.get("answer") or "").strip()[:MAX_ANSWER_CHARS]

        if not answer:
            return jsonify({"error": "Type an answer first."}), 400

        database = db.get_db()
        row = database.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            return jsonify({"error": "That interview session has expired. Start again."}), 404
        if row["state"] != "open":
            return jsonify({"error": "This interview is already finished."}), 409

        lang = row["language"]
        transcript = json.loads(row["transcript"])
        transcript.append({"role": "student", "text": answer})

        if len(transcript) > MAX_TRANSCRIPT_TURNS:
            nxt = {"question": "", "done": True, "engine": "fallback"}
        else:
            nxt = interview.next_question(transcript, lang)

        if not nxt["done"]:
            entry = {"role": "ai", "text": nxt["question"]}
            if nxt.get("qid"):
                entry["qid"] = nxt["qid"]
            transcript.append(entry)

        database.execute(
            "UPDATE sessions SET transcript = ?, engine = ?, updated_at = ? WHERE id = ?",
            (json.dumps(transcript), nxt.get("engine", row["engine"]),
             datetime.now(timezone.utc).isoformat(), session_id),
        )
        database.commit()

        return jsonify({
            "sessionId": session_id,
            "question": nxt["question"],
            "done": nxt["done"],
            "turn": sum(1 for t in transcript if t["role"] == "student"),
            "engine": nxt.get("engine", row["engine"]),
        })

    @app.post("/api/interview/finish")
    def interview_finish():
        body = json_body()
        session_id = str(body.get("sessionId") or "")[:64]

        database = db.get_db()
        row = database.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            return jsonify({"error": "That interview session has expired. Start again."}), 404

        transcript = json.loads(row["transcript"])
        if not any(t["role"] == "student" for t in transcript):
            return jsonify({"error": "Answer at least one question first."}), 400

        lang = clean_lang(body.get("language") or row["language"])
        user = auth.current_user(required=False)

        academics = clean_academics(body.get("academics"))
        if academics is None and user is not None and user["academics"]:
            academics = json.loads(user["academics"])

        payload, vectors, top_df = score_interview(transcript, academics, lang, user)
        save_submission(payload, vectors, top_df, transcript, academics, lang,
                        user, session_id)

        database.execute("UPDATE sessions SET state = 'done', updated_at = ? WHERE id = ?",
                         (datetime.now(timezone.utc).isoformat(), session_id))
        database.commit()

        payload["sessionId"] = session_id
        payload["saved"] = user is not None
        return jsonify(payload)

    # ------------------------------------------------- one-shot compatibility --

    @app.post("/api/match")
    def match():
        """
        Score a conversation in one call, without the turn-by-turn session.
        Used by the offline demo path and by tests.
        """
        body = json_body()
        lang = clean_lang(body.get("language"))
        transcript = clean_transcript(body.get("transcript"))

        if not transcript:
            # Accept the old structured payload too, so nothing that already
            # points at this endpoint breaks.
            parts = []
            for key in ("subjects", "activities"):
                values = body.get(key)
                if isinstance(values, list):
                    parts.extend(str(v) for v in values[:20])
            for key in ("workstyle", "goal"):
                if body.get(key):
                    parts.append(str(body[key]))
            if parts:
                transcript = [{"role": "student", "text": ". ".join(parts)[:MAX_ANSWER_CHARS]}]

        if not transcript:
            return jsonify({"error": "Send a transcript of the interview."}), 400

        user = auth.current_user(required=False)
        academics = clean_academics(body.get("academics"))
        if academics is None and user is not None and user["academics"]:
            academics = json.loads(user["academics"])

        payload, vectors, top_df = score_interview(transcript, academics, lang, user)
        save_submission(payload, vectors, top_df, transcript, academics, lang, user, None)
        payload["saved"] = user is not None
        return jsonify(payload)

    @app.get("/api/me/history")
    @auth.login_required("student")
    def history():
        rows = db.get_db().execute(
            """SELECT created_at, top_career, top_fit, engine, language
               FROM submissions WHERE user_id = ?
               ORDER BY created_at DESC LIMIT 20""",
            (g.user["id"],),
        ).fetchall()
        return jsonify([{
            "createdAt": r["created_at"],
            "topCareer": r["top_career"],
            "fit": round(r["top_fit"] * 100),
            "engine": r["engine"],
            "language": r["language"],
        } for r in rows])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=config.DEBUG, port=config.PORT)
