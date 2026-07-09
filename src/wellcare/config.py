"""
Application configuration and constants.

All tunable settings are centralized here. Sensitive values (credentials)
will be moved to environment variables in a later phase.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PRESCRIPTIONS_DIR = PROJECT_ROOT / "Patient_Prescriptions"
DATABASE_PATH = PROJECT_ROOT / "clinic.db"

# ── Application ────────────────────────────────────────────────────────────
APP_TITLE = "WellCare Hospital Patient Management"
APP_GEOMETRY = "1440x1024"
APP_MIN_WIDTH = 900
APP_MIN_HEIGHT = 700

DEFAULT_APPEARANCE_MODE = "Light"  # "Light" | "Dark"
DEFAULT_COLOR_THEME = "blue"

# ── Colors ─────────────────────────────────────────────────────────────────
COLOR_PRIMARY = "#1e85da"
COLOR_DARK_BG = "#2b2b2b"
COLOR_LIGHT_BG = "#ebebeb"
COLOR_HEADER = "#1e3c72"
COLOR_WHITE = "#ffffff"
COLOR_SUCCESS = "#52bb6c"
COLOR_DANGER = "#e25353"
COLOR_WARNING = "#ffd700"

# ── Credentials (hardcoded defaults — will be moved to env in Phase 3) ──
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"
STAFF_USERNAME = "staff"
STAFF_PASSWORD = "123"

# ── Dashboard ──────────────────────────────────────────────────────────────
AUTO_REFRESH_INTERVAL_MS = 10_000  # 10 seconds
