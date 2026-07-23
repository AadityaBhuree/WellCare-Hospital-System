"""Typed domain models for WellCare Hospital System."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Gender(Enum):
    """Gender categories."""

    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class BloodGroup(Enum):
    """Standard blood groups."""

    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class AppointmentStatus(Enum):
    """Appointment workflow states."""

    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"


class PaymentStatus(Enum):
    """Invoice payment states."""

    PENDING = "Pending"
    PAID = "Paid"
    PARTIAL = "Partial"
    REFUNDED = "Refunded"


@dataclass
class Patient:
    """Patient record entity."""

    id: int | None = None
    first_name: str = ""
    last_name: str = ""
    age: int = 0
    gender: str = ""
    blood_group: str = ""
    weight: float = 0.0
    mobile: str = ""
    email: str = ""
    address: str = ""
    pincode: str = ""
    symptoms: str = ""
    created_at: datetime | None = None

    @property
    def full_name(self) -> str:
        """Return formatted full name."""
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class Appointment:
    """Patient appointment entity."""

    id: int | None = None
    patient_id: int = 0
    doctor_name: str = ""
    department: str = ""
    date: str = ""  # YYYY-MM-DD
    time_slot: str = ""  # e.g. "09:00-09:30"
    status: str = AppointmentStatus.SCHEDULED.value
    notes: str = ""
    created_at: datetime | None = None


@dataclass
class Doctor:
    """Doctor entity."""

    id: int | None = None
    name: str = ""
    specialization: str = ""
    phone: str = ""
    email: str = ""
    available_days: str = "Mon,Tue,Wed,Thu,Fri"
    is_active: bool = True


@dataclass
class Bill:
    """Patient billing invoice entity."""

    id: int | None = None
    patient_id: int = 0
    appointment_id: int | None = None
    amount: float = 0.0
    description: str = ""
    status: str = PaymentStatus.PENDING.value
    created_at: datetime | None = None
