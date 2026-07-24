"""Unit tests for medical records database operations and MedicalRecordsFrame UI."""

from unittest.mock import MagicMock, patch

import pytest
from src.wellcare.database import Database


@pytest.fixture
def db():
    """Create Database instance for testing."""
    database = object.__new__(Database)
    database.conn = MagicMock()
    database.cur = MagicMock()
    return database


class TestMedicalRecordsDatabase:
    """Test suite for database medical records methods."""

    def test_add_medical_record_success(self, db) -> None:
        db.cur.lastrowid = 1
        rec_id = db.add_medical_record(
            patient_id=1,
            doctor_name="Dr. Smith",
            diagnosis="Flu",
            treatment="Rest",
            notes="Hydrate",
        )

        assert rec_id == 1
        db.conn.commit.assert_called_once()

    def test_add_medical_record_failure(self, db) -> None:
        db.cur.execute.side_effect = Exception("DB Error")
        rec_id = db.add_medical_record(1, "Dr. Smith", "Flu", "Rest")

        assert rec_id is None

    def test_get_patient_medical_history(self, db) -> None:
        db.cur.fetchall.return_value = [
            (1, 1, "John Doe", "Dr. Smith", "Flu", "Rest", "Hydrate", "2026-07-24")
        ]
        records = db.get_patient_medical_history(patient_id=1)

        assert len(records) == 1
        assert records[0][2] == "John Doe"


@pytest.fixture(autouse=True)
def _mock_tk():
    """Mock customtkinter widgets so frame can be created headlessly."""
    with (
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkFrame.grid_columnconfigure"),
        patch("customtkinter.CTkFrame.pack"),
        patch("customtkinter.CTkFrame.grid"),
        patch("customtkinter.CTkLabel"),
        patch("customtkinter.CTkEntry", side_effect=lambda *args, **kwargs: MagicMock()),
        patch("customtkinter.CTkButton"),
        patch("customtkinter.CTkTextbox", side_effect=lambda *args, **kwargs: MagicMock()),
        patch("src.wellcare.frames.medical_records.messagebox") as mock_msgbox,
        patch("src.wellcare.frames.medical_records.ToastNotification"),
    ):
        yield {"msgbox": mock_msgbox}


@pytest.fixture
def controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.db = MagicMock()
    ctrl.db.get_patient_medical_history.return_value = [
        (1, 1, "John Doe", "Dr. Smith", "Flu", "Rest", "Hydrate", "2026-07-24")
    ]
    return ctrl


@pytest.fixture
def frame(controller: MagicMock):
    from src.wellcare.frames.medical_records import MedicalRecordsFrame

    master = MagicMock()
    return MedicalRecordsFrame(master=master, controller=controller)


class TestMedicalRecordsFrame:
    """Test suite for MedicalRecordsFrame UI component."""

    def test_init_loads_records(self, frame, controller) -> None:
        assert frame.controller is controller
        controller.db.get_patient_medical_history.assert_called_once()

    def test_save_record_invalid_pid(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="abc")
        frame._save_record_action()
        controller.db.add_medical_record.assert_not_called()

    def test_save_record_missing_fields(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="1")
        frame.doctor_entry.get = MagicMock(return_value="")
        frame.diagnosis_entry.get = MagicMock(return_value="")
        frame._save_record_action()
        controller.db.add_medical_record.assert_not_called()

    def test_save_record_patient_not_found(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="99")
        frame.doctor_entry.get = MagicMock(return_value="Dr. Smith")
        frame.diagnosis_entry.get = MagicMock(return_value="Flu")
        frame.treatment_entry.get = MagicMock(return_value="Rest")
        controller.db.get_patient_by_id.return_value = None

        frame._save_record_action()
        controller.db.add_medical_record.assert_not_called()

    def test_save_record_success(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="1")
        frame.doctor_entry.get = MagicMock(return_value="Dr. Smith")
        frame.diagnosis_entry.get = MagicMock(return_value="Flu")
        frame.treatment_entry.get = MagicMock(return_value="Rest")
        frame.notes_entry.get = MagicMock(return_value="Hydrate")

        mock_patient = MagicMock()
        mock_patient.full_name = "John Doe"
        controller.db.get_patient_by_id.return_value = mock_patient
        controller.db.add_medical_record.return_value = 1

        frame._save_record_action()
        controller.db.add_medical_record.assert_called_once()
