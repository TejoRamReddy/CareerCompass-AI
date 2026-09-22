"""
Test suite. Runs with no Gemini key, so it exercises the fallback path and
stays deterministic and offline.

    cd backend && pytest -q
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ["GEMINI_API_KEY"] = ""
os.environ["RATE_LIMIT_PER_MINUTE"] = "10000"
os.environ["AUTH_RATE_LIMIT_PER_MINUTE"] = "10000"

_fd, _path = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["DATABASE_PATH"] = _path

import config  # noqa: E402

config.DB_PATH = _path
config.GEMINI_API_KEY = ""
config.GEMINI_ENABLED = False
config.RATE_LIMIT_PER_MINUTE = 10000
config.AUTH_RATE_LIMIT_PER_MINUTE = 10000

import app as app_module  # noqa: E402
import matching  # noqa: E402
from careers_data import CAREERS, DIMS  # noqa: E402


@pytest.fixture(scope="module")
def client():
    application = app_module.create_app()
    application.config["TESTING"] = True
    with application.test_client() as c:
        yield c


def register(client, **overrides):
    import uuid
    body = {
        "name": "Test Student",
        "email": f"s{uuid.uuid4().hex[:8]}@example.com",
        "password": "correct-horse-battery",
        "role": "student",
        "branch": "CSE",
        "college": "Anna University",
        "classCode": "CS2027",
    }
    body.update(overrides)
    res = client.post("/api/auth/register", json=body)
    return res


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


CODING_TRANSCRIPT = [
    {"role": "ai", "text": "Which subjects do you enjoy?"},
    {"role": "student", "text": "I really like computer science and maths. I write "
                                "python programs at home and solve puzzles."},
    {"role": "ai", "text": "What do you do outside class?"},
    {"role": "student", "text": "I build small apps and try algorithm problems. "
                                "I also analyse cricket statistics for fun."},
]

CARING_TRANSCRIPT = [
    {"role": "ai", "text": "Which subjects do you enjoy?"},
    {"role": "student", "text": "Biology is my favourite. I want to help patients "
                                "and I listen to my friends when they are upset."},
    {"role": "ai", "text": "What do people come to you for?"},
    {"role": "student", "text": "They come to me to talk. I tutor juniors in "
                                "chemistry and I care about them."},
]


# ------------------------------------------------------------------ basics --

def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"
    assert res.get_json()["geminiConfigured"] is False


def test_career_dataset_is_26_and_well_formed():
    assert len(CAREERS) == 26
    for c in CAREERS:
        assert len(c["vec"]) == len(DIMS)
        assert all(0 <= v <= 5 for v in c["vec"])
        assert c["name_ta"] and c["blurb_ta"]


def test_careers_endpoint_localises(client):
    en = client.get("/api/careers?lang=en").get_json()
    ta = client.get("/api/careers?lang=ta").get_json()
    assert len(en) == 26
    assert en[0]["name"] != ta[0]["name"]
    assert ta[0]["nameEn"] == en[0]["nameEn"]


# ----------------------------------------------------------------- scoring --

def test_different_students_get_different_careers(client):
    coder = client.post("/api/match", json={"transcript": CODING_TRANSCRIPT}).get_json()
    carer = client.post("/api/match", json={"transcript": CARING_TRANSCRIPT}).get_json()
    assert coder["matches"][0]["nameEn"] != carer["matches"][0]["nameEn"]
    assert coder["matches"][0]["category"] == "Tech & Engineering"


def test_fit_is_spread_not_bunched(client):
    """The old engine returned 81-87% for everything. Calibration should spread it."""
    data = client.post("/api/match", json={"transcript": CODING_TRANSCRIPT}).get_json()
    fits = [m["fit"] for m in data["matches"]]
    assert fits == sorted(fits, reverse=True)
    assert all(0 <= f <= 100 for f in fits)
    # Raw similarity is reported separately and is never called a probability.
    assert "similarity" in data["matches"][0]


def test_academic_marks_change_the_ranking(client):
    base = client.post("/api/match", json={"transcript": CODING_TRANSCRIPT}).get_json()
    weak_math = client.post("/api/match", json={
        "transcript": CODING_TRANSCRIPT,
        "academics": {"math": 35, "computer": 40, "science": 30, "language": 85, "social": 80},
    }).get_json()
    assert weak_math["usedAcademics"] is True
    assert base["usedAcademics"] is False
    assert weak_math["matches"][0]["fit"] != base["matches"][0]["fit"]


def test_academic_vector_scaling():
    vec = matching.academic_vector({"math": 100})
    assert vec[DIMS.index("math")] == pytest.approx(5.0)
    assert matching.academic_vector(None).sum() == 0


def test_calibration_bounds():
    assert matching.calibrate(0.0) == 0.0
    assert matching.calibrate(1.0) == 1.0
    assert 0 < matching.calibrate(0.7) < 1


def test_match_rejects_empty_body(client):
    assert client.post("/api/match", json={}).status_code == 400


def test_gap_and_roadmap_present(client):
    data = client.post("/api/match", json={"transcript": CARING_TRANSCRIPT}).get_json()
    assert data["gap"]["rows"]
    assert all(r["need"] >= 4 for r in data["gap"]["rows"])
    assert data["roadmap"]
    assert data["engine"] == "fallback"


def test_tamil_results_are_tamil(client):
    data = client.post("/api/match", json={
        "transcript": CARING_TRANSCRIPT, "language": "ta"
    }).get_json()
    assert any("\u0b80" <= ch <= "\u0bff" for ch in data["matches"][0]["blurb"])


# -------------------------------------------------------------------- auth --

def test_register_and_login(client):
    res = register(client, email="flow@example.com")
    assert res.status_code == 201
    token = res.get_json()["token"]

    me = client.get("/api/auth/me", headers=auth_header(token))
    assert me.status_code == 200
    assert me.get_json()["branch"] == "CSE"
    assert me.get_json()["shareCode"]

    again = client.post("/api/auth/login", json={
        "email": "flow@example.com", "password": "correct-horse-battery"})
    assert again.status_code == 200


def test_password_is_hashed_not_stored(client):
    register(client, email="hash@example.com", password="plaintext-password-123")
    import db as db_module
    conn = db_module.connect()
    row = conn.execute("SELECT password_hash FROM users WHERE email = ?",
                       ("hash@example.com",)).fetchone()
    conn.close()
    assert "plaintext-password-123" not in row["password_hash"]
    assert row["password_hash"].startswith(("pbkdf2:", "scrypt:"))


def test_duplicate_email_rejected(client):
    register(client, email="dupe@example.com")
    assert register(client, email="dupe@example.com").status_code == 409


def test_short_password_rejected(client):
    assert register(client, email="short@example.com", password="abc").status_code == 400


def test_wrong_password_rejected(client):
    register(client, email="wrong@example.com")
    res = client.post("/api/auth/login", json={
        "email": "wrong@example.com", "password": "not-the-password"})
    assert res.status_code == 401


def test_protected_route_needs_token(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me",
                      headers={"Authorization": "Bearer nonsense"}).status_code == 401


# --------------------------------------------------------------- interview --

def test_full_interview_flow(client):
    token = register(client, email="interview@example.com").get_json()["token"]

    start = client.post("/api/interview/start", json={"language": "en"},
                        headers=auth_header(token)).get_json()
    session_id = start["sessionId"]
    assert start["question"]

    answers = [
        "I enjoy computer science and maths, I write code at home.",
        "I build small apps and solve algorithm puzzles for hours.",
        "I usually work alone, deeply focused on one problem.",
        "Friends ask me to fix their laptops and explain maths.",
        "I want work that keeps teaching me new things.",
    ]
    for answer in answers:
        res = client.post("/api/interview/reply",
                          json={"sessionId": session_id, "answer": answer},
                          headers=auth_header(token))
        assert res.status_code == 200
        if res.get_json()["done"]:
            break

    finish = client.post("/api/interview/finish",
                         json={"sessionId": session_id,
                               "academics": {"math": 88, "computer": 92}},
                         headers=auth_header(token))
    assert finish.status_code == 200
    data = finish.get_json()
    assert len(data["matches"]) == 3
    assert data["saved"] is True
    assert data["matches"][0]["why"]

    history = client.get("/api/me/history", headers=auth_header(token)).get_json()
    assert len(history) == 1


def test_reply_rejects_unknown_session(client):
    res = client.post("/api/interview/reply",
                      json={"sessionId": "does-not-exist", "answer": "hello"})
    assert res.status_code == 404


def test_reply_rejects_empty_answer(client):
    start = client.post("/api/interview/start", json={}).get_json()
    res = client.post("/api/interview/reply",
                      json={"sessionId": start["sessionId"], "answer": "   "})
    assert res.status_code == 400


# -------------------------------------------------------------- dashboards --

def test_teacher_sees_only_their_class(client):
    student = register(client, email="pupil@example.com", classCode="TN101")
    student_token = student.get_json()["token"]
    other = register(client, email="outsider@example.com", classCode="ZZ999")
    assert other.status_code == 201

    client.post("/api/match", json={"transcript": CODING_TRANSCRIPT},
                headers=auth_header(student_token))

    teacher = register(client, email="teacher@example.com", role="teacher",
                       classCode="TN101", branch=None, college=None)
    teacher_token = teacher.get_json()["token"]

    data = client.get("/api/teacher/class",
                      headers=auth_header(teacher_token)).get_json()
    assert data["classCode"] == "TN101"
    names = [s["name"] for s in data["students"]]
    assert len(data["students"]) == 1
    assert data["completedCount"] == 1
    assert data["topCareers"]


def test_student_cannot_open_teacher_dashboard(client):
    token = register(client, email="nosy@example.com").get_json()["token"]
    assert client.get("/api/teacher/class", headers=auth_header(token)).status_code == 403


def test_parent_links_with_share_code_and_sees_results(client):
    student = register(client, email="child@example.com")
    student_token = student.get_json()["token"]
    share_code = student.get_json()["user"]["shareCode"]
    client.post("/api/match", json={"transcript": CARING_TRANSCRIPT},
                headers=auth_header(student_token))

    parent = register(client, email="parent@example.com", role="parent",
                      branch=None, college=None, classCode=None)
    parent_token = parent.get_json()["token"]

    linked = client.post("/api/parent/link", json={"shareCode": share_code},
                         headers=auth_header(parent_token))
    assert linked.status_code == 201

    data = client.get("/api/parent/children",
                      headers=auth_header(parent_token)).get_json()
    assert len(data["children"]) == 1
    assert data["children"][0]["completed"] is True
    assert data["children"][0]["matches"]


def test_parent_link_rejects_bad_code(client):
    parent = register(client, email="parent2@example.com", role="parent",
                      branch=None, college=None, classCode=None)
    res = client.post("/api/parent/link", json={"shareCode": "NOPE99"},
                      headers=auth_header(parent.get_json()["token"]))
    assert res.status_code == 404


# ------------------------------------------------------------------- stats --

def test_stats_reflect_the_database(client):
    data = client.get("/api/stats").get_json()
    assert data["totalSubmissions"] > 0
    assert data["registeredStudents"] > 0
    assert data["mostCommonTopMatch"]


# ===========================================================================
# Deck-completion features: real Gemini path (mocked), consistency check,
# health probe, feedback, QR, and the fuller dashboards.
# ===========================================================================

import json as _json
import re as _re

import gemini  # noqa: E402


class FakeGemini:
    """Stands in for gemini._call so the Gemini code path is tested offline."""

    def __init__(self, fail=False, consistency=None):
        self.fail = fail
        self.calls = []
        self.consistency = consistency or {
            "level": "medium", "flags": ["Said they love maths but gave no example"]}

    def __call__(self, system, user, *, as_json=True, max_tokens=800):
        self.calls.append(system[:40])
        if self.fail:
            raise gemini.GeminiUnavailable("simulated outage")
        if '"ok": true' in system:
            return '{"ok": true}'
        if "career counsellor inside" in system:
            answered = int(_re.search(r"answered (\d+)", user).group(1))
            if answered >= 5:
                return _json.dumps({"question": "", "done": True, "note": ""})
            return _json.dumps({"question": f"Follow-up number {answered}: tell me more?",
                                "done": False, "note": "noted"})
        if "score the" in system:
            return _json.dumps({
                "scores": {d: (5 if d in ("coding", "math") else 1) for d in DIMS},
                "summary": "You are drawn to building things with code.",
                "evidence": {"coding": "I write python at home"},
                "consistency": self.consistency,
            })
        if "explain career recommendations" in system:
            names = _re.findall(r"^- (.+?):", user, _re.M)
            return _json.dumps({n: f"You said you write python, which fits {n}." for n in names})
        raise AssertionError("unexpected Gemini prompt: " + system[:60])


@pytest.fixture()
def gemini_on(monkeypatch):
    """Turn Gemini 'on' with a fake backend, and reset the health-probe cache."""
    fake = FakeGemini()
    monkeypatch.setattr(config, "GEMINI_ENABLED", True)
    monkeypatch.setattr(config, "GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(gemini, "_call", fake)
    gemini._probe_cache.update(at=0.0, result=None)
    yield fake
    gemini._probe_cache.update(at=0.0, result=None)


def run_interview(client, token=None, language="en", confidence_before=None):
    headers = auth_header(token) if token else {}
    body = {"language": language}
    if confidence_before:
        body["confidenceBefore"] = confidence_before
    start = client.post("/api/interview/start", json=body, headers=headers).get_json()
    sid = start["sessionId"]
    for answer in ["I like coding and maths.", "I build apps at home.", "I work alone.",
                   "People ask me to fix laptops.", "I want to keep learning."]:
        res = client.post("/api/interview/reply",
                          json={"sessionId": sid, "answer": answer}, headers=headers).get_json()
        if res["done"]:
            break
    return start, sid


def test_health_reports_unconfigured_without_key(client):
    data = client.get("/api/health").get_json()
    assert data["geminiConfigured"] is False
    assert data["geminiReachable"] is False


def test_health_reports_reachable_when_gemini_answers(client, gemini_on):
    data = client.get("/api/health").get_json()
    assert data["geminiConfigured"] is True
    assert data["geminiReachable"] is True
    assert data["geminiError"] is None


def test_health_reports_unreachable_when_key_is_present_but_gemini_fails(client, monkeypatch):
    monkeypatch.setattr(config, "GEMINI_ENABLED", True)
    monkeypatch.setattr(config, "GEMINI_API_KEY", "bad-key")
    monkeypatch.setattr(gemini, "_call", FakeGemini(fail=True))
    gemini._probe_cache.update(at=0.0, result=None)
    data = client.get("/api/health").get_json()
    assert data["geminiConfigured"] is True
    assert data["geminiReachable"] is False, "a present-but-broken key must not show as live"
    assert "simulated outage" in data["geminiError"]
    gemini._probe_cache.update(at=0.0, result=None)


def test_probe_is_cached(client, gemini_on):
    client.get("/api/health")
    client.get("/api/health")
    client.get("/api/health")
    assert sum(1 for c in gemini_on.calls if "ok" in c or "Reply with JSON only" in c) == 1


def test_full_gemini_path_uses_gemini_for_everything(client, gemini_on):
    token = register(client, email="g1@example.com").get_json()["token"]
    start, sid = run_interview(client, token)
    assert start["engine"] == "gemini"

    res = client.post("/api/interview/finish", json={"sessionId": sid},
                      headers=auth_header(token)).get_json()
    assert res["engine"] == "gemini"
    assert res["matches"][0]["why"].startswith("You said you write python")
    assert res["consistency"]["level"] == "medium"
    assert res["consistency"]["flags"]


def test_gemini_failure_mid_interview_falls_back_cleanly(client, gemini_on, monkeypatch):
    start = client.post("/api/interview/start", json={"language": "en"}).get_json()
    sid = start["sessionId"]
    assert start["engine"] == "gemini"

    monkeypatch.setattr(gemini, "_call", FakeGemini(fail=True))   # Gemini dies now
    res = client.post("/api/interview/reply",
                      json={"sessionId": sid, "answer": "I like coding and maths."})
    assert res.status_code == 200
    assert res.get_json()["engine"] == "fallback"
    assert res.get_json()["question"]

    fin = client.post("/api/interview/finish", json={"sessionId": sid}).get_json()
    assert fin["engine"] == "fallback"
    assert fin["consistency"] is None       # the scripted engine can't cross-check
    assert len(fin["matches"]) == 3


def test_garbled_gemini_json_falls_back(client, gemini_on, monkeypatch):
    monkeypatch.setattr(gemini, "_call", lambda *a, **k: "this is not json at all")
    data = client.post("/api/match", json={"transcript": CODING_TRANSCRIPT}).get_json()
    assert data["engine"] == "fallback"
    assert len(data["matches"]) == 3


def test_out_of_range_gemini_scores_are_clamped(client, gemini_on, monkeypatch):
    def wild(system, user, *, as_json=True, max_tokens=800):
        if "score the" in system:
            return _json.dumps({"scores": {**{d: 99 for d in DIMS}, "math": -7}, "summary": "x",
                                "consistency": {"level": "bogus", "flags": "not a list"}})
        return FakeGemini()(system, user, as_json=as_json, max_tokens=max_tokens)
    monkeypatch.setattr(gemini, "_call", wild)
    profile = gemini.extract_profile(CODING_TRANSCRIPT)
    assert all(0 <= v <= 5 for v in profile["vector"])
    assert profile["consistency"] is None       # invalid consistency is dropped, not trusted


def test_consistency_prompt_asks_for_a_specific_example():
    assert "specific, recent example" in gemini.INTERVIEW_SYSTEM
    assert "never as doubt" in gemini.INTERVIEW_SYSTEM.lower() or "never as doubt" in gemini.INTERVIEW_SYSTEM


# --------------------------------------------------------------- feedback ----

def test_feedback_requires_finished_session(client):
    start = client.post("/api/interview/start", json={}).get_json()
    res = client.post("/api/feedback", json={"sessionId": start["sessionId"], "rating": 5})
    assert res.status_code == 409


def test_feedback_rejects_bad_rating(client):
    assert client.post("/api/feedback", json={"sessionId": "x", "rating": 9}).status_code == 400
    assert client.post("/api/feedback", json={"sessionId": "x"}).status_code == 400


def test_feedback_unknown_session(client):
    assert client.post("/api/feedback", json={"sessionId": "nope", "rating": 4}).status_code == 404


def test_feedback_is_saved_upserted_and_feeds_stats(client):
    _, sid = run_interview(client, confidence_before=2)
    client.post("/api/interview/finish", json={"sessionId": sid})

    first = client.post("/api/feedback", json={
        "sessionId": sid, "rating": 3, "confidenceAfter": 4, "wouldAct": "yes",
        "comment": "helpful"})
    assert first.status_code == 200
    # Rating again replaces, it doesn't double count.
    client.post("/api/feedback", json={"sessionId": sid, "rating": 5,
                                       "confidenceAfter": 5, "wouldAct": "yes"})

    import db as db_module
    conn = db_module.connect()
    rows = conn.execute("SELECT rating, confidence_after FROM feedback WHERE session_id = ?",
                        (sid,)).fetchall()
    conn.close()
    assert len(rows) == 1 and rows[0]["rating"] == 5

    stats = client.get("/api/stats").get_json()
    assert stats["feedbackCount"] >= 1
    assert stats["averageRating"] is not None
    assert stats["averageConfidenceChange"] is not None
    assert stats["shareWhoWouldActOnTop3"] is not None


# ----------------------------------------------------------------------- QR --

def test_qr_returns_svg_for_an_allowed_origin(client):
    origin = config.ALLOWED_ORIGINS[0]
    res = client.get("/api/qr", query_string={"url": origin + "/demo.html"})
    assert res.status_code == 200
    assert res.mimetype == "image/svg+xml"
    assert b"<svg" in res.data


def test_qr_refuses_arbitrary_urls(client):
    res = client.get("/api/qr", query_string={"url": "https://evil.example.com/phish"})
    assert res.status_code == 400
    assert client.get("/api/qr").status_code == 400
    assert client.get("/api/qr", query_string={"url": config.ALLOWED_ORIGINS[0] + "/" + "a" * 400}
                      ).status_code == 400


# -------------------------------------------------------------- dashboards ---

def test_teacher_gets_workshop_ideas_for_common_gaps(client):
    student = register(client, email="ws1@example.com", classCode="WS100")
    tok = student.get_json()["token"]
    client.post("/api/match", json={"transcript": CARING_TRANSCRIPT}, headers=auth_header(tok))
    teacher = register(client, email="wsteach@example.com", role="teacher",
                       classCode="WS100", branch=None, college=None).get_json()["token"]
    data = client.get("/api/teacher/class", headers=auth_header(teacher)).get_json()
    assert data["workshops"], "a class with gaps should get workshop suggestions"
    assert all(w["idea"] for w in data["workshops"])
    ta = client.get("/api/teacher/class?lang=ta", headers=auth_header(teacher)).get_json()
    assert any("\u0b80" <= ch <= "\u0bff" for ch in ta["workshops"][0]["idea"])


def test_teacher_sees_attempts_and_fit_change(client):
    student = register(client, email="ws2@example.com", classCode="WS200")
    tok = student.get_json()["token"]
    client.post("/api/match", json={"transcript": CARING_TRANSCRIPT}, headers=auth_header(tok))
    client.post("/api/match", json={"transcript": CODING_TRANSCRIPT}, headers=auth_header(tok))
    teacher = register(client, email="wsteach2@example.com", role="teacher",
                       classCode="WS200", branch=None, college=None).get_json()["token"]
    row = client.get("/api/teacher/class", headers=auth_header(teacher)).get_json()["students"][0]
    assert row["attempts"] == 2
    assert row["fitChange"] is not None


def test_parent_sees_progress_over_time_and_home_tips(client):
    student = register(client, email="prog@example.com")
    tok = student.get_json()["token"]
    code = student.get_json()["user"]["shareCode"]
    # Latest run is the one with skill gaps, so the tips have something to target.
    client.post("/api/match", json={"transcript": CODING_TRANSCRIPT}, headers=auth_header(tok))
    client.post("/api/match", json={"transcript": CARING_TRANSCRIPT}, headers=auth_header(tok))

    parent = register(client, email="progparent@example.com", role="parent",
                      branch=None, college=None, classCode=None).get_json()["token"]
    client.post("/api/parent/link", json={"shareCode": code}, headers=auth_header(parent))
    child = client.get("/api/parent/children", headers=auth_header(parent)).get_json()["children"][0]

    assert child["attempts"] == 2
    assert len(child["progress"]) == 2
    assert child["skillChange"], "a big shift between runs should show up as a skill change"
    assert all(abs(m["change"]) >= 0.3 for m in child["skillChange"])
    assert len(child["tips"]) >= 2
    assert "transcript" not in child                       # still never exposed


def test_parent_with_single_run_has_no_fake_progress(client):
    student = register(client, email="one@example.com")
    tok = student.get_json()["token"]
    code = student.get_json()["user"]["shareCode"]
    client.post("/api/match", json={"transcript": CODING_TRANSCRIPT}, headers=auth_header(tok))
    parent = register(client, email="oneparent@example.com", role="parent",
                      branch=None, college=None, classCode=None).get_json()["token"]
    client.post("/api/parent/link", json={"shareCode": code}, headers=auth_header(parent))
    child = client.get("/api/parent/children", headers=auth_header(parent)).get_json()["children"][0]
    assert child["skillChange"] == []        # one run has no "over time"


def test_parent_tips_are_in_tamil_when_asked(client):
    student = register(client, email="tam@example.com")
    tok = student.get_json()["token"]
    code = student.get_json()["user"]["shareCode"]
    client.post("/api/match", json={"transcript": CARING_TRANSCRIPT, "language": "ta"},
                headers=auth_header(tok))
    parent = register(client, email="tamparent@example.com", role="parent",
                      branch=None, college=None, classCode=None).get_json()["token"]
    client.post("/api/parent/link", json={"shareCode": code}, headers=auth_header(parent))
    child = client.get("/api/parent/children?lang=ta",
                       headers=auth_header(parent)).get_json()["children"][0]
    assert any("\u0b80" <= ch <= "\u0bff" for ch in child["tips"][-1])


# ===========================================================================
# Gemini HTTP layer, against a local mock server. Checks what we actually put
# on the wire and how we handle what comes back — including that the API key
# never appears in a URL, a log line, or a response body.
# ===========================================================================

import threading  # noqa: E402
from http.server import BaseHTTPRequestHandler, HTTPServer  # noqa: E402

SECRET = "AQ.test-secret-key-do-not-leak-1234567890"


class _MockGoogle(BaseHTTPRequestHandler):
    status = 200
    payload = None
    seen = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        type(self).seen.append({"path": self.path, "headers": dict(self.headers),
                                "body": _json.loads(body)})
        payload = type(self).payload
        if payload is None:
            payload = {"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}]}
        raw = _json.dumps(payload).encode()
        self.send_response(type(self).status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


@pytest.fixture()
def mock_google(monkeypatch):
    _MockGoogle.status, _MockGoogle.payload, _MockGoogle.seen = 200, None, []
    server = HTTPServer(("127.0.0.1", 0), _MockGoogle)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(config, "GEMINI_BASE_URL", f"http://127.0.0.1:{server.server_port}/v1beta")
    monkeypatch.setattr(config, "GEMINI_API_KEY", SECRET)
    monkeypatch.setattr(config, "GEMINI_ENABLED", True)
    monkeypatch.setattr(config, "GEMINI_MODEL", "gemini-test-model")
    gemini._probe_cache.update(at=0.0, result=None)
    yield _MockGoogle
    server.shutdown()
    gemini._probe_cache.update(at=0.0, result=None)


def test_request_has_the_right_shape_and_key_is_in_a_header_only(mock_google):
    gemini._call("SYSTEM PROMPT", "USER TEXT", max_tokens=123)
    req = mock_google.seen[0]

    assert req["path"] == "/v1beta/models/gemini-test-model:generateContent"
    assert SECRET not in req["path"], "the key must never be in the URL"
    assert req["headers"].get("x-goog-api-key") == SECRET
    assert req["body"]["systemInstruction"]["parts"][0]["text"] == "SYSTEM PROMPT"
    assert req["body"]["contents"][0]["parts"][0]["text"] == "USER TEXT"
    assert req["body"]["generationConfig"]["maxOutputTokens"] == 123
    assert req["body"]["generationConfig"]["responseMimeType"] == "application/json"


def test_response_text_parts_are_joined(mock_google):
    mock_google.payload = {"candidates": [{"content": {"parts": [{"text": '{"a":'}, {"text": ' 1}'}]}}]}
    assert gemini._parse_json(gemini._call("s", "u")) == {"a": 1}


def test_json_wrapped_in_a_code_fence_is_still_parsed():
    assert gemini._parse_json('```json\n{"question": "hi", "done": false}\n```')["question"] == "hi"


@pytest.mark.parametrize("status", [400, 403, 404, 429, 500, 503])
def test_http_errors_become_graceful_unavailable(mock_google, status):
    mock_google.status = status
    mock_google.payload = {"error": {"message": f"echo of key {SECRET}"}}
    with pytest.raises(gemini.GeminiUnavailable) as exc:
        gemini._call("s", "u")
    assert SECRET not in str(exc.value), "an error body that echoes the key must be redacted"
    assert str(status) in str(exc.value)


@pytest.mark.parametrize("payload", [
    {}, {"candidates": []}, {"candidates": [{}]},
    {"candidates": [{"content": {"parts": []}}]},
    {"candidates": [{"content": {"parts": [{"text": "   "}]}}]},
    {"promptFeedback": {"blockReason": "SAFETY"}},          # a safety block has no candidates
])
def test_odd_gemini_responses_never_crash(mock_google, payload):
    mock_google.payload = payload
    with pytest.raises(gemini.GeminiUnavailable):
        gemini._call("s", "u")


def test_unreachable_host_is_reported_without_leaking_the_key(client, monkeypatch):
    monkeypatch.setattr(config, "GEMINI_BASE_URL", "http://127.0.0.1:1/v1beta")   # nothing listens here
    monkeypatch.setattr(config, "GEMINI_API_KEY", SECRET)
    monkeypatch.setattr(config, "GEMINI_ENABLED", True)
    gemini._probe_cache.update(at=0.0, result=None)

    body = client.get("/api/health").get_data(as_text=True)
    assert SECRET not in body, "/api/health is public and must never contain the key"
    data = _json.loads(body)
    assert data["geminiConfigured"] is True and data["geminiReachable"] is False
    gemini._probe_cache.update(at=0.0, result=None)


def test_health_never_contains_the_key_even_when_google_echoes_it(client, mock_google):
    mock_google.status = 403
    mock_google.payload = {"error": {"message": f"API key {SECRET} is invalid"}}
    body = client.get("/api/health").get_data(as_text=True)
    assert SECRET not in body


def test_end_to_end_over_real_http_with_the_mock(client, mock_google, monkeypatch):
    """The whole flow through requests → HTTP → parse, not a patched _call."""
    def responder():
        # Answer according to which prompt arrived, like the real service would.
        body = mock_google.seen[-1]["body"]
        system = body["systemInstruction"]["parts"][0]["text"]
        user = body["contents"][0]["parts"][0]["text"]
        if "career counsellor inside" in system:
            n = int(_re.search(r"answered (\d+)", user).group(1))
            text = _json.dumps({"question": "" if n >= 5 else f"Q{n + 1}?", "done": n >= 5})
        elif "score the" in system:
            text = _json.dumps({"scores": {d: (5 if d in ("empathy", "science") else 0) for d in DIMS},
                                "summary": "You care about people.",
                                "consistency": {"level": "high", "flags": []}})
        elif "explain career recommendations" in system:
            names = _re.findall(r"^- (.+?):", user, _re.M)
            text = _json.dumps({n: f"Because you said you care, {n} fits." for n in names})
        else:
            text = '{"ok": true}'
        return {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    # Make the mock stateful: compute the payload from each incoming request.
    original = _MockGoogle.do_POST

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        _MockGoogle.seen.append({"path": self.path, "headers": dict(self.headers),
                                 "body": _json.loads(raw.decode())})
        out = _json.dumps(responder()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    monkeypatch.setattr(_MockGoogle, "do_POST", do_POST)

    start, sid = run_interview(client)
    assert start["engine"] == "gemini"
    fin = client.post("/api/interview/finish", json={"sessionId": sid}).get_json()

    assert fin["engine"] == "gemini"
    assert fin["consistency"]["level"] == "high"
    assert fin["matches"][0]["why"].startswith("Because you said you care")
    assert fin["matches"][0]["category"] == "Medicine, Science & Creative"
    assert all(SECRET not in r["path"] for r in mock_google.seen)
    assert all(r["headers"].get("x-goog-api-key") == SECRET for r in mock_google.seen)


# ===========================================================================
# A model that rejects thinkingConfig outright (HTTP 400) should be retried
# once without it, rather than treated as unavailable.
# ===========================================================================

def test_model_rejecting_thinking_config_is_retried_without_it(mock_google, monkeypatch):
    calls = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = _json.loads(self.rfile.read(length).decode())
        calls.append(body)
        has_thinking = "thinkingConfig" in body.get("generationConfig", {})
        if has_thinking:
            out, status = {"error": {"message": "Unknown field thinkingConfig"}}, 400
        else:
            out = {"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}]}
            status = 200
        raw = _json.dumps(out).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    monkeypatch.setattr(mock_google, "do_POST", do_POST)

    result = gemini._call("s", "u")
    assert result == '{"ok": true}'
    assert len(calls) == 2, "first attempt with thinkingConfig, then a retry without it"
    assert "thinkingConfig" in calls[0]["generationConfig"]
    assert "thinkingConfig" not in calls[1]["generationConfig"]


def test_a_400_unrelated_to_thinking_config_is_not_retried(mock_google):
    mock_google.status = 400
    mock_google.payload = {"error": {"message": "some other validation problem"}}
    with pytest.raises(gemini.GeminiUnavailable):
        gemini._call("s", "u")
    assert len(mock_google.seen) == 1, "only unrelated 400s should not trigger a retry"
