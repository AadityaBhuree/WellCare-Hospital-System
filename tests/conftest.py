"""
Shared pytest fixtures for WellCare tests.

Sets up environment variables at module level so that ``src.wellcare.config``
loads test-friendly defaults without requiring a real ``.env`` file.
This makes the test suite fully CI-safe.
"""

import os

# ── Pre-computed bcrypt hash for "123" ─────────────────────────────────────
_BCRYPT_HASH_123 = "$2b$12$Ilzeazc/m5vkkU9/9fL/j.XAgakZNjAYUis4/bQm8DP/m6Fn2IPfu"

# ── Set environment variables before any module imports ────────────────────
# These are read by config.py (via os.getenv) at import time, so they
# must be set now — before any test file imports src.wellcare.config.
os.environ.setdefault("APP_TITLE", "WellCare Hospital Patient Management")
os.environ.setdefault("APP_GEOMETRY", "1440x1024")
os.environ.setdefault("APP_MIN_WIDTH", "900")
os.environ.setdefault("APP_MIN_HEIGHT", "700")
os.environ.setdefault("APPEARANCE_MODE", "Light")
os.environ.setdefault("COLOR_THEME", "blue")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD_HASH", _BCRYPT_HASH_123)
os.environ.setdefault("STAFF_USERNAME", "staff")
os.environ.setdefault("STAFF_PASSWORD_HASH", _BCRYPT_HASH_123)
os.environ.setdefault("AUTO_REFRESH_INTERVAL_MS", "10000")

# Now it's safe to import config-dependent modules in tests.

import sqlite3

import pytest

from src.wellcare.database import Database


# ── Shared Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def db() -> Database:
    """Create a fresh in-memory Database instance for each test.

    Overrides the file-based :attr:`Database.conn` with an in-memory
    SQLite database so tests never touch the real ``clinic.db``.
    """
    database = Database()
    database.conn = sqlite3.connect(":memory:", check_same_thread=False)
    database.cur = database.conn.cursor()
    database._create_table()
    return database
