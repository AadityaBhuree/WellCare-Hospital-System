"""
Authentication utilities using bcrypt for password hashing.
"""

import bcrypt
from src.wellcare.config import (
    ADMIN_PASSWORD_HASH,
    ADMIN_USERNAME,
    STAFF_PASSWORD_HASH,
    STAFF_USERNAME,
)
from src.wellcare.logger import logger


def hash_password(password: str) -> str:
    """Hash a plaintext password with a random salt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed: str) -> bool:
    """Check a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
    except (ValueError, AttributeError) as exc:
        logger.error("Password verification error: %s", exc)
        return False


def authenticate_user(uid: str, password: str) -> str | None:
    """Authenticate a user by ID and password.

    Returns the role string ("admin" | "staff") on success, or None on failure.
    """
    if uid == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH):
        return "admin"
    if uid == STAFF_USERNAME and verify_password(password, STAFF_PASSWORD_HASH):
        return "staff"
    return None
