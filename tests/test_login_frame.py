"""Tests for LoginFrame with mocked customtkinter dependencies.

``tkinter`` and ``customtkinter`` are available in this environment, so we
only need to mock widget creation — not the entire Tk stack.
"""

from unittest.mock import MagicMock, patch

import pytest

# Import needed modules first so they register in sys.modules properly
import tkinter  # noqa: F401


@pytest.fixture(autouse=True)
def _mock_tk():
    """Mock customtkinter widgets so the frame can be created without a display."""
    with (
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkFrame.grid_columnconfigure"),
        patch("customtkinter.CTkLabel"),
        patch("customtkinter.CTkEntry") as mock_entry,
        patch("customtkinter.CTkButton"),
        patch("src.wellcare.frames.login.messagebox") as mock_msgbox,
    ):
        mock_entry_instance = MagicMock()
        mock_entry.return_value = mock_entry_instance
        yield {
            "entry": mock_entry_instance,
            "msgbox": mock_msgbox,
        }


@pytest.fixture
def controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.is_logged_in = False
    ctrl.current_user_role = None
    return ctrl


@pytest.fixture
def frame(controller: MagicMock, _mock_tk: dict) -> "LoginFrame":
    from src.wellcare.frames.login import LoginFrame

    master = MagicMock()
    f = LoginFrame(master=master, controller=controller)
    f._mock_entry = _mock_tk["entry"]
    f._mock_msgbox = _mock_tk["msgbox"]
    return f


class TestLoginFrameInit:
    """Tests for LoginFrame creation and UI building."""

    def test_init_sets_controller(self, frame, controller) -> None:
        assert frame.controller is controller

    def test_init_creates_widgets(self, frame) -> None:
        assert frame.id_entry is not None
        assert frame.password_entry is not None


class TestLoginCheck:
    """Tests for the _login_check authentication logic."""

    def test_admin_login(self, frame) -> None:
        frame._mock_entry.get.side_effect = ["admin", "123"]
        frame._login_check()

        assert frame.controller.is_logged_in is True
        assert frame.controller.current_user_role == "admin"
        frame.controller.update_nav_buttons.assert_called_once()
        frame.controller.show_frame_by_name.assert_called_with("HomeFrame")
        frame._mock_msgbox.showinfo.assert_called_once_with(
            "Admin Login",
            "Welcome Administrator!\nFull system dashboard unlocked.",
        )

    def test_staff_login(self, frame) -> None:
        frame._mock_entry.get.side_effect = ["staff", "123"]
        frame._login_check()

        assert frame.controller.is_logged_in is True
        assert frame.controller.current_user_role == "staff"
        frame.controller.update_nav_buttons.assert_called_once()
        frame.controller.show_frame_by_name.assert_called_with("HomeFrame")
        frame._mock_msgbox.showinfo.assert_called_once_with(
            "Staff Login",
            "Login Successful. Redirecting to Home.",
        )

    def test_invalid_password(self, frame) -> None:
        frame._mock_entry.get.side_effect = ["admin", "wrong_password"]
        frame._login_check()

        assert frame.controller.is_logged_in is False
        frame._mock_msgbox.showwarning.assert_called_once_with(
            "Warning", "Invalid User ID or Password!",
        )

    def test_invalid_username(self, frame) -> None:
        frame._mock_entry.get.side_effect = ["unknown_user", "123"]
        frame._login_check()

        assert frame.controller.is_logged_in is False
        frame._mock_msgbox.showwarning.assert_called_once()

    def test_empty_credentials(self, frame) -> None:
        frame._mock_entry.get.side_effect = ["", ""]
        frame._login_check()

        assert frame.controller.is_logged_in is False
        frame._mock_msgbox.showwarning.assert_called_once()

    def test_whitespace_stripping(self, frame) -> None:
        frame._mock_entry.get.side_effect = ["  admin  ", "  123  "]
        frame._login_check()

        assert frame.controller.is_logged_in is True
        assert frame.controller.current_user_role == "admin"

    def test_case_sensitive_username(self, frame) -> None:
        frame._mock_entry.get.side_effect = ["Admin", "123"]
        frame._login_check()

        assert frame.controller.is_logged_in is False
        frame._mock_msgbox.showwarning.assert_called_once()
