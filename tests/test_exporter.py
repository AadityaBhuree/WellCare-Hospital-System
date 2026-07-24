"""Unit tests for the patient data exporter module."""

import json
from pathlib import Path

from src.wellcare.models import Patient
from src.wellcare.utils.exporter import export_patients_to_csv, export_patients_to_json


def test_export_patients_to_csv(tmp_path: Path) -> None:
    patients = [
        Patient(
            id=1,
            first_name="Jane",
            last_name="Doe",
            age="30",
            gender="Female",
            blood_group="A+",
            weight="60",
            mobile="9876543210",
            email="jane@example.com",
            address="123 Street",
            pincode="400001",
            symptoms="Fever",
            created_at="2026-07-24 10:00:00",
        )
    ]
    csv_file = tmp_path / "patients.csv"
    assert export_patients_to_csv(patients, csv_file) is True
    assert csv_file.exists()
    content = csv_file.read_text(encoding="utf-8")
    assert "Jane" in content
    assert "Doe" in content
    assert "jane@example.com" in content


def test_export_patients_to_json(tmp_path: Path) -> None:
    patients = [
        Patient(
            id=2,
            first_name="John",
            last_name="Smith",
            age="45",
            gender="Male",
            blood_group="O+",
            weight="75",
            mobile="9123456789",
            email="john@example.com",
            address="456 Avenue",
            pincode="400002",
            symptoms="Cough",
            created_at="2026-07-24 11:00:00",
        )
    ]
    json_file = tmp_path / "patients.json"
    assert export_patients_to_json(patients, json_file) is True
    assert json_file.exists()
    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["first_name"] == "John"
    assert data[0]["last_name"] == "Smith"
