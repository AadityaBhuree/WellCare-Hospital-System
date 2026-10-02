"""Authentication utilities using bcrypt for password hashing and security controls."""

import hmac
import time

import bcrypt
from src.wellcare.config import (
    ADMIN_PASSWORD_HASH,
    ADMIN_USERNAME,
    STAFF_PASSWORD_HASH,
    STAFF_USERNAME,
)
from src.wellcare.logger import logger

# In-memory rate limiting tracker: uid -> (failed_attempts, lock_until_timestamp)
_LOGIN_ATTEMPTS: dict[str, tuple[int, float]] = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 30.0


def hash_password(password: str) -> str:
    """Hash a plaintext password with a random salt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed: str) -> bool:
    """Check a plaintext password against a bcrypt hash."""
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
    except (ValueError, AttributeError) as exc:
        logger.error("Password verification error: %s", exc)
        return False


def is_rate_limited(uid: str) -> bool:
    """Check if user ID is currently locked out due to too many failed attempts."""
    if uid in _LOGIN_ATTEMPTS:
        attempts, lock_until = _LOGIN_ATTEMPTS[uid]
        if time.monotonic() < lock_until:
            return True
        if time.monotonic() >= lock_until and attempts >= MAX_FAILED_ATTEMPTS:
            # Reset after lockout period expires
            _LOGIN_ATTEMPTS.pop(uid, None)
    return False


def record_failed_attempt(uid: str) -> None:
    """Record a failed login attempt for rate limiting."""
    attempts, _ = _LOGIN_ATTEMPTS.get(uid, (0, 0.0))
    new_attempts = attempts + 1
    lock_until = 0.0
    if new_attempts >= MAX_FAILED_ATTEMPTS:
        lock_until = time.monotonic() + LOCKOUT_DURATION_SECONDS
        logger.warning(
            "User %s locked out for %d seconds due to %d failed attempts",
            uid,
            int(LOCKOUT_DURATION_SECONDS),
            new_attempts,
        )
    _LOGIN_ATTEMPTS[uid] = (new_attempts, lock_until)


def reset_attempts(uid: str) -> None:
    """Reset failed login attempts on successful login."""
    _LOGIN_ATTEMPTS.pop(uid, None)


def authenticate_user(uid: str, password: str) -> str | None:
    """Authenticate a user by ID and password with timing-safe comparison and rate limiting.

    Returns the role string ("admin" | "staff") on success, or None on failure.
    """
    if is_rate_limited(uid):
        logger.warning("Authentication blocked for %s: rate limited", uid)
        return None

    # Timing-safe username comparisons
    is_admin = hmac.compare_digest(uid, ADMIN_USERNAME)
    is_staff = hmac.compare_digest(uid, STAFF_USERNAME)

    if is_admin and verify_password(password, ADMIN_PASSWORD_HASH):
        reset_attempts(uid)
        logger.info("Admin authentication successful for %s", uid)
        return "admin"

    if is_staff and verify_password(password, STAFF_PASSWORD_HASH):
        reset_attempts(uid)
        logger.info("Staff authentication successful for %s", uid)
        return "staff"

    record_failed_attempt(uid)
    logger.warning("Failed authentication attempt for %s", uid)
    return None
