"""Tests for DoctorsFrame with mocked customtkinter dependencies."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _mock_tk():
    """Mock customtkinter widgets so the frame can be instantiated headlessly."""
    with (
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkFrame.grid_columnconfigure"),
        patch("customtkinter.CTkFrame.pack"),
        patch("customtkinter.CTkFrame.grid"),
        patch("customtkinter.CTkScrollableFrame"),
        patch("customtkinter.CTkLabel"),
        patch("customtkinter.CTkEntry", side_effect=lambda *args, **kwargs: MagicMock()),
        patch("customtkinter.CTkButton"),
        patch("src.wellcare.frames.doctors.messagebox"),
        patch("src.wellcare.frames.doctors.ToastNotification"),
    ):
        yield


@pytest.fixture
def controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.db = MagicMock()
    ctrl.current_user_role = "admin"
    return ctrl


@pytest.fixture
def frame(controller: MagicMock):
    from src.wellcare.frames.doctors import DoctorsFrame

    master = MagicMock()
    return DoctorsFrame(master=master, controller=controller)


class TestDoctorsFrame:
    """Tests for DoctorsFrame UI logic and operations."""

    def test_init_sets_controller(self, frame, controller) -> None:
        assert frame.controller is controller

    def test_load_doctors_calls_db(self, frame, controller) -> None:
        controller.db.get_all_doctors.return_value = [
            (1, "Dr. Sarah", "Cardiology", "9876543210", "sarah@clinic.com", "Mon-Fri", 1)
        ]
        frame.load_doctors()
        controller.db.get_all_doctors.assert_called_with(active_only=True)

    def test_filter_doctors_calls_db(self, frame, controller) -> None:
        frame.spec_entry.get = MagicMock(return_value="Cardiology")
        controller.db.get_doctors_by_specialization.return_value = []
        frame._filter_doctors()
        controller.db.get_doctors_by_specialization.assert_called_once_with("Cardiology")

    def test_add_doctor_action_validation_fails(self, frame) -> None:
        frame.name_input.get = MagicMock(return_value="")
        frame.spec_input.get = MagicMock(return_value="")
        frame._add_doctor_action()
        frame.controller.db.add_doctor.assert_not_called()

    def test_add_doctor_action_success(self, frame) -> None:
        frame.name_input.get = MagicMock(return_value="Dr. John")
        frame.spec_input.get = MagicMock(return_value="Neurology")
        frame.phone_input.get = MagicMock(return_value="9876543210")
        frame.email_input.get = MagicMock(return_value="john@clinic.com")
        frame.days_input.get = MagicMock(return_value="Mon,Wed,Fri")
        frame.controller.db.add_doctor.return_value = True

        frame._add_doctor_action()
        frame.controller.db.add_doctor.assert_called_once_with(
            "Dr. John", "Neurology", "9876543210", "john@clinic.com", "Mon,Wed,Fri"
        )
