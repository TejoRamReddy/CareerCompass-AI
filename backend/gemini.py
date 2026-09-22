"""
Gemini client.

Three jobs, all server-side so the API key never reaches a browser:

    next_question()    decides what to ask next, given the conversation so far

    extract_profile()  turns the whole conversation into a 12-dimension vector

    explain_matches()  writes a short reason each career fits this student

Every call raises GeminiUnavailable on any failure (no key, network, bad
JSON, safety block). The caller falls back to the scripted engine, so the
product still works with no key, no internet, and no surprises on stage.
"""

import json
import logging
import re
import time as _time
from typing import Dict, List, Optional

import requests

import config
from careers_data import DIMS


log = logging.getLogger(__name__)

ENDPOINT = "{base}/models/{model}:generateContent"


def _redact(text) -> str:
    """Never let the API key reach a log line or a response body."""
    text = str(text)

    key = config.GEMINI_API_KEY

    if key:
        text = text.replace(key, "<redacted>")

    return text


class GeminiUnavailable(RuntimeError):
    """Raised whenever Gemini can't give us a usable answer."""


def available() -> bool:
    return config.GEMINI_ENABLED


# --------------------------------------------------------------------- probe --

# "A key exists" and "Gemini is answering" are different things:
# a wrong key, retired model name or quota problem all leave the key present.
# The health endpoint uses probe() so the UI badge reflects what will
# really happen.

_probe_cache = {
    "at": 0.0,
    "result": None
}

PROBE_TTL_SECONDS = 60


def probe(force: bool = False) -> dict:
    """
    Return:

        {
            "configured": bool,
            "reachable": bool,
            "model": str,
            "error": str | None
        }
    """

    if not config.GEMINI_ENABLED:
        return {
            "configured": False,
            "reachable": False,
            "model": config.GEMINI_MODEL,
            "error": None,
        }

    now = _time.time()

    cached = _probe_cache["result"]

    if (
        not force
        and cached is not None
        and now - _probe_cache["at"] < PROBE_TTL_SECONDS
    ):
        return cached

    try:
        _call(
            'Reply with JSON only: {"ok": true}',
            "ping",
            max_tokens=40
        )

        result = {
            "configured": True,
            "reachable": True,
            "model": config.GEMINI_MODEL,
            "error": None,
        }

    except GeminiUnavailable as exc:

        result = {
            "configured": True,
            "reachable": False,
            "model": config.GEMINI_MODEL,
            "error": _redact(exc)[:200],
        }

    _probe_cache["at"] = now
    _probe_cache["result"] = result

    return result


# --------------------------------------------------------------------- call --

def _call(
    system: str,
    user: str,
    *,
    as_json: bool = True,
    max_tokens: int = 800
) -> str:

    if not config.GEMINI_ENABLED:
        raise GeminiUnavailable(
            "no GEMINI_API_KEY configured"
        )

    def build(with_thinking_off: bool) -> dict:

        body = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": system
                    }
                ]
            },

            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": user
                        }
                    ]
                }
            ],

            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": max_tokens,
            }
        }

        if with_thinking_off:
            # Some newer Gemini models support thinkingConfig.
            # We disable thinking because our prompts request short,
            # structured responses.

            body["generationConfig"]["thinkingConfig"] = {
                "thinkingBudget": 0
            }

        if as_json:
            body["generationConfig"]["responseMimeType"] = (
                "application/json"
            )

        return body

    url = ENDPOINT.format(
        base=config.GEMINI_BASE_URL,
        model=config.GEMINI_MODEL
    )

    def post(body):

        try:

            return requests.post(
                url,

                headers={
                    "x-goog-api-key": config.GEMINI_API_KEY,
                    "Content-Type": "application/json",
                },

                json=body,

                timeout=config.GEMINI_TIMEOUT,
            )

        except requests.RequestException as exc:

            raise GeminiUnavailable(
                _redact(f"network error: {exc}")
            ) from exc

    # ------------------------------------------------------------------
    # First attempt
    # ------------------------------------------------------------------

    res = post(
        build(with_thinking_off=True)
    )

    # ------------------------------------------------------------------
    # Some Gemini model families reject thinkingConfig with HTTP 400.
    # Retry once without it.
    # ------------------------------------------------------------------

    if (
        res.status_code == 400
        and "thinkingConfig" in res.text
    ):

        res = post(
            build(with_thinking_off=False)
        )

    # ------------------------------------------------------------------
    # Gemini may temporarily return HTTP 503 when the model is busy.
    #
    # Retry twice with short delays.
    # ------------------------------------------------------------------

    if res.status_code == 503:

        for delay in (1, 2):

            _time.sleep(delay)

            res = post(
                build(with_thinking_off=True)
            )

            if res.status_code == 200:
                break

            # If the retry rejects thinkingConfig,
            # try once without it.

            if (
                res.status_code == 400
                and "thinkingConfig" in res.text
            ):

                res = post(
                    build(with_thinking_off=False)
                )

                if res.status_code == 200:
                    break

    # ------------------------------------------------------------------
    # Final HTTP error
    # ------------------------------------------------------------------

    if res.status_code != 200:

        raise GeminiUnavailable(
            _redact(
                f"HTTP {res.status_code}: {res.text[:200]}"
            )
        )

    # ------------------------------------------------------------------
    # Parse Gemini response
    # ------------------------------------------------------------------

    try:

        data = res.json()

    except ValueError as exc:

        raise GeminiUnavailable(
            f"invalid JSON response from Gemini: {exc}"
        ) from exc

    try:

        candidates = data["candidates"]

        finish_reason = candidates[0].get(
            "finishReason",
            ""
        )

        parts = candidates[0].get(
            "content",
            {}
        ).get(
            "parts",
            []
        )

        text = "".join(
            p.get("text", "")
            for p in parts
        ).strip()

    except (
        KeyError,
        IndexError,
        ValueError
    ) as exc:

        raise GeminiUnavailable(
            f"unexpected response shape: {exc}"
        ) from exc

    # ------------------------------------------------------------------
    # Empty response handling
    # ------------------------------------------------------------------

    if not text:

        if finish_reason == "MAX_TOKENS":

            raise GeminiUnavailable(
                f"hit max_tokens ({max_tokens}) "
                "before producing text — raise max_tokens"
            )

        block = (
            data.get("promptFeedback", {})
            .get("blockReason")
        )

        if block:

            raise GeminiUnavailable(
                f"blocked by Gemini safety filter: {block}"
            )

        raise GeminiUnavailable(
            "empty response "
            f"(finishReason={finish_reason or 'unknown'})"
        )

    return text


# ------------------------------------------------------------------ JSON -----

def _parse_json(text: str) -> dict:

    try:

        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # Models occasionally wrap JSON in prose or a code fence.

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if match:

        try:

            return json.loads(
                match.group(0)
            )

        except json.JSONDecodeError as exc:

            raise GeminiUnavailable(
                f"could not parse JSON: {exc}"
            ) from exc

    raise GeminiUnavailable(
        "no JSON object in response"
    )


def _lang_name(lang: str) -> str:
    return "Tamil" if lang == "ta" else "English"


# ---------------------------------------------------------------- interview --

INTERVIEW_SYSTEM = """You are the career counsellor inside CareerCompass AI, \
talking to a student in Tamil Nadu, India. Many of them are the first in their \
family to reach college, and many studied in Tamil-medium schools.

Your job is to run a short, warm conversation — not a quiz. Ask ONE question at \
a time. Each question must follow from what the student just said: pick up a \
specific detail they mentioned and go one level deeper. Never repeat a question \
already in the transcript, and never present a list of options to choose from.

Rules:

- Write in {language}. Keep the question under 30 words, at a class-10 reading level.
- No jargon, no assumptions about their family's money, caste or background.
- Never name a career or hint at what they should become. You are gathering, not advising.
- Aim for {min_turns}-{max_turns} questions total, then stop.
- If the student's answer is very short or says "I don't know", ask something easier \
and more concrete instead of pressing.
- Consistency check: around question 4 or 5, pick ONE strong claim the student made \
earlier ("I love coding", "I'm good at maths") and ask for a specific, recent example \
of it. Do this kindly, as curiosity, never as doubt. Never accuse the student of lying.

Reply with JSON only:

{{"question": "<the next question, or empty string if done>", "done": <true|false>, "note": "<one short phrase: what you learned from the last answer>"}}"""


def next_question(
    transcript: List[dict],
    lang: str = "en",
    min_turns: int = 5,
    max_turns: int = 7
) -> dict:

    """
    transcript: [{"role": "ai"|"student", "text": ...}, ...]

    Returns:
        {
            "question": str,
            "done": bool,
            "note": str
        }
    """

    answered = sum(
        1
        for t in transcript
        if t.get("role") == "student"
    )

    lines = "\n".join(
        f"{'Counsellor' if t.get('role') == 'ai' else 'Student'}: "
        f"{t.get('text', '')}"
        for t in transcript
    ) or "(the conversation has not started yet)"

    system = INTERVIEW_SYSTEM.format(
        language=_lang_name(lang),
        min_turns=min_turns,
        max_turns=max_turns
    )

    user = (
        f"Conversation so far:\n{lines}\n\n"
        f"The student has answered {answered} question(s). "
        f"{'You have enough to build a profile — set done to true.' if answered >= max_turns else 'Ask the next question.'}"
    )

    data = _parse_json(
        _call(
            system,
            user,
            max_tokens=300
        )
    )

    question = str(
        data.get("question", "")
    ).strip()

    done = bool(
        data.get("done")
    ) or not question

    if answered >= min_turns and not question:
        done = True

    if not done and not question:
        raise GeminiUnavailable(
            "no question returned"
        )

    return {
        "question": question,
        "done": done,
        "note": str(
            data.get("note", "")
        ).strip()
    }


# ------------------------------------------------------------- profile ------

PROFILE_SYSTEM = """You read a career-counselling conversation and score the \
student on 12 skill and interest dimensions.

Dimensions: coding, math, science, design, communication, business, leadership, \
empathy, writing, research, handsOn, creativity.

Score each 0-5 based ONLY on evidence in the conversation:

0 = never came up

1-2 = mentioned in passing, or weak evidence

3 = clear interest or some experience

4-5 = strong, repeated, specific evidence (they described doing it, not just liking it)

Be strict. Do not give a 4 or 5 unless the student gave a concrete example. Most \
dimensions in a short conversation should be 0-2.

Also write a two-sentence summary of this student in {language}, in the second \
person ("You..."), describing what they are drawn to and how they like to work.

Then assess CONSISTENCY: did the concrete examples the student gave back up the \
interests they claimed? "high" = claims were backed by specific examples; "medium" = \
some backed, some only asserted; "low" = mostly assertions, or answers contradict \
each other. List at most 2 flags in {language}, each one short and neutral \
("Said they love maths but gave no example"). Empty list if none. Never guess at \
motives.

Reply with JSON only:

{{"scores": {{"coding": 0, "math": 0, "science": 0, "design": 0, \
"communication": 0, "business": 0, "leadership": 0, "empathy": 0, \
"writing": 0, "research": 0, "handsOn": 0, "creativity": 0}}, \
"summary": "<two sentences>", \
"evidence": {{"<dimension>": "<the phrase they said that justified a score of 3+>"}}, \
"consistency": {{"level": "<high|medium|low>", "flags": ["<short flag>"]}}}}"""


def extract_profile(
    transcript: List[dict],
    lang: str = "en"
) -> dict:

    """
    Conversation ->
    {
        "vector": [12 floats],
        "summary": str,
        "evidence": {...}
    }
    """

    lines = "\n".join(
        f"{'Counsellor' if t.get('role') == 'ai' else 'Student'}: "
        f"{t.get('text', '')}"
        for t in transcript
    )

    if not lines.strip():
        raise GeminiUnavailable(
            "empty transcript"
        )

    data = _parse_json(
        _call(
            PROFILE_SYSTEM.format(
                language=_lang_name(lang)
            ),
            f"Conversation:\n{lines}",
            max_tokens=900
        )
    )

    scores = data.get("scores") or {}

    if not isinstance(scores, dict):
        raise GeminiUnavailable(
            "scores missing"
        )

    vector = []

    for dim in DIMS:

        try:

            value = float(
                scores.get(dim, 0)
            )

        except (
            TypeError,
            ValueError
        ):

            value = 0.0

        vector.append(
            max(
                0.0,
                min(5.0, value)
            )
        )

    if sum(vector) == 0:

        raise GeminiUnavailable(
            "all-zero profile"
        )

    raw = (
        data.get("consistency")
        if isinstance(
            data.get("consistency"),
            dict
        )
        else {}
    )

    level = str(
        raw.get("level", "")
    ).lower()

    flags = (
        raw.get("flags")
        if isinstance(
            raw.get("flags"),
            list
        )
        else []
    )

    consistency = None

    if level in {
        "high",
        "medium",
        "low"
    }:

        consistency = {
            "level": level,
            "flags": [
                str(f).strip()[:160]
                for f in flags
                if str(f).strip()
            ][:2]
        }

    return {
        "vector": vector,
        "summary": str(
            data.get("summary", "")
        ).strip(),

        "evidence": {
            k: str(v)
            for k, v in (
                data.get("evidence") or {}
            ).items()
            if isinstance(k, str)
        },

        "consistency": consistency,
    }


# ------------------------------------------------------------ explanations --

EXPLAIN_SYSTEM = """You explain career recommendations to a student in Tamil Nadu.

For each career given, write ONE sentence (max 28 words) in {language} saying why \
it fits THIS student. Use the student's own words and examples from the \
conversation — quote the specific thing they said. Never use generic praise like \
"your strong analytical skills". Address them as "you".

If a career fits only partly, say so honestly in the same sentence.

Reply with JSON only:
{{"<career name exactly as given>": "<one sentence>"}}"""


def explain_matches(
    transcript: List[dict],
    careers: List[dict],
    lang: str = "en"
) -> Dict[str, str]:

    """
    Returns:
        {career_name: one-sentence reason}
    """

    lines = "\n".join(
        f"{'Counsellor' if t.get('role') == 'ai' else 'Student'}: "
        f"{t.get('text', '')}"
        for t in transcript
    )

    listing = "\n".join(
        f"- {c['name']}: needs {c.get('needs', '')}"
        for c in careers
    )

    data = _parse_json(
        _call(
            EXPLAIN_SYSTEM.format(
                language=_lang_name(lang)
            ),
            f"Conversation:\n{lines}\n\n"
            f"Careers to explain:\n{listing}",
            max_tokens=600
        )
    )

    out = {}

    for c in careers:

        text = data.get(
            c["name"]
        )

        if isinstance(text, str) and text.strip():

            out[c["name"]] = text.strip()

    if not out:

        raise GeminiUnavailable(
            "no explanations returned"
        )

    return out


# ------------------------------------------------------------- translation --

def translate(
    text: str,
    target: str
) -> Optional[str]:

    """
    Best-effort translation for free-text the fallback engine can't localise.
    """

    system = (
        f"Translate the user's text into {_lang_name(target)}, "
        f"keeping the tone plain and the meaning exact. "
        f"Reply with JSON only: "
        f"{{\"text\": \"<translation>\"}}"
    )

    try:

        result = _parse_json(
            _call(
                system,
                text,
                max_tokens=400
            )
        ).get("text")

    except GeminiUnavailable:

        return None

    return (
        result.strip()
        if isinstance(result, str) and result.strip()
        else None
    )