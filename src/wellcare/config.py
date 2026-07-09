"""
Application configuration and constants.

Settings are loaded from environment variables via python-dotenv,
with sensible defaults for development.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Load .env file ─────────────────────────────────────────────────────────
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PRESCRIPTIONS_DIR = PROJECT_ROOT / "Patient_Prescriptions"
DATABASE_PATH = PROJECT_ROOT / "clinic.db"

# ── Application ────────────────────────────────────────────────────────────
APP_TITLE = os.getenv("APP_TITLE", "WellCare Hospital Patient Management")
APP_GEOMETRY = os.getenv("APP_GEOMETRY", "1440x1024")
APP_MIN_WIDTH = int(os.getenv("APP_MIN_WIDTH", "900"))
APP_MIN_HEIGHT = int(os.getenv("APP_MIN_HEIGHT", "700"))

DEFAULT_APPEARANCE_MODE = os.getenv("APPEARANCE_MODE", "Light")  # "Light" | "Dark"
DEFAULT_COLOR_THEME = os.getenv("COLOR_THEME", "blue")

# ── Colors ─────────────────────────────────────────────────────────────────
COLOR_PRIMARY = "#1e85da"
COLOR_DARK_BG = "#2b2b2b"
COLOR_LIGHT_BG = "#ebebeb"
COLOR_HEADER = "#1e3c72"
COLOR_WHITE = "#ffffff"
COLOR_SUCCESS = "#52bb6c"
COLOR_DANGER = "#e25353"
COLOR_WARNING = "#ffd700"

# ── Credentials (loaded from .env) ────────────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
STAFF_USERNAME = os.getenv("STAFF_USERNAME", "staff")
STAFF_PASSWORD_HASH = os.getenv("STAFF_PASSWORD_HASH", "")

# ── Dashboard ──────────────────────────────────────────────────────────────
AUTO_REFRESH_INTERVAL_MS = int(os.getenv("AUTO_REFRESH_INTERVAL_MS", "10000"))  # 10 seconds
