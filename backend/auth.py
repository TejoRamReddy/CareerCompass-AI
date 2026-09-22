"""
Accounts and sessions.

Passwords are never stored or transmitted in plain text: Werkzeug's
generate_password_hash uses PBKDF2-HMAC-SHA256 with a per-user random salt,
and only the resulting hash goes in the database. This is the claim slide 22
and the website make — now it is actually true.

Sessions are stateless JWTs signed with SECRET_KEY.
"""

import functools
import re
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

import config
from db import get_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
ROLES = {"student", "teacher", "parent"}


class AuthError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


# ------------------------------------------------------------------ tokens --

def issue_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=config.TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthError("Your session has expired. Sign in again.", 401)
    except jwt.InvalidTokenError:
        raise AuthError("Invalid session token.", 401)


def current_user(required: bool = True):
    """Read the bearer token and load the user. Returns None when optional."""
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        if required:
            raise AuthError("Sign in to continue.", 401)
        return None

    payload = decode_token(header[7:].strip())
    row = get_db().execute(
        "SELECT * FROM users WHERE id = ?", (payload["sub"],)
    ).fetchone()
    if row is None:
        if required:
            raise AuthError("Account not found.", 401)
        return None
    return row


def login_required(*roles):
    """Decorator. login_required() for any user, login_required('teacher') to scope."""
    def wrapper(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            user = current_user(required=True)
            if roles and user["role"] not in roles:
                return jsonify({"error": "You don't have access to this."}), 403
            g.user = user
            return fn(*args, **kwargs)
        return inner
    return wrapper


# ---------------------------------------------------------------- registry --

def validate_registration(data: dict) -> dict:
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "student").strip().lower()

    if len(name) < 2 or len(name) > 80:
        raise AuthError("Enter your name.")
    if not EMAIL_RE.match(email) or len(email) > 160:
        raise AuthError("Enter a valid email address.")
    if len(password) < 8:
        raise AuthError("Use a password of at least 8 characters.")
    if len(password) > 200:
        raise AuthError("That password is too long.")
    if role not in ROLES:
        raise AuthError("Choose student, teacher or parent.")

    clean = {
        "name": name, "email": email, "password": password, "role": role,
        "branch": (data.get("branch") or "").strip()[:80] or None,
        "college": (data.get("college") or "").strip()[:120] or None,
        "class_code": (data.get("classCode") or "").strip().upper()[:20] or None,
        "language": "ta" if (data.get("language") or "en") == "ta" else "en",
    }

    if role == "student" and not clean["branch"]:
        raise AuthError("Tell us your branch or stream.")
    if role == "student" and not clean["college"]:
        raise AuthError("Tell us your school or college.")
    if role == "teacher" and not clean["class_code"]:
        raise AuthError("Teachers need a class code — make one up and share it with your students.")

    return clean


def create_user(clean: dict) -> int:
    db = get_db()
    existing = db.execute(
        "SELECT 1 FROM users WHERE email = ?", (clean["email"],)
    ).fetchone()
    if existing:
        raise AuthError("An account already exists with that email.", 409)

    share_code = None
    if clean["role"] == "student":
        # Short code a parent types to link to this student.
        for _ in range(10):
            candidate = secrets.token_hex(3).upper()
            if not db.execute("SELECT 1 FROM users WHERE share_code = ?",
                              (candidate,)).fetchone():
                share_code = candidate
                break

    cursor = db.execute(
        """INSERT INTO users
           (role, name, email, password_hash, branch, college, class_code,
            share_code, language, academics, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (clean["role"], clean["name"], clean["email"],
         generate_password_hash(clean["password"]),
         clean["branch"], clean["college"], clean["class_code"], share_code,
         clean["language"], None, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return cursor.lastrowid


def verify_login(email: str, password: str):
    email = (email or "").strip().lower()
    row = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    # Same message either way, so the endpoint can't be used to discover
    # which emails have accounts.
    if row is None or not check_password_hash(row["password_hash"], password or ""):
        raise AuthError("Email or password is incorrect.", 401)
    return row


def public_user(row) -> dict:
    return {
        "id": row["id"],
        "role": row["role"],
        "name": row["name"],
        "email": row["email"],
        "branch": row["branch"],
        "college": row["college"],
        "classCode": row["class_code"],
        "shareCode": row["share_code"],
        "language": row["language"],
    }
