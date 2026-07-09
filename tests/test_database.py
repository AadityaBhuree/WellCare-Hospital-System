"""Tests for Database operations using an in-memory SQLite database."""

import pytest

from src.wellcare.database import Database


@pytest.fixture
def db() -> Database:
    """Create a fresh in-memory Database instance for each test."""
    database = Database()
    # Override with in-memory database for testing
    import sqlite3

    database.conn = sqlite3.connect(":memory:", check_same_thread=False)
    database.cur = database.conn.cursor()
    database._create_table()
    return database


class TestDatabase:
    """Tests for Database CRUD and stats operations."""

    def test_add_patient(self, db: Database) -> None:
        data = (
            "John", "Doe", "30", "Male", "A+", "80",
            "9876543210", "john@example.com", "123 Street", "123456",
            "Fever",
        )
        assert db.add_patient(data) is True

    def test_search_patient_by_first_name(self, db: Database) -> None:
        data = (
            "Jane", "Smith", "25", "Female", "B+", "60",
            "9876543211", "jane@example.com", "456 Avenue", "654321",
            "Headache",
        )
        db.add_patient(data)
        results = db.search_patient("Jane")
        assert len(results) == 1
        assert results[0][1] == "Jane"
        assert results[0][2] == "Smith"

    def test_search_patient_by_last_name(self, db: Database) -> None:
        data = (
            "Bob", "Brown", "40", "Male", "O+", "85",
            "9876543212", "bob@example.com", "789 Road", "789012",
            "Cough",
        )
        db.add_patient(data)
        results = db.search_patient("Brown")
        assert len(results) == 1
        assert results[0][1] == "Bob"

    def test_search_patient_partial_match(self, db: Database) -> None:
        data = (
            "Alice", "Johnson", "35", "Female", "AB+", "65",
            "9876543213", "alice@example.com", "321 Lane", "321098",
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
            "Delete", "Me", "50", "Male", "A-", "70",
            "9876543214", "delete@example.com", "1 Road", "111111",
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
            "John", "Doe", "30", "Male", "A+", "80",
            "9876543210", "john@example.com", "123 Street", "123456",
            "Fever, Cough",
        )
        data2 = (
            "Jane", "Smith", "25", "Female", "B+", "60",
            "9876543211", "jane@example.com", "456 Avenue", "654321",
            "Headache",
        )
        db.add_patient(data1)
        db.add_patient(data2)

        stats = db.get_dashboard_stats()
        assert stats["total"] == 2
        assert len(stats["genders"]) == 2
        assert len(stats["recent"]) == 2

    def test_symptom_frequencies(self, db: Database) -> None:
        db.add_patient((
            "P1", "", "30", "Male", "A+", "80",
            "1", "a@b.com", "Addr", "000000", "Fever, Cough",
        ))
        db.add_patient((
            "P2", "", "25", "Female", "B+", "60",
            "2", "b@b.com", "Addr", "111111", "Fever",
        ))
        db.add_patient((
            "P3", "", "35", "Male", "O+", "70",
            "3", "c@b.com", "Addr", "222222", "Cough, Cold",
        ))

        frequencies = db.get_symptom_frequencies(top_n=3)
        words = [word for word, _ in frequencies]
        assert "fever" in words
        assert "cough" in words
