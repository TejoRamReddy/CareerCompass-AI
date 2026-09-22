"""
Teacher and parent views.

Both are deliberately narrow. A teacher sees the shape of their class, not a
transcript of what a student said in confidence. A parent sees one child's
results, and only after the child gives them a share code.
"""

import json
from collections import Counter
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

import auth
from careers_data import (DIM_LABELS, DIM_LABELS_TA, DIMS, PARENT_GENERAL_TIP,
                          PARENT_TIPS, WORKSHOPS)
from db import get_db

bp = Blueprint("dashboards", __name__)


def _latest_result(student_id):
    row = get_db().execute(
        """SELECT created_at, top_career, top_fit, engine, result
           FROM submissions WHERE user_id = ?
           ORDER BY created_at DESC LIMIT 1""",
        (student_id,),
    ).fetchone()
    return row


def _lang():
    return "ta" if request.args.get("lang") == "ta" else "en"


def _all_runs(student_id):
    """Every completed interview for a student, oldest first."""
    return get_db().execute(
        """SELECT created_at, top_career, top_fit, combined_vector
           FROM submissions WHERE user_id = ? ORDER BY created_at ASC""",
        (student_id,),
    ).fetchall()


def _skill_change(runs, lang, limit=3):
    """
    How the profile moved between a student's first and latest interview.
    Returns the skills that moved most, e.g. [{"label": "Coding", "change": +1.2}].
    Needs at least two runs; a single run has no 'over time' to show.
    """
    if len(runs) < 2:
        return []
    labels = DIM_LABELS_TA if lang == "ta" else DIM_LABELS
    first = json.loads(runs[0]["combined_vector"])
    last = json.loads(runs[-1]["combined_vector"])
    moves = []
    for i, dim in enumerate(DIMS):
        delta = round(float(last[i]) - float(first[i]), 1)
        if abs(delta) >= 0.3:
            moves.append({"dim": dim, "label": labels[dim], "change": delta})
    moves.sort(key=lambda m: -abs(m["change"]))
    return moves[:limit]


# ------------------------------------------------------------------ teacher --

@bp.get("/api/teacher/class")
@auth.login_required("teacher")
def teacher_class():
    """Aggregate view of every student who signed up with this class code."""
    database = get_db()
    class_code = g.user["class_code"]
    lang = "ta" if request.args.get("lang") == "ta" else "en"
    labels = DIM_LABELS_TA if lang == "ta" else DIM_LABELS

    students = database.execute(
        "SELECT id, name, branch, college FROM users "
        "WHERE role = 'student' AND class_code = ? ORDER BY name",
        (class_code,),
    ).fetchall()

    rows, career_counts, gap_counts = [], Counter(), Counter()

    for s in students:
        latest = _latest_result(s["id"])
        runs = _all_runs(s["id"])
        entry = {
            "id": s["id"],
            "name": s["name"],
            "branch": s["branch"],
            "completed": latest is not None,
            "attempts": len(runs),
            "topCareer": None,
            "fit": None,
            "fitChange": (round((runs[-1]["top_fit"] - runs[0]["top_fit"]) * 100)
                          if len(runs) > 1 else None),
            "takenAt": None,
        }
        if latest is not None:
            entry.update({
                "topCareer": latest["top_career"],
                "fit": round(latest["top_fit"] * 100),
                "takenAt": latest["created_at"],
            })
            career_counts[latest["top_career"]] += 1
            result = json.loads(latest["result"])
            for gap in result.get("gap", {}).get("rows", []):
                if gap.get("gap", 0) > 0.5:
                    gap_counts[gap["dim"]] += 1
        rows.append(entry)

    return jsonify({
        "classCode": class_code,
        "teacher": g.user["name"],
        "studentCount": len(rows),
        "completedCount": sum(1 for r in rows if r["completed"]),
        "students": rows,
        "topCareers": [{"career": c, "count": n} for c, n in career_counts.most_common(5)],
        "commonGaps": [{"dim": d, "label": labels.get(d, d), "count": n}
                       for d, n in gap_counts.most_common(5)],
        # A workshop idea for each of the three skills most of the class is short on.
        "workshops": [{"dim": d, "label": labels.get(d, d), "count": n,
                       "idea": WORKSHOPS.get(d, {}).get(lang, "")}
                      for d, n in gap_counts.most_common(3) if d in WORKSHOPS],
    })


# ------------------------------------------------------------------- parent --

@bp.post("/api/parent/link")
@auth.login_required("parent")
def parent_link():
    """A parent links to a child using the share code shown on the child's account."""
    code = str((request.get_json(silent=True) or {}).get("shareCode", "")).strip().upper()[:12]
    if not code:
        return jsonify({"error": "Enter the code from your child's account."}), 400

    database = get_db()
    student = database.execute(
        "SELECT id, name FROM users WHERE share_code = ? AND role = 'student'", (code,)
    ).fetchone()
    if student is None:
        return jsonify({"error": "No student found with that code. Check it and try again."}), 404

    database.execute(
        "INSERT OR IGNORE INTO links (parent_id, student_id, created_at) VALUES (?, ?, ?)",
        (g.user["id"], student["id"], datetime.now(timezone.utc).isoformat()),
    )
    database.commit()
    return jsonify({"linked": {"id": student["id"], "name": student["name"]}}), 201


@bp.get("/api/parent/children")
@auth.login_required("parent")
def parent_children():
    """
    One card per linked child: their latest top match, the reasons, and the
    suggested next steps. No transcript — what they said stays theirs.
    """
    database = get_db()
    children = database.execute(
        """SELECT u.id, u.name, u.branch, u.college
           FROM links l JOIN users u ON u.id = l.student_id
           WHERE l.parent_id = ? ORDER BY u.name""",
        (g.user["id"],),
    ).fetchall()

    out = []
    for child in children:
        latest = _latest_result(child["id"])
        card = {
            "id": child["id"], "name": child["name"],
            "branch": child["branch"], "college": child["college"],
            "completed": latest is not None,
        }
        if latest is not None:
            lang = _lang()
            result = json.loads(latest["result"])
            runs = _all_runs(child["id"])

            # "How to support your child at home": tied to the skills this
            # child's top career leans on and they're still short of.
            gap_dims = [g["dim"] for g in result.get("gap", {}).get("rows", [])
                        if g.get("gap", 0) > 0.5][:2]
            tips = [PARENT_TIPS[d][lang] for d in gap_dims if d in PARENT_TIPS]
            tips.append(PARENT_GENERAL_TIP[lang])

            card.update({
                "takenAt": latest["created_at"],
                "matches": result.get("matches", [])[:3],
                "roadmap": result.get("roadmap", [])[:4],
                "summary": result.get("summary", ""),
                "attempts": len(runs),
                "progress": [{"takenAt": r["created_at"], "topCareer": r["top_career"],
                              "fit": round(r["top_fit"] * 100)} for r in runs[-8:]],
                "skillChange": _skill_change(runs, lang),
                "tips": tips,
            })
        out.append(card)

    return jsonify({"parent": g.user["name"], "children": out})
