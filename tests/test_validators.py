"""Tests for input validation utilities."""

from src.wellcare.utils.validators import (
    validate_age,
    validate_email,
    validate_mobile,
    validate_patient_input,
    validate_weight,
)


class TestValidateMobile:
    """Tests for validate_mobile."""

    def test_valid_mobile(self) -> None:
        assert validate_mobile("9876543210") is None

    def test_mobile_too_short(self) -> None:
        assert validate_mobile("12345") == "Mobile No must be at least 10 digits."

    def test_mobile_empty(self) -> None:
        assert validate_mobile("") == "Mobile No must be at least 10 digits."

    def test_mobile_with_letters(self) -> None:
        assert validate_mobile("abc1234567") == "Mobile No must be at least 10 digits."


class TestValidateEmail:
    """Tests for validate_email."""

    def test_valid_email(self) -> None:
        assert validate_email("test@example.com") is None

    def test_invalid_email_no_at(self) -> None:
        assert validate_email("invalid") == "Invalid Email format."

    def test_invalid_email_no_domain(self) -> None:
        assert validate_email("test@.com") == "Invalid Email format."

    def test_empty_email(self) -> None:
        assert validate_email("") is None


class TestValidateWeight:
    """Tests for validate_weight."""

    def test_valid_weight_integer(self) -> None:
        assert validate_weight("70") is None

    def test_valid_weight_decimal(self) -> None:
        assert validate_weight("70.5") is None

    def test_invalid_weight_text(self) -> None:
        assert validate_weight("heavy") == "Weight must be numeric."

    def test_empty_weight(self) -> None:
        assert validate_weight("") is None


class TestValidateAge:
    """Tests for validate_age."""

    def test_valid_age(self) -> None:
        assert validate_age("25") is None

    def test_age_not_selected(self) -> None:
        assert validate_age("Select Age") == "Please select an Age."

    def test_age_empty(self) -> None:
        assert validate_age("") == "Please select an Age."


class TestValidatePatientInput:
    """Tests for validate_patient_input (integration)."""

    def test_all_valid(self) -> None:
        assert (
            validate_patient_input(
                mobile="9876543210",
                email="test@example.com",
                weight="70",
                age="25",
            )
            is None
        )

    def test_first_error_mobile(self) -> None:
        err = validate_patient_input(
            mobile="123",
            email="test@example.com",
            weight="70",
            age="25",
        )
        assert err == "Mobile No must be at least 10 digits."

    def test_first_error_email(self) -> None:
        err = validate_patient_input(
            mobile="9876543210",
            email="invalid",
            weight="70",
            age="25",
        )
        assert err == "Invalid Email format."

    def test_first_error_weight(self) -> None:
        err = validate_patient_input(
            mobile="9876543210",
            email="test@example.com",
            weight="abc",
            age="25",
        )
        assert err == "Weight must be numeric."

    def test_first_error_age(self) -> None:
        err = validate_patient_input(
            mobile="9876543210",
            email="test@example.com",
            weight="70",
            age="Select Age",
        )
        assert err == "Please select an Age."
