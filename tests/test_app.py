"""Tests for ClinicApp (central controller).

To avoid complex CustomTkinter widget initialization (which requires a display),
we create ClinicApp instances via ``object.__new__(ClinicApp)`` and set the
necessary attributes manually. This gives us full control over the test
environment while still testing real method implementations.
"""

import tkinter  # noqa: F401
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from src.wellcare.app import ClinicApp


def _make_mock_widget() -> MagicMock:
    """Create a mock widget with common geometry manager methods."""
    w = MagicMock()
    w.grid = MagicMock()
    w.grid_forget = MagicMock()
    w.grid_remove = MagicMock()
    w.pack = MagicMock()
    w.place = MagicMock()
    w.destroy = MagicMock()
    w.configure = MagicMock()
    return w


@pytest.fixture
def app() -> "ClinicApp":
    """Create a ClinicApp instance without calling __init__.

    Uses ``object.__new__`` to bypass CustomTkinter's complex widget
    initialization (which requires a display/server). Then sets up
    minimal attributes needed for testing specific methods.
    """
    from src.wellcare.app import ClinicApp

    app = object.__new__(ClinicApp)

    # Core state variables (set by __init__)
    app.is_logged_in = False
    app.current_user_role = None
    app.current_frame = None

    # Database mock
    mock_db = MagicMock()
    mock_db.conn = MagicMock()
    app.db = mock_db

    # Lifecycle helpers
    app.after = MagicMock()

    # Mock widgets needed by navigation and UI methods
    app.date_label = _make_mock_widget()
    app.main_frame = _make_mock_widget()
    app.upper_frame = _make_mock_widget()
    app.button_frame = _make_mock_widget()
    app.home_screen_button = _make_mock_widget()
    app.about_button = _make_mock_widget()
    app.login_screen_button = _make_mock_widget()
    app.dashboard_button = _make_mock_widget()
    app.new_patient_record_button = _make_mock_widget()
    app.search_button = _make_mock_widget()
    app.logout_button = _make_mock_widget()
    app.mode_switch = _make_mock_widget()
    app.mode_switch.get.return_value = False

    return app


class TestClinicAppState:
    """Tests for initial state setup."""

    def test_default_state(self, app) -> None:
        assert app.is_logged_in is False
        assert app.current_user_role is None
        assert app.current_frame is None

    def test_has_database(self, app) -> None:
        assert app.db is not None
        assert app.db.conn is not None


class TestShowFrameByName:
    """Tests for show_frame_by_name navigation logic."""

    def test_shows_home_frame(self, app) -> None:
        app.is_logged_in = True
        from src.wellcare.frames import HomeFrame

        with (
            patch.object(HomeFrame, "__init__", return_value=None),
            patch.object(HomeFrame, "pack"),
        ):
            app.show_frame_by_name("HomeFrame")
            assert app.current_frame is not None

    def test_shows_login_frame(self, app) -> None:
        from src.wellcare.frames import LoginFrame

        with (
            patch.object(LoginFrame, "__init__", return_value=None),
            patch.object(LoginFrame, "pack"),
        ):
            app.show_frame_by_name("LoginFrame")
            assert app.current_frame is not None

    def test_shows_about_frame(self, app) -> None:
        app.is_logged_in = True
        from src.wellcare.frames import AboutFrame

        with (
            patch.object(AboutFrame, "__init__", return_value=None),
            patch.object(AboutFrame, "pack"),
        ):
            app.show_frame_by_name("AboutFrame")
            assert app.current_frame is not None

    def test_shows_dashboard_when_logged_in(self, app) -> None:
        app.is_logged_in = True
        app.current_user_role = "admin"
        from src.wellcare.frames import DashboardFrame

        with (
            patch.object(DashboardFrame, "__init__", return_value=None),
            patch.object(DashboardFrame, "pack"),
        ):
            app.show_frame_by_name("DashboardFrame")
            assert app.current_frame is not None

    def test_shows_patient_entry_when_logged_in(self, app) -> None:
        app.is_logged_in = True
        from src.wellcare.frames import PatientEntryFrame

        with (
            patch.object(PatientEntryFrame, "__init__", return_value=None),
            patch.object(PatientEntryFrame, "pack"),
        ):
            app.show_frame_by_name("PatientEntryFrame")
            assert app.current_frame is not None

    def test_shows_search_when_logged_in(self, app) -> None:
        app.is_logged_in = True
        from src.wellcare.frames import SearchFrame

        with (
            patch.object(SearchFrame, "__init__", return_value=None),
            patch.object(SearchFrame, "pack"),
        ):
            app.show_frame_by_name("SearchFrame")
            assert app.current_frame is not None

    def test_denies_dashboard_when_logged_out(self, app) -> None:
        app.is_logged_in = False
        with patch("src.wellcare.app.messagebox") as mock_msgbox:
            app.show_frame_by_name("DashboardFrame")
            mock_msgbox.showwarning.assert_called_with(
                "Access Denied",
                "Please login first.",
            )

    def test_denies_patient_entry_when_logged_out(self, app) -> None:
        app.is_logged_in = False
        with patch("src.wellcare.app.messagebox") as mock_msgbox:
            app.show_frame_by_name("PatientEntryFrame")
            mock_msgbox.showwarning.assert_called_with(
                "Access Denied",
                "Please login first.",
            )

    def test_denies_search_when_logged_out(self, app) -> None:
        app.is_logged_in = False
        with patch("src.wellcare.app.messagebox") as mock_msgbox:
            app.show_frame_by_name("SearchFrame")
            mock_msgbox.showwarning.assert_called_with(
                "Access Denied",
                "Please login first.",
            )

    def test_unknown_frame_logs_error(self, app) -> None:
        from src.wellcare.app import logger

        with patch.object(logger, "error") as mock_log:
            app.show_frame_by_name("NonExistentFrame")
            mock_log.assert_called_with("Unknown frame: %s", "NonExistentFrame")

    def test_destroys_previous_frame(self, app) -> None:
        app.is_logged_in = True
        previous = MagicMock()
        app.current_frame = previous
        from src.wellcare.frames import AboutFrame

        with (
            patch.object(AboutFrame, "__init__", return_value=None),
            patch.object(AboutFrame, "pack"),
        ):
            app.show_frame_by_name("AboutFrame")
            previous.destroy.assert_called_once()

    def test_redirects_to_login_on_access_denied(self, app) -> None:
        """When access is denied, redirect to LoginFrame."""
        app.is_logged_in = False
        from src.wellcare.frames import LoginFrame

        with (
            patch("src.wellcare.app.messagebox"),
            patch.object(LoginFrame, "__init__", return_value=None),
            patch.object(LoginFrame, "pack"),
        ):
            app.show_frame_by_name("DashboardFrame")
            assert app.current_frame is not None


class TestUpdateNavButtons:
    """Tests for update_nav_buttons visibility logic."""

    def test_logged_out(self, app) -> None:
        app.is_logged_in = False
        app.update_nav_buttons()

        app.dashboard_button.grid_forget.assert_called()
        app.new_patient_record_button.grid_forget.assert_called()
        app.search_button.grid_forget.assert_called()
        app.logout_button.grid_forget.assert_called()
        app.about_button.grid.assert_called_with(column=1, row=0, padx=15)
        app.login_screen_button.grid.assert_called_with(column=2, row=0, padx=15)

    def test_logged_in_as_admin(self, app) -> None:
        app.is_logged_in = True
        app.current_user_role = "admin"
        app.update_nav_buttons()

        app.login_screen_button.grid_forget.assert_called()
        app.dashboard_button.grid.assert_called_with(column=1, row=0, padx=15)
        app.new_patient_record_button.grid.assert_called_with(column=2, row=0, padx=15)
        app.search_button.grid.assert_called_with(column=3, row=0, padx=15)
        app.about_button.grid.assert_called_with(column=4, row=0, padx=15)
        app.logout_button.grid.assert_called_with(column=5, row=0, padx=15)

    def test_logged_in_as_staff_hides_dashboard(self, app) -> None:
        app.is_logged_in = True
        app.current_user_role = "staff"
        app.update_nav_buttons()

        app.dashboard_button.grid_forget.assert_called()
        app.new_patient_record_button.grid.assert_called_with(column=1, row=0, padx=15)
        app.search_button.grid.assert_called_with(column=2, row=0, padx=15)
        app.about_button.grid.assert_called_with(column=3, row=0, padx=15)
        app.logout_button.grid.assert_called_with(column=4, row=0, padx=15)


class TestLogoutAction:
    """Tests for _logout_action."""

    def test_resets_state(self, app) -> None:
        app.is_logged_in = True
        app.current_user_role = "admin"
        with patch("src.wellcare.app.messagebox"):
            app._logout_action()

        assert app.is_logged_in is False
        assert app.current_user_role is None

    def test_shows_message(self, app) -> None:
        with patch("src.wellcare.app.messagebox") as mock_msgbox:
            app._logout_action()
            mock_msgbox.showinfo.assert_called_with(
                "Logout",
                "You have been logged out successfully.",
            )

    def test_returns_to_home(self, app) -> None:
        from src.wellcare.frames import HomeFrame

        with (
            patch("src.wellcare.app.messagebox"),
            patch.object(HomeFrame, "__init__", return_value=None),
        ):
            app._logout_action()
            assert app.current_frame is not None


class TestToggleMode:
    """Tests for _toggle_mode."""

    def test_dark_mode(self, app) -> None:
        from src.wellcare.app import ctk

        app.mode_switch.get.return_value = True
        with patch.object(ctk, "set_appearance_mode") as mock_set:
            app._toggle_mode()
            mock_set.assert_called_with("Dark")

    def test_light_mode(self, app) -> None:
        from src.wellcare.app import ctk

        app.mode_switch.get.return_value = False
        with patch.object(ctk, "set_appearance_mode") as mock_set:
            app._toggle_mode()
            mock_set.assert_called_with("Light")


class TestRefreshDashboard:
    """Tests for refresh_dashboard_if_open."""

    def test_refresh_when_dashboard_is_current(self, app) -> None:
        from src.wellcare.frames.dashboard import DashboardFrame

        dashboard_mock = _make_mock_widget()
        dashboard_mock.__class__ = DashboardFrame
        app.current_frame = dashboard_mock

        app.refresh_dashboard_if_open()
        dashboard_mock._render_charts.assert_called_once()

    def test_noop_when_other_frame(self, app) -> None:
        app.current_frame = MagicMock()  # Not a DashboardFrame
        app.refresh_dashboard_if_open()


class TestUpdateTime:
    """Tests for _update_time."""

    def test_updates_date_label(self, app) -> None:
        app._update_time()
        app.date_label.configure.assert_called_once()
        call_kwargs = app.date_label.configure.call_args[1]
        assert "text" in call_kwargs
        assert "Date:" in call_kwargs["text"]
        assert "Time:" in call_kwargs["text"]

    def test_schedules_next_update(self, app) -> None:
        app._update_time()
        app.after.assert_called_once_with(1000, app._update_time)
