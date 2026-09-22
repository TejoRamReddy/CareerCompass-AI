"""
Interview orchestration.

Tries Gemini first for every step. If Gemini isn't configured or fails, falls
back to a scripted question bank and a keyword-based profile extractor, and
labels the result honestly as `engine: "fallback"` so nothing in the UI claims
AI it didn't use.
"""

import logging
import re
from typing import Dict, List

import gemini
from careers_data import (
    DIM_LABELS,
    DIM_LABELS_TA,
    DIMS,
    FALLBACK_QUESTIONS,
    KEYWORD_BOOSTS,
)

log = logging.getLogger(__name__)

MIN_TURNS = 5
MAX_TURNS = 7

OPENERS = {
    "en": "Hi — I'm going to ask you a few questions about yourself. There are no "
          "right answers, so just say what's true. Which subjects do you actually "
          "enjoy, and why?",
    "ta": "வணக்கம் — உங்களைப் பற்றி சில கேள்விகள் கேட்கப் போகிறேன். சரியான பதில் "
          "என்று எதுவும் இல்லை, உண்மையைச் சொன்னால் போதும். எந்தப் பாடங்கள் "
          "உங்களுக்குப் பிடிக்கும், ஏன்?",
}


def _answered(transcript: List[dict]) -> int:
    return sum(1 for t in transcript if t.get("role") == "student")


# ------------------------------------------------------------- questioning --

def opening_question(lang: str = "en") -> Dict:
    return {"question": OPENERS.get(lang, OPENERS["en"]), "done": False, "engine": "scripted"}


def next_question(transcript: List[dict], lang: str = "en") -> Dict:
    """Ask the next question. Gemini if we can, script if we must."""
    answered = _answered(transcript)

    if gemini.available():
        try:
            result = gemini.next_question(transcript, lang, MIN_TURNS, MAX_TURNS)
            result["engine"] = "gemini"
            return result
        except gemini.GeminiUnavailable as exc:
            log.warning("Gemini question failed, using fallback: %s", exc)

    if answered >= MIN_TURNS:
        return {"question": "", "done": True, "engine": "fallback"}

    asked = {t.get("qid") for t in transcript if t.get("role") == "ai"}
    for q in FALLBACK_QUESTIONS:
        if q["id"] not in asked:
            return {"question": q[lang if lang in q else "en"], "qid": q["id"],
                    "done": False, "engine": "fallback"}
    return {"question": "", "done": True, "engine": "fallback"}


# ------------------------------------------------------ profile extraction --

def _keyword_vector(transcript: List[dict]) -> List[float]:
    """
    Fallback extractor: count skill keywords across everything the student said.

    Crude compared with Gemini, but it reads the student's actual words rather
    than a fixed option-to-boost lookup table, and it degrades sensibly.
    """
    text = " ".join(
        t.get("text", "") for t in transcript if t.get("role") == "student"
    ).lower()
    words = set(re.findall(r"[\w\u0b80-\u0bff]+", text))

    vector = []
    for dim in DIMS:
        hits = 0
        for keyword in KEYWORD_BOOSTS.get(dim, []):
            if " " in keyword:
                if keyword in text:
                    hits += 1
            elif keyword in words or any(w.startswith(keyword) for w in words):
                hits += 1
        # 1 hit -> 2.0, 2 -> 3.2, 3 -> 4.0, 4+ -> 4.5, capped at 5
        vector.append(min(5.0, [0, 2.0, 3.2, 4.0, 4.5, 5.0][min(hits, 5)]))
    return vector


def _fallback_summary(vector: List[float], lang: str) -> str:
    labels = DIM_LABELS_TA if lang == "ta" else DIM_LABELS
    ranked = sorted(zip(DIMS, vector), key=lambda p: p[1], reverse=True)
    top = [labels[d] for d, v in ranked if v > 0][:3]
    if not top:
        return ("You didn't give much away in this conversation — retake it with "
                "fuller answers for a sharper profile." if lang != "ta" else
                "இந்த உரையாடலில் அதிகம் தெரியவில்லை — விரிவான பதில்களுடன் மீண்டும் "
                "முயற்சி செய்தால் துல்லியம் கூடும்.")
    if lang == "ta":
        return f"உங்கள் பதில்களில் {', '.join(top)} ஆகியவை தொடர்ந்து வெளிப்படுகின்றன."
    joined = ", ".join(t.lower() for t in top[:-1])
    joined = f"{joined} and {top[-1].lower()}" if joined else top[-1].lower()
    return f"Your answers kept coming back to {joined}."


def build_profile(transcript: List[dict], lang: str = "en") -> Dict:
    """Conversation -> {"vector", "summary", "evidence", "engine"}"""
    if gemini.available():
        try:
            profile = gemini.extract_profile(transcript, lang)
            profile["engine"] = "gemini"
            return profile
        except gemini.GeminiUnavailable as exc:
            log.warning("Gemini profile extraction failed, using fallback: %s", exc)

    vector = _keyword_vector(transcript)
    return {
        "vector": vector,
        "summary": _fallback_summary(vector, lang),
        "evidence": {},
        "consistency": None,   # the scripted engine can't cross-check; it says so
        "engine": "fallback",
    }


# ------------------------------------------------------------ explanations --

def _template_reason(career: dict, gap_free: List[str], lang: str) -> str:
    labels = DIM_LABELS_TA if lang == "ta" else DIM_LABELS
    names = [labels[d] for d in gap_free[:2]]
    if lang == "ta":
        if names:
            return (f"உங்கள் பதில்களில் தெரிந்த {' மற்றும் '.join(names)} "
                    f"தான் இந்தப் பணி அதிகம் நம்பியிருப்பது.")
        return "உங்கள் ஒட்டுமொத்த சுயவிவரம் இந்தத் துறையுடன் ஓரளவு பொருந்துகிறது."
    if names:
        joined = " and ".join(n.lower() for n in names)
        return f"Your answers pointed to {joined}, which is what this work leans on most."
    return "This is a broad fit rather than a sharp one — worth a look, not a decision."


def explain(transcript: List[dict], careers: List[dict], student_vec,
            lang: str = "en") -> Dict[str, str]:
    """
    careers: [{"name", "needs": "coding, math", "strong_dims": [...]}, ...]
    Returns {career_name: one-sentence reason}
    """
    if gemini.available():
        try:
            return gemini.explain_matches(transcript, careers, lang)
        except gemini.GeminiUnavailable as exc:
            log.warning("Gemini explanations failed, using templates: %s", exc)

    out = {}
    for c in careers:
        met = [d for d in c.get("strong_dims", [])
               if student_vec[DIMS.index(d)] >= 3]
        out[c["name"]] = _template_reason(c, met, lang)
    return out
