"""SQLite schema and connection handling.

Tables
------
users         students, teachers and parents (passwords stored as hashes only)
links         parent -> student links, created with a student's share code
careers       the 26-career dataset, seeded once
sessions      one row per interview, including the full transcript
submissions   one row per completed interview, with the scored result
"""

import json
import sqlite3

from flask import g

import config
from careers_data import CAREERS

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    role          TEXT NOT NULL CHECK (role IN ('student','teacher','parent')),
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    branch        TEXT,
    college       TEXT,
    class_code    TEXT,
    share_code    TEXT UNIQUE,
    language      TEXT NOT NULL DEFAULT 'en',
    academics     TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS links (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id  INTEGER NOT NULL REFERENCES users(id),
    student_id INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    UNIQUE (parent_id, student_id)
);

CREATE TABLE IF NOT EXISTS careers (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL UNIQUE,
    name_ta  TEXT NOT NULL,
    category TEXT NOT NULL,
    blurb    TEXT NOT NULL,
    blurb_ta TEXT NOT NULL,
    vector   TEXT NOT NULL,
    academic TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id         TEXT PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    language   TEXT NOT NULL DEFAULT 'en',
    engine     TEXT NOT NULL,
    transcript TEXT NOT NULL,
    state      TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS submissions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT NOT NULL,
    user_id         INTEGER REFERENCES users(id),
    session_id      TEXT REFERENCES sessions(id),
    language        TEXT NOT NULL DEFAULT 'en',
    engine          TEXT NOT NULL,
    interest_vector TEXT NOT NULL,
    academic_vector TEXT NOT NULL,
    combined_vector TEXT NOT NULL,
    top_career      TEXT NOT NULL,
    top_similarity  REAL NOT NULL,
    top_fit         REAL NOT NULL,
    result          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at        TEXT NOT NULL,
    session_id        TEXT NOT NULL UNIQUE REFERENCES sessions(id),
    user_id           INTEGER REFERENCES users(id),
    rating            INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    confidence_after  INTEGER CHECK (confidence_after BETWEEN 1 AND 5),
    would_act         TEXT CHECK (would_act IN ('yes','maybe','no')),
    comment           TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_class ON users(class_code);
CREATE INDEX IF NOT EXISTS idx_sub_user ON submissions(user_id);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect()
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if missing, then seed / refresh the career dataset."""
    conn = connect()
    conn.executescript(SCHEMA)

    # Light migration: databases created before feedback existed lack this column.
    session_cols = {r["name"] for r in conn.execute("PRAGMA table_info(sessions)")}
    if "confidence_before" not in session_cols:
        conn.execute("ALTER TABLE sessions ADD COLUMN confidence_before INTEGER")

    for c in CAREERS:
        conn.execute(
            """
            INSERT INTO careers (name, name_ta, category, blurb, blurb_ta, vector, academic)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                name_ta=excluded.name_ta, category=excluded.category,
                blurb=excluded.blurb, blurb_ta=excluded.blurb_ta,
                vector=excluded.vector, academic=excluded.academic
            """,
            (c["name"], c["name_ta"], c["category"], c["blurb"], c["blurb_ta"],
             json.dumps(c["vec"]), json.dumps(c["academic"])),
        )

    conn.commit()
    conn.close()
