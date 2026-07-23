"""Input validation utilities for patient data entry."""

import re


def validate_mobile(mobile: str) -> str | None:
    """Validate mobile number. Returns error message or None."""
    if not mobile.isdigit() or len(mobile) < 10:
        return "Mobile No must be at least 10 digits."
    return None


def validate_email(email: str) -> str | None:
    """Validate email format. Returns error message or None."""
    if email:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            return "Invalid Email format."
    return None


def validate_weight(weight: str) -> str | None:
    """Validate weight is numeric. Returns error message or None."""
    if weight and not weight.replace(".", "", 1).isdigit():
        return "Weight must be numeric."
    return None


def validate_age(age: str) -> str | None:
    """Validate age selection. Returns error message or None."""
    if age in ("Select Age", ""):
        return "Please select an Age."
    return None


def validate_pincode(pincode: str) -> str | None:
    """Validate pincode format (6 digits for Indian format). Returns error message or None."""
    if pincode and (not pincode.isdigit() or len(pincode) != 6):
        return "Pincode must be a 6-digit number."
    return None


def validate_patient_input(
    mobile: str,
    email: str,
    weight: str,
    age: str,
    pincode: str = "",
) -> str | None:
    """Validate all patient input fields. Returns first error or None."""
    err = validate_mobile(mobile)
    if err:
        return err
    err = validate_email(email)
    if err:
        return err
    err = validate_weight(weight)
    if err:
        return err
    err = validate_age(age)
    if err:
        return err
    err = validate_pincode(pincode)
    if err:
        return err
    return None
