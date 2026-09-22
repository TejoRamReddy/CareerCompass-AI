"""
Check your Gemini setup end to end, on your own machine.

    cd backend
    python check_gemini.py

It reads GEMINI_API_KEY and GEMINI_MODEL from backend/.env (or the environment),
then runs the same three calls the app makes: ask the next interview question,
extract a profile with the consistency check, and explain a career match.

If the model name is wrong (Google retires models), it lists the ones your key
can actually use so you can copy one into .env.

The key is never printed.
"""

import sys

import requests

import config
import gemini
from careers_data import DIMS

SAMPLE = [
    {"role": "ai", "text": "Which subjects do you actually enjoy, and why?"},
    {"role": "student", "text": "I like computer science and maths. I write small Python "
                                "programs at home, and last week I built a marks calculator "
                                "for my class."},
    {"role": "ai", "text": "What do you do outside class for hours without noticing?"},
    {"role": "student", "text": "Solving logic puzzles, and I help friends fix their phones."},
]


def ok(message):
    print(f"  \u2713 {message}")


def bad(message):
    print(f"  \u2717 {message}")


def list_models():
    try:
        res = requests.get(
            f"{config.GEMINI_BASE_URL}/models",
            headers={"x-goog-api-key": config.GEMINI_API_KEY},
            params={"pageSize": 100}, timeout=15)
        if res.status_code != 200:
            bad(f"Couldn't list models (HTTP {res.status_code}).")
            return
        names = [m["name"].split("/", 1)[1] for m in res.json().get("models", [])
                 if "generateContent" in m.get("supportedGenerationMethods", [])]
        flash = [n for n in names if "flash" in n]
        print("\n  Models your key can use for generateContent:")
        for n in (flash or names)[:12]:
            print(f"    - {n}")
        print("\n  Put one of these in backend/.env as GEMINI_MODEL=<name> and run this again.")
    except requests.RequestException as exc:
        bad(f"Couldn't reach Google to list models: {exc}")


def main() -> int:
    print("CareerCompass AI: Gemini check\n")

    if not config.GEMINI_ENABLED:
        bad("GEMINI_API_KEY is empty. Copy .env.example to .env and paste your key in.")
        print("     Without a key the app still works, using the scripted fallback interview.")
        return 1
    ok(f"Key found (length {len(config.GEMINI_API_KEY)}). Model: {config.GEMINI_MODEL}")

    print("\n1. Reaching Gemini")
    status = gemini.probe(force=True)
    if not status["reachable"]:
        bad(status["error"] or "unknown error")
        list_models()
        print("\n  Common causes: wrong key, model name retired, quota exhausted, or no internet.")
        return 1
    ok("Gemini answered.")

    failures = 0

    print("\n2. Dynamic interview question (should build on the last answer)")
    try:
        q = gemini.next_question(SAMPLE, "en")
        ok(f"Next question: {q['question']!r}")
        if not q["question"]:
            bad("Empty question returned.")
            failures += 1
    except gemini.GeminiUnavailable as exc:
        bad(str(exc)); failures += 1

    print("\n3. Profile extraction + consistency check")
    try:
        p = gemini.extract_profile(SAMPLE, "en")
        top = sorted(zip(DIMS, p["vector"]), key=lambda x: -x[1])[:4]
        ok("Top skills: " + ", ".join(f"{d} {v:g}" for d, v in top))
        ok(f"Summary: {p['summary']!r}")
        if p["consistency"]:
            ok(f"Consistency: {p['consistency']['level']} {p['consistency']['flags']}")
        else:
            bad("No consistency block came back. The app will just hide that note.")
    except gemini.GeminiUnavailable as exc:
        bad(str(exc)); failures += 1

    print("\n4. Match explanation")
    try:
        careers = [{"name": "Backend Developer", "needs": "coding, math"}]
        out = gemini.explain_matches(SAMPLE, careers, "en")
        ok(out.get("Backend Developer", "(missing)"))
    except gemini.GeminiUnavailable as exc:
        bad(str(exc)); failures += 1

    print("\n5. Tamil")
    try:
        q = gemini.next_question(SAMPLE, "ta")
        has_tamil = any("\u0b80" <= ch <= "\u0bff" for ch in q["question"])
        (ok if has_tamil else bad)(f"Tamil question: {q['question']!r}")
        failures += 0 if has_tamil else 1
    except gemini.GeminiUnavailable as exc:
        bad(str(exc)); failures += 1

    print("\n" + ("All good. Start the app: python app.py" if not failures
                  else f"{failures} check(s) failed. The app will fall back where these fail."))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
