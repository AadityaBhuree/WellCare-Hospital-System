"""Tests for BillingFrame with mocked customtkinter dependencies."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _mock_tk():
    """Mock customtkinter widgets so BillingFrame can be instantiated headlessly."""
    with (
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkFrame.grid_columnconfigure"),
        patch("customtkinter.CTkFrame.pack"),
        patch("customtkinter.CTkFrame.grid"),
        patch("customtkinter.CTkLabel"),
        patch("customtkinter.CTkEntry", side_effect=lambda *args, **kwargs: MagicMock()),
        patch("customtkinter.CTkComboBox", side_effect=lambda *args, **kwargs: MagicMock()),
        patch("customtkinter.CTkButton"),
        patch("customtkinter.CTkTextbox", side_effect=lambda *args, **kwargs: MagicMock()),
        patch("src.wellcare.frames.billing.messagebox") as mock_msgbox,
        patch("src.wellcare.frames.billing.ToastNotification"),
        patch("src.wellcare.frames.billing.KPICard") as mock_kpi,
    ):
        mock_kpi.return_value = MagicMock()
        yield {"msgbox": mock_msgbox}


@pytest.fixture
def controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.db = MagicMock()
    ctrl.db.get_billing_stats.return_value = {
        "total_revenue": 1000.0,
        "pending_amount": 250.0,
        "paid_count": 5,
        "pending_count": 2,
    }
    ctrl.db.get_bills.return_value = [
        (1, 10, "John Doe", None, 150.0, "Consultation", "Paid", "2026-07-24")
    ]
    return ctrl


@pytest.fixture
def frame(controller: MagicMock):
    from src.wellcare.frames.billing import BillingFrame

    master = MagicMock()
    return BillingFrame(master=master, controller=controller)


class TestBillingFrame:
    """Test suite for BillingFrame UI operations."""

    def test_init_loads_billing_data(self, frame, controller) -> None:
        assert frame.controller is controller
        controller.db.get_billing_stats.assert_called_once()
        controller.db.get_bills.assert_called_once()

    def test_create_bill_validation_invalid_pid(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="abc")
        frame.amount_entry.get = MagicMock(return_value="100.0")
        frame._create_bill_action()
        controller.db.add_bill.assert_not_called()

    def test_create_bill_validation_invalid_amount(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="1")
        frame.amount_entry.get = MagicMock(return_value="-50.0")
        frame._create_bill_action()
        controller.db.add_bill.assert_not_called()

    def test_create_bill_patient_not_found(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="99")
        frame.amount_entry.get = MagicMock(return_value="100.0")
        frame.desc_entry.get = MagicMock(return_value="Checkup")
        frame.status_combo.get = MagicMock(return_value="Pending")

        controller.db.get_patient_by_id.return_value = None
        frame._create_bill_action()
        controller.db.add_bill.assert_not_called()

    def test_create_bill_success(self, frame, controller) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="1")
        frame.amount_entry.get = MagicMock(return_value="150.00")
        frame.desc_entry.get = MagicMock(return_value="Consultation")
        frame.status_combo.get = MagicMock(return_value="Pending")

        mock_patient = MagicMock()
        mock_patient.full_name = "Jane Doe"
        controller.db.get_patient_by_id.return_value = mock_patient
        controller.db.add_bill.return_value = 101

        frame._create_bill_action()
        controller.db.add_bill.assert_called_once()

    def test_mark_paid_action_success(self, frame, controller) -> None:
        frame.bill_id_entry.get = MagicMock(return_value="101")
        controller.db.update_bill_status.return_value = True

        frame._mark_paid_action()
        controller.db.update_bill_status.assert_called_once_with(101, "Paid")
