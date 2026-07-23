"""Tests for PatientEntryFrame with mocked customtkinter.

Uses ``MagicMock`` subclasses for widget types so the ``isinstance()``
checks in ``patient_entry.py`` work correctly without a display.
"""

# Import tkinter first so customtkinter can find its sub-modules
import tkinter  # noqa: F401
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from src.wellcare.frames.patient_entry import PatientEntryFrame


# ── Mock widget classes (isinstance-safe) ──────────────────────────────────
# These subclass MagicMock so isinstance(w, MockTextbox) returns True
# when w was created via MagicMock(spec=MockTextbox).


class _MockEntry(MagicMock):
    pass


class _MockComboBox(MagicMock):
    pass


class _MockTextbox(MagicMock):
    pass


@pytest.fixture(autouse=True)
def _mock_tk():
    """Replace customtkinter widget classes with isinstance-safe mocks."""
    with (
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkFrame.grid_columnconfigure"),
        patch("customtkinter.CTkLabel"),
        patch("customtkinter.CTkEntry", _MockEntry),
        patch("customtkinter.CTkComboBox", _MockComboBox),
        patch("customtkinter.CTkTextbox", _MockTextbox),
        patch("customtkinter.CTkButton"),
        patch("customtkinter.CTkFrame") as mock_inner_frame,
    ):
        mock_inner_frame.return_value = MagicMock()
        yield {}


def _make_widget(wtype: type) -> MagicMock:
    """Return a mock widget that isinstance() recognises as *wtype*."""
    w = wtype()
    w.get.return_value = ""
    return w


@pytest.fixture
def controller() -> MagicMock:
    ctrl = MagicMock()
    ctrl.db = MagicMock()
    ctrl.db.conn = MagicMock()
    ctrl.db.add_patient.return_value = True
    return ctrl


@pytest.fixture
def frame(controller: MagicMock, _mock_tk: dict) -> "PatientEntryFrame":
    from src.wellcare.frames.patient_entry import PatientEntryFrame

    master = MagicMock()
    with patch.object(PatientEntryFrame, "_build_ui"):
        f = PatientEntryFrame(master=master, controller=controller)

    # Replace the real inputs dict with controlled mocks
    f.inputs = {}
    for name in ["first_name", "last_name", "weight", "pincode", "email", "mobile"]:
        f.inputs[name] = _make_widget(_MockEntry)

    f.inputs["age"] = _make_widget(_MockComboBox)
    f.inputs["gender"] = _make_widget(_MockComboBox)
    f.inputs["blood"] = _make_widget(_MockComboBox)
    f.inputs["symptoms"] = _make_widget(_MockTextbox)
    f.inputs["address"] = _make_widget(_MockTextbox)

    f.status_label = MagicMock()
    f.after = MagicMock()
    return f


def _set(frame, name: str, value: str) -> None:
    frame.inputs[name].get.return_value = value


# ── Tests ──────────────────────────────────────────────────────────────────


class TestGetVal:
    def test_get_entry(self, frame) -> None:
        _set(frame, "first_name", "John")
        assert frame._get_val("first_name") == "John"

    def test_get_textbox(self, frame) -> None:
        _set(frame, "symptoms", "Fever, Cough")
        assert frame._get_val("symptoms") == "Fever, Cough"

    def test_get_combo(self, frame) -> None:
        _set(frame, "age", "25")
        assert frame._get_val("age") == "25"


class TestDisplayStatus:
    def test_displays_message(self, frame) -> None:
        frame._display_status("Hello", "red")
        frame.status_label.configure.assert_called_with(
            text="Hello",
            text_color="red",
        )

    def test_schedules_clear(self, frame) -> None:
        frame._display_status("X", "green")
        frame.after.assert_called_once()
        cb = frame.after.call_args[0][1]
        cb()
        frame.status_label.configure.assert_called_with(text="")


class TestClearEntries:
    def test_clears_entry(self, frame) -> None:
        frame._clear_entries()
        frame.inputs["first_name"].delete.assert_called_with(0, "end")

    def test_clears_textbox(self, frame) -> None:
        frame._clear_entries()
        frame.inputs["symptoms"].delete.assert_called_with("1.0", "end")

    def test_resets_combos(self, frame) -> None:
        frame._clear_entries()
        frame.inputs["age"].set.assert_called_with("Select Age")
        frame.inputs["gender"].set.assert_called_with("Select")


class TestSaveAction:
    def test_requires_first_name(self, frame) -> None:
        frame._save_action()
        frame.status_label.configure.assert_called_with(
            text="First Name, Last Name, and Mobile are required.",
            text_color="red",
        )

    def test_requires_last_name(self, frame) -> None:
        _set(frame, "first_name", "John")
        _set(frame, "mobile", "9876543210")
        frame._save_action()
        frame.status_label.configure.assert_called_with(
            text="First Name, Last Name, and Mobile are required.",
            text_color="red",
        )

    def test_requires_mobile(self, frame) -> None:
        _set(frame, "first_name", "John")
        _set(frame, "last_name", "Doe")
        frame._save_action()
        frame.status_label.configure.assert_called_with(
            text="First Name, Last Name, and Mobile are required.",
            text_color="red",
        )

    def test_validates_mobile(self, frame) -> None:
        _set(frame, "first_name", "John")
        _set(frame, "last_name", "Doe")
        _set(frame, "mobile", "123")
        frame._save_action()
        frame.status_label.configure.assert_called_with(
            text="Mobile No must be at least 10 digits.",
            text_color="red",
        )

    def test_saves_successfully(self, frame) -> None:
        _set(frame, "first_name", "John")
        _set(frame, "last_name", "Doe")
        _set(frame, "age", "30")
        _set(frame, "mobile", "9876543210")
        _set(frame, "email", "john@test.com")
        _set(frame, "weight", "70")
        _set(frame, "gender", "Male")
        _set(frame, "blood", "A+")
        _set(frame, "symptoms", "Fever")
        _set(frame, "address", "123 Street")
        _set(frame, "pincode", "123456")

        frame._save_action()
        frame.controller.db.add_patient.assert_called_once()
        frame.status_label.configure.assert_called_with(
            text="Patient Record Added Successfully!",
            text_color="green",
        )
        frame.controller.refresh_dashboard_if_open.assert_called_once()
        frame.inputs["first_name"].delete.assert_called()

    def test_shows_db_error(self, frame) -> None:
        frame.controller.db.add_patient.return_value = False
        _set(frame, "first_name", "John")
        _set(frame, "last_name", "Doe")
        _set(frame, "age", "30")
        _set(frame, "mobile", "9876543210")
        _set(frame, "email", "john@test.com")
        _set(frame, "weight", "70")

        frame._save_action()
        frame.status_label.configure.assert_called_with(
            text="Failed to add record.",
            text_color="red",
        )

    def test_handles_no_db_connection(self, frame) -> None:
        frame.controller.db.conn = None
        _set(frame, "first_name", "John")
        _set(frame, "last_name", "Doe")
        _set(frame, "age", "30")
        _set(frame, "mobile", "9876543210")
        _set(frame, "email", "john@test.com")
        _set(frame, "weight", "70")

        frame._save_action()
        frame.status_label.configure.assert_called_with(
            text="Database is unavailable.",
            text_color="red",
        )


class TestSaveAndPrintAction:
    @patch("src.wellcare.frames.patient_entry.generate_prescription")
    def test_save_and_print(self, mock_generate, frame) -> None:
        mock_generate.return_value = "/path/to.pdf"
        _set(frame, "first_name", "John")
        _set(frame, "last_name", "Doe")
        _set(frame, "age", "30")
        _set(frame, "mobile", "9876543210")
        _set(frame, "email", "john@test.com")
        _set(frame, "weight", "70")

        frame._save_and_print_action()
        frame.controller.db.add_patient.assert_called_once()
        mock_generate.assert_called_once_with("John", "Doe", "30", "9876543210")

    @patch("src.wellcare.frames.patient_entry.generate_prescription")
    def test_save_and_print_missing_fields(self, mock_generate, frame) -> None:
        frame._save_and_print_action()
        mock_generate.assert_not_called()
        frame.status_label.configure.assert_called_with(
            text="Required elements missing.",
            text_color="red",
        )
