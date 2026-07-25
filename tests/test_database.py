"""Tests for Database operations using an in-memory SQLite database.

The ``db`` fixture is provided by ``tests/conftest.py``.
"""

from src.wellcare.database import Database


class TestDatabase:
    """Tests for Database CRUD and stats operations."""

    def test_add_patient(self, db: Database) -> None:
        data = (
            "John",
            "Doe",
            "30",
            "Male",
            "A+",
            "80",
            "9876543210",
            "john@example.com",
            "123 Street",
            "123456",
            "Fever",
        )
        assert db.add_patient(data) is True

    def test_search_patient_by_first_name(self, db: Database) -> None:
        data = (
            "Jane",
            "Smith",
            "25",
            "Female",
            "B+",
            "60",
            "9876543211",
            "jane@example.com",
            "456 Avenue",
            "654321",
            "Headache",
        )
        db.add_patient(data)
        results = db.search_patient("Jane")
        assert len(results) == 1
        assert results[0][1] == "Jane"
        assert results[0][2] == "Smith"

    def test_search_patient_by_last_name(self, db: Database) -> None:
        data = (
            "Bob",
            "Brown",
            "40",
            "Male",
            "O+",
            "85",
            "9876543212",
            "bob@example.com",
            "789 Road",
            "789012",
            "Cough",
        )
        db.add_patient(data)
        results = db.search_patient("Brown")
        assert len(results) == 1
        assert results[0][1] == "Bob"

    def test_search_patient_partial_match(self, db: Database) -> None:
        data = (
            "Alice",
            "Johnson",
            "35",
            "Female",
            "AB+",
            "65",
            "9876543213",
            "alice@example.com",
            "321 Lane",
            "321098",
            "Cold",
        )
        db.add_patient(data)
        results = db.search_patient("John")
        assert len(results) == 1
        assert results[0][1] == "Alice"

    def test_search_patient_no_results(self, db: Database) -> None:
        results = db.search_patient("NonExistent")
        assert len(results) == 0

    def test_delete_patient(self, db: Database) -> None:
        data = (
            "Delete",
            "Me",
            "50",
            "Male",
            "A-",
            "70",
            "9876543214",
            "delete@example.com",
            "1 Road",
            "111111",
            "Pain",
        )
        db.add_patient(data)
        results = db.search_patient("Delete")
        assert len(results) == 1
        patient_id = results[0][0]

        assert db.delete_patient(patient_id) is True
        assert len(db.search_patient("Delete")) == 0

    def test_delete_nonexistent_patient(self, db: Database) -> None:
        assert db.delete_patient(9999) is False

    def test_dashboard_stats_empty(self, db: Database) -> None:
        stats = db.get_dashboard_stats()
        assert stats["total"] == 0
        assert stats["today"] == 0
        assert stats["genders"] == []
        assert stats["blood_groups"] == []
        assert stats["ages"] == []
        assert stats["symptoms"] == []
        assert stats["trends"] == []
        assert stats["recent"] == []

    def test_dashboard_stats_with_patients(self, db: Database) -> None:
        data1 = (
            "John",
            "Doe",
            "30",
            "Male",
            "A+",
            "80",
            "9876543210",
            "john@example.com",
            "123 Street",
            "123456",
            "Fever, Cough",
        )
        data2 = (
            "Jane",
            "Smith",
            "25",
            "Female",
            "B+",
            "60",
            "9876543211",
            "jane@example.com",
            "456 Avenue",
            "654321",
            "Headache",
        )
        db.add_patient(data1)
        db.add_patient(data2)

        stats = db.get_dashboard_stats()
        assert stats["total"] == 2
        assert len(stats["genders"]) == 2
        assert len(stats["recent"]) == 2

    def test_symptom_frequencies(self, db: Database) -> None:
        db.add_patient(
            (
                "P1",
                "",
                "30",
                "Male",
                "A+",
                "80",
                "1",
                "a@b.com",
                "Addr",
                "000000",
                "Fever, Cough",
            )
        )
        db.add_patient(
            (
                "P2",
                "",
                "25",
                "Female",
                "B+",
                "60",
                "2",
                "b@b.com",
                "Addr",
                "111111",
                "Fever",
            )
        )
        db.add_patient(
            (
                "P3",
                "",
                "35",
                "Male",
                "O+",
                "70",
                "3",
                "c@b.com",
                "Addr",
                "222222",
                "Cough, Cold",
            )
        )

        frequencies = db.get_symptom_frequencies(top_n=3)
        words = [word for word, _ in frequencies]
        assert "fever" in words
        assert "cough" in words

    def test_appointment_crud(self, db: Database) -> None:
        from src.wellcare.models import Appointment, AppointmentStatus

        # First add a patient
        patient_data = (
            "Test",
            "Patient",
            "30",
            "Male",
            "A+",
            "70",
            "9998887776",
            "test@p.com",
            "Addr",
            "123456",
            "Fever",
        )
        assert db.add_patient(patient_data) is True
        patients = db.search_patient("Test")
        assert len(patients) == 1
        patient_id = patients[0][0]

        appt = Appointment(
            patient_id=patient_id,
            doctor_name="Dr. Test",
            department="General",
            date="2026-07-25",
            time_slot="10:00 AM",
            status=AppointmentStatus.SCHEDULED.value,
            notes="Regular checkup",
        )
        assert db.add_appointment(appt) is True

        appts = db.get_appointments()
        assert len(appts) >= 1

        appt_id = appts[0][0]
        assert db.update_appointment_status(appt_id, AppointmentStatus.COMPLETED.value) is True

    def test_audit_logging(self, db: Database) -> None:
        db.log_action("user1", "TEST_ACTION", "Test details")
        logs = db.get_recent_audit_logs(limit=10)
        assert len(logs) >= 1
        assert logs[0][1] == "user1"
        assert logs[0][2] == "TEST_ACTION"
        assert logs[0][3] == "Test details"

    def test_get_appointment_status_counts(self, db: Database) -> None:
        counts = db.get_appointment_status_counts()
        assert isinstance(counts, list)

    def test_search_patient_by_mobile_and_email(self, db: Database) -> None:
        data = (
            "Alice",
            "Wonderland",
            "28",
            "Female",
            "O+",
            "55",
            "9876543219",
            "alice@wonderland.com",
            "789 Path",
            "111222",
            "Flu",
        )
        assert db.add_patient(data) is True
        res_mobile = db.search_patient("9876543219")
        assert len(res_mobile) == 1
        res_email = db.search_patient("alice@wonderland.com")
        assert len(res_email) == 1

    def test_check_appointment_conflict(self, db: Database) -> None:
        from src.wellcare.models import Appointment, AppointmentStatus

        appt = Appointment(
            patient_id=1,
            doctor_name="Dr. Unique",
            department="Cardiology",
            date="2026-08-01",
            time_slot="11:00 AM",
            status=AppointmentStatus.SCHEDULED.value,
        )
        assert db.add_appointment(appt) is True
        assert db.check_appointment_conflict("Dr. Unique", "2026-08-01", "11:00 AM") is True
        assert db.check_appointment_conflict("Dr. Unique", "2026-08-01", "02:00 PM") is False
