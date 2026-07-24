"""Unit tests for Doctor database operations."""

from src.wellcare.database import Database


def test_add_and_get_doctors(tmp_path) -> None:
    db_file = tmp_path / "test_clinic.db"
    db = Database()
    db.conn = __import__("sqlite3").connect(str(db_file))
    db.cur = db.conn.cursor()
    db._create_table()

    # Add doctors
    assert db.add_doctor("Dr. Sarah Connor", "Cardiology", "9876543210", "sarah@clinic.com") is True
    assert (
        db.add_doctor("Dr. Gregory House", "Diagnostics", "9123456789", "house@clinic.com") is True
    )

    # Retrieve all active doctors
    doctors = db.get_all_doctors(active_only=True)
    assert len(doctors) == 2
    names = [d[1] for d in doctors]
    assert "Dr. Sarah Connor" in names
    assert "Dr. Gregory House" in names

    # Filter by specialization
    cardio_docs = db.get_doctors_by_specialization("Cardiology")
    assert len(cardio_docs) == 1
    assert cardio_docs[0][1] == "Dr. Sarah Connor"

    # Toggle active status
    doc_id = cardio_docs[0][0]
    assert db.toggle_doctor_status(doc_id, is_active=False) is True

    # Verify inactive doctor is hidden when active_only=True
    active_after = db.get_all_doctors(active_only=True)
    assert len(active_after) == 1
    assert active_after[0][1] == "Dr. Gregory House"

    db.close()
