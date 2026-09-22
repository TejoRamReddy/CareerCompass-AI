"""
The recommendation engine.

Content-based filtering over a pandas DataFrame of career vectors, using
scikit-learn's cosine_similarity, then a weighted blend with academic
performance to produce the final ranking.

Why the numbers used to look inflated
-------------------------------------
Every career vector is all-positive, so cosine similarity between any student
and any career sits in a narrow high band (~0.35-0.95). Reporting that raw
number as a "match %" made a bad fit look like 81%. Two fixes here:

  1. We report `similarity` (the honest raw cosine) separately from `fit`.
  2. `fit` is the raw score rescaled across the realistic band, so the spread
     between a strong and a weak match is actually visible.

Neither number is a probability, and nothing in the UI calls it one.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import minmax_scale

import config
from careers_data import (
    ACADEMIC_SUBJECTS,
    CAREERS,
    DIM_LABELS,
    DIM_LABELS_TA,
    DIMS,
    SKILL_ACTIONS,
    SKILL_ACTIONS_TA,
)

# Which school subject feeds which skill dimension. Marks are evidence of
# ability, so they nudge the same 12 dimensions the interview does.
SUBJECT_TO_DIMS = {
    "math": {"math": 1.0, "research": 0.2},
    "science": {"science": 1.0, "research": 0.3, "handsOn": 0.2},
    "language": {"writing": 0.8, "communication": 0.6},
    "social": {"empathy": 0.4, "communication": 0.4, "research": 0.4, "business": 0.2},
    "computer": {"coding": 1.0, "math": 0.2, "design": 0.2},
}


def careers_dataframe(rows=None) -> pd.DataFrame:
    """Careers as a DataFrame: one row per career, one column per skill."""
    import json

    if rows is None:
        records = [
            {"name": c["name"], "name_ta": c["name_ta"], "category": c["category"],
             "blurb": c["blurb"], "blurb_ta": c["blurb_ta"],
             "vec": c["vec"], "academic": c["academic"]}
            for c in CAREERS
        ]
    else:
        records = [
            {"name": r["name"], "name_ta": r["name_ta"], "category": r["category"],
             "blurb": r["blurb"], "blurb_ta": r["blurb_ta"],
             "vec": json.loads(r["vector"]), "academic": json.loads(r["academic"])}
            for r in rows
        ]

    df = pd.DataFrame(records)
    skills = pd.DataFrame(df["vec"].tolist(), columns=DIMS, index=df.index)
    return pd.concat([df.drop(columns=["vec"]), skills], axis=1)


def academic_vector(academics: Optional[Dict[str, float]]) -> np.ndarray:
    """Marks out of 100 -> a 12-dimension skill vector on the same 0-5 scale."""
    vec = np.zeros(len(DIMS), dtype=float)
    if not academics:
        return vec
    for subject, marks in academics.items():
        if subject not in SUBJECT_TO_DIMS:
            continue
        try:
            score = float(marks)
        except (TypeError, ValueError):
            continue
        score = max(0.0, min(100.0, score)) / 100.0 * 5.0
        for dim, weight in SUBJECT_TO_DIMS[subject].items():
            vec[DIMS.index(dim)] += score * weight
    return np.clip(vec, 0, 5)


def combine(interest: np.ndarray, academic: np.ndarray) -> np.ndarray:
    """Weighted blend of what the student likes and what they're doing well in."""
    interest = np.asarray(interest, dtype=float)
    academic = np.asarray(academic, dtype=float)
    if not academic.any():
        return interest  # no marks supplied — interests carry the whole weight
    return config.INTEREST_WEIGHT * interest + config.ACADEMIC_WEIGHT * academic


def academic_fit(academics: Optional[Dict[str, float]], weights: Dict[str, float]) -> float:
    """
    How well this student's marks line up with the subjects a career leans on.
    Returns 0-1. Falls back to a neutral 0.5 when no marks were given, so a
    student who skipped this step is neither rewarded nor punished.
    """
    if not academics:
        return 0.5
    num = den = 0.0
    for subject in ACADEMIC_SUBJECTS:
        weight = float(weights.get(subject, 0.0))
        if weight <= 0:
            continue
        marks = academics.get(subject)
        if marks is None:
            continue
        try:
            marks = max(0.0, min(100.0, float(marks)))
        except (TypeError, ValueError):
            continue
        num += weight * (marks / 100.0)
        den += weight
    return num / den if den else 0.5


def calibrate(similarity: float) -> float:
    """Rescale raw cosine across its realistic band so the spread is visible."""
    floor, ceiling = config.SIMILARITY_FLOOR, config.SIMILARITY_CEILING
    return float(np.clip((similarity - floor) / (ceiling - floor), 0.0, 1.0))


def rank_careers(interest_vec, academics=None, career_rows=None, top_n: int = 3) -> dict:
    """Score every career and return the top N, plus the vectors used."""
    interest = np.asarray(interest_vec, dtype=float).reshape(1, -1)
    acad_vec = academic_vector(academics)
    combined = combine(interest[0], acad_vec).reshape(1, -1)

    df = careers_dataframe(career_rows)
    matrix = df[DIMS].to_numpy(dtype=float)

    if not combined.any():
        sims = np.zeros(len(df))
    else:
        sims = cosine_similarity(combined, matrix)[0]

    df = df.assign(similarity=sims)
    df["academic_fit"] = df["academic"].apply(lambda w: academic_fit(academics, w))
    df["fit"] = (
        0.75 * df["similarity"].apply(calibrate) + 0.25 * df["academic_fit"]
    )

    # A within-run percentile, so a student can see the shape of the ranking
    # even when several careers score closely.
    if len(df) > 1 and df["fit"].nunique() > 1:
        df["relative"] = minmax_scale(df["fit"])
    else:
        df["relative"] = 0.5

    df = df.sort_values("fit", ascending=False).reset_index(drop=True)

    return {
        "ranked": df,
        "top": df.head(top_n),
        "interest_vector": interest[0],
        "academic_vector": acad_vec,
        "combined_vector": combined[0],
    }


def skill_gap(combined_vec, career_row, lang: str = "en") -> List[dict]:
    """The skills the #1 career leans on hardest, and where the student stands."""
    labels = DIM_LABELS_TA if lang == "ta" else DIM_LABELS
    rows = []
    for i, dim in enumerate(DIMS):
        need = float(career_row[dim])
        if need < 4:
            continue
        have = float(np.clip(combined_vec[i], 0, 5))
        rows.append({
            "dim": dim,
            "label": labels[dim],
            "need": round(need, 1),
            "have": round(have, 1),
            "gap": round(max(0.0, need - have), 1),
        })
    rows.sort(key=lambda r: (-r["gap"], -r["need"]))
    return rows[:4]


def roadmap(gap_rows: List[dict], career_name: str, lang: str = "en") -> List[str]:
    """Two concrete actions for each of the two biggest real gaps."""
    actions = SKILL_ACTIONS_TA if lang == "ta" else SKILL_ACTIONS
    real = [r for r in gap_rows if r["gap"] > 0.5][:2]
    if not real:
        if lang == "ta":
            return [f"உங்கள் சுயவிவரம் ஏற்கனவே {career_name} துறையுடன் நெருக்கமாகப் "
                    f"பொருந்துகிறது — அதை நிரூபிக்கும் ஒரு திட்டத்தை உருவாக்குங்கள்."]
        return [f"Your profile already lines up closely with {career_name} — "
                f"focus on building one portfolio project that proves it."]
    out = []
    for r in real:
        out.extend(actions.get(r["dim"], []))
    return out


def top_skills(vec, n: int = 2, lang: str = "en") -> List[str]:
    labels = DIM_LABELS_TA if lang == "ta" else DIM_LABELS
    pairs = sorted(zip(DIMS, np.asarray(vec, dtype=float)), key=lambda p: p[1], reverse=True)
    return [labels[d] for d, v in pairs if v > 0][:n]
