"""Tests for AppointmentsFrame with mocked customtkinter dependencies."""

import tkinter  # noqa: F401
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from src.wellcare.frames.appointments import AppointmentsFrame


@pytest.fixture(autouse=True)
def _mock_tk():
    """Mock customtkinter widgets so the frame can be created without a display."""
    with (
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkFrame.grid_columnconfigure"),
        patch("customtkinter.CTkFrame.pack"),
        patch("customtkinter.CTkFrame.grid"),
        patch("customtkinter.CTkLabel"),
        patch("customtkinter.CTkEntry") as mock_entry,
        patch("customtkinter.CTkComboBox") as mock_combo,
        patch("customtkinter.CTkButton"),
        patch("customtkinter.CTkTextbox") as mock_textbox,
        patch("src.wellcare.frames.appointments.messagebox") as mock_msgbox,
    ):
        mock_entry_instance = MagicMock()
        mock_entry.return_value = mock_entry_instance
        mock_combo_instance = MagicMock()
        mock_combo.return_value = mock_combo_instance
        mock_textbox_instance = MagicMock()
        mock_textbox.return_value = mock_textbox_instance
        yield {
            "entry": mock_entry_instance,
            "combo": mock_combo_instance,
            "textbox": mock_textbox_instance,
            "msgbox": mock_msgbox,
        }


@pytest.fixture
def controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.db = MagicMock()
    return ctrl


@pytest.fixture
def frame(controller: MagicMock) -> "AppointmentsFrame":
    from src.wellcare.frames.appointments import AppointmentsFrame

    master = MagicMock()
    return AppointmentsFrame(master=master, controller=controller)


class TestAppointmentsFrame:
    """Tests for AppointmentsFrame UI actions."""

    def test_init_sets_controller(self, frame, controller) -> None:
        assert frame.controller is controller

    def test_schedule_action_invalid_patient_id(self, frame) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="abc")
        frame._schedule_action()
        frame.controller.db.get_patient_by_id.assert_not_called()

    def test_schedule_action_patient_not_found(self, frame) -> None:
        frame.patient_id_entry.get = MagicMock(return_value="99")
        frame.doctor_combo.get = MagicMock(return_value="Dr. Test (Cardiology)")
        frame.date_entry.get = MagicMock(return_value="2026-07-25")
        frame.slot_combo.get = MagicMock(return_value="09:00 AM")
        frame.notes_entry.get = MagicMock(return_value="Checkup")

        frame.controller.db.get_patient_by_id.return_value = None
        frame._schedule_action()
        frame.controller.db.get_patient_by_id.assert_called_once_with(99)
