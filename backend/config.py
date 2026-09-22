"""Configuration, read from the environment. Nothing secret is hard-coded."""

import os

from dotenv import load_dotenv

load_dotenv()  # reads backend/.env if present; ignored in production


def _bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- database ---------------------------------------------------------------
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "careercompass.db"))

# --- auth -------------------------------------------------------------------
# Rotated per deploy. If unset we generate an ephemeral one so local dev works,
# but every restart then invalidates existing tokens — set it in production.
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
TOKEN_TTL_HOURS = int(os.environ.get("TOKEN_TTL_HOURS", "72"))

# --- Gemini -----------------------------------------------------------------
# The key lives here and only here. The browser never sees it: every Gemini
# call goes through this backend.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_TIMEOUT = float(os.environ.get("GEMINI_TIMEOUT", "20"))
GEMINI_BASE_URL = os.environ.get(
    "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
GEMINI_ENABLED = bool(GEMINI_API_KEY)

# --- CORS -------------------------------------------------------------------
# Comma-separated list of origins allowed to call this API. Defaults to local
# dev only — set ALLOWED_ORIGINS on Render to your GitHub Pages URL.
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500",
    ).split(",") if o.strip()
]

# --- rate limiting ----------------------------------------------------------
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "40"))
AUTH_RATE_LIMIT_PER_MINUTE = int(os.environ.get("AUTH_RATE_LIMIT_PER_MINUTE", "8"))

# --- scoring weights --------------------------------------------------------
# Slide 9: "weighted scoring with academic performance". These are the weights.
INTEREST_WEIGHT = float(os.environ.get("INTEREST_WEIGHT", "0.70"))
ACADEMIC_WEIGHT = float(os.environ.get("ACADEMIC_WEIGHT", "0.30"))

# Cosine similarity between two all-positive vectors is compressed into roughly
# the 0.35-0.95 band, which is why the old demo showed 81-87% for everything.
# We report the raw similarity AND a calibrated fit rescaled across this band.
SIMILARITY_FLOOR = float(os.environ.get("SIMILARITY_FLOOR", "0.35"))
SIMILARITY_CEILING = float(os.environ.get("SIMILARITY_CEILING", "0.95"))

DEBUG = _bool("FLASK_DEBUG", False)
PORT = int(os.environ.get("PORT", "5000"))
