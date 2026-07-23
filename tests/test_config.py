"""Tests for configuration module."""

from src.wellcare.config import (
    ADMIN_USERNAME,
    APP_GEOMETRY,
    APP_MIN_HEIGHT,
    APP_MIN_WIDTH,
    APP_TITLE,
    AUTO_REFRESH_INTERVAL_MS,
    COLOR_DANGER,
    COLOR_DARK_BG,
    COLOR_HEADER,
    COLOR_LIGHT_BG,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_WHITE,
    DATABASE_PATH,
    DEFAULT_APPEARANCE_MODE,
    DEFAULT_COLOR_THEME,
    PRESCRIPTIONS_DIR,
    STAFF_USERNAME,
)


class TestConfig:
    """Tests that config values are loaded correctly."""

    def test_app_title(self) -> None:
        assert APP_TITLE == "WellCare Hospital Patient Management"

    def test_app_geometry(self) -> None:
        assert APP_GEOMETRY == "1440x1024"

    def test_app_min_width(self) -> None:
        assert APP_MIN_WIDTH == 900

    def test_app_min_height(self) -> None:
        assert APP_MIN_HEIGHT == 700

    def test_appearance_mode(self) -> None:
        assert DEFAULT_APPEARANCE_MODE == "Light"

    def test_color_theme(self) -> None:
        assert DEFAULT_COLOR_THEME == "blue"

    def test_colors(self) -> None:
        assert COLOR_PRIMARY == "#1e85da"
        assert COLOR_DARK_BG == "#2b2b2b"
        assert COLOR_LIGHT_BG == "#ebebeb"
        assert COLOR_HEADER == "#1e3c72"
        assert COLOR_WHITE == "#ffffff"
        assert COLOR_SUCCESS == "#52bb6c"
        assert COLOR_DANGER == "#e25353"
        assert COLOR_WARNING == "#ffd700"

    def test_credentials(self) -> None:
        assert ADMIN_USERNAME == "admin"
        assert STAFF_USERNAME == "staff"

    def test_dashboard_refresh(self) -> None:
        assert AUTO_REFRESH_INTERVAL_MS == 10000

    def test_paths(self) -> None:
        assert "Patient_Prescriptions" in str(PRESCRIPTIONS_DIR)
        assert "clinic.db" in str(DATABASE_PATH)
