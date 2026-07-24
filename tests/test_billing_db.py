"""Unit tests for billing database CRUD operations and financial statistics."""

from unittest.mock import MagicMock

import pytest
from src.wellcare.database import Database
from src.wellcare.models import Bill, PaymentStatus


@pytest.fixture
def db():
    """Create in-memory SQLite database instance for testing."""
    database = object.__new__(Database)
    database.conn = MagicMock()
    database.cur = MagicMock()
    database._cache = MagicMock()
    return database


class TestBillingDatabase:
    """Test suite for billing database methods."""

    def test_add_bill_success(self, db) -> None:
        db.cur.lastrowid = 101
        bill = Bill(patient_id=1, appointment_id=5, amount=150.0, description="Consultation Fee")
        bill_id = db.add_bill(bill)

        assert bill_id == 101
        db.cur.execute.assert_called()
        db.conn.commit.assert_called_once()

    def test_add_bill_failure(self, db) -> None:
        db.cur.execute.side_effect = Exception("DB Error")
        bill = Bill(patient_id=1, amount=100.0)
        bill_id = db.add_bill(bill)

        assert bill_id is None

    def test_get_bills_all(self, db) -> None:
        db.cur.fetchall.return_value = [
            (101, 1, "John Doe", 5, 150.0, "Consultation", "Pending", "2026-07-24 10:00:00")
        ]
        results = db.get_bills()

        assert len(results) == 1
        assert results[0][2] == "John Doe"

    def test_get_bills_by_patient(self, db) -> None:
        db.cur.fetchall.return_value = []
        results = db.get_bills(patient_id=1)

        assert results == []
        db.cur.execute.assert_called()
        args = db.cur.execute.call_args[0]
        assert "WHERE b.patient_id = ?" in args[0]
        assert args[1] == [1]

    def test_update_bill_status_success(self, db) -> None:
        db.cur.rowcount = 1
        success = db.update_bill_status(101, PaymentStatus.PAID.value)

        assert success is True
        db.conn.commit.assert_called_once()

    def test_get_billing_stats(self, db) -> None:
        db.cur.fetchall.return_value = [
            ("Paid", 150.0),
            ("Paid", 200.0),
            ("Pending", 100.0),
            ("Partial", 50.0),
        ]
        stats = db.get_billing_stats()

        assert stats["total_revenue"] == 350.0
        assert stats["pending_amount"] == 150.0
        assert stats["paid_count"] == 2
        assert stats["pending_count"] == 2
