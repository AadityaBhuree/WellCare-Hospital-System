"""
Input validation utilities for patient data entry.
"""

import re
from typing import Optional


def validate_mobile(mobile: str) -> Optional[str]:
    """Validate mobile number. Returns error message or None."""
    if not mobile.isdigit() or len(mobile) < 10:
        return "Mobile No must be at least 10 digits."
    return None


def validate_email(email: str) -> Optional[str]:
    """Validate email format. Returns error message or None."""
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid Email format."
    return None


def validate_weight(weight: str) -> Optional[str]:
    """Validate weight is numeric. Returns error message or None."""
    if weight and not weight.replace(".", "", 1).isdigit():
        return "Weight must be numeric."
    return None


def validate_age(age: str) -> Optional[str]:
    """Validate age selection. Returns error message or None."""
    if age in ("Select Age", ""):
        return "Please select an Age."
    return None


def validate_patient_input(
    mobile: str,
    email: str,
    weight: str,
    age: str,
) -> Optional[str]:
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
    return None
