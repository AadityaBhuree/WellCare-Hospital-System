"""Tests for authentication utilities."""

from src.wellcare.utils.auth import authenticate_user, hash_password, verify_password


class TestHashPassword:
    """Tests for hash_password."""

    def test_hash_returns_string(self) -> None:
        hashed = hash_password("test123")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_starts_with_bcrypt_prefix(self) -> None:
        hashed = hash_password("test123")
        assert hashed.startswith("$2b$")

    def test_hash_is_different_each_time(self) -> None:
        h1 = hash_password("test123")
        h2 = hash_password("test123")
        assert h1 != h2


class TestVerifyPassword:
    """Tests for verify_password."""

    def test_verify_correct_password(self) -> None:
        hashed = hash_password("correct_password")
        assert verify_password("correct_password", hashed) is True

    def test_verify_wrong_password(self) -> None:
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_verify_empty_password(self) -> None:
        hashed = hash_password("mypassword")
        assert verify_password("", hashed) is False

    def test_verify_invalid_hash(self) -> None:
        assert verify_password("test", "invalid_hash") is False


class TestAuthenticateUser:
    """Tests for authenticate_user.

    Environment variables are set by ``tests/conftest.py``, making
    these tests CI-safe without a real ``.env`` file.
    """

    def test_authenticate_valid_admin(self) -> None:
        role = authenticate_user("admin", "123")
        assert role == "admin"

    def test_authenticate_valid_staff(self) -> None:
        role = authenticate_user("staff", "123")
        assert role == "staff"

    def test_authenticate_invalid_password(self) -> None:
        role = authenticate_user("admin", "wrong_password")
        assert role is None

    def test_authenticate_invalid_username(self) -> None:
        role = authenticate_user("unknown", "123")
        assert role is None

    def test_authenticate_empty_credentials(self) -> None:
        role = authenticate_user("", "")
        assert role is None
