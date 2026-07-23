"""Design system tokens and theme configuration for WellCare Hospital System."""


class Theme:
    """Centralized design system tokens with light and dark mode support."""

    # Primary colors
    PRIMARY = "#1e3c72"
    PRIMARY_LIGHT = "#2a5298"
    PRIMARY_ACCENT = "#1e85da"

    # Status colors
    SUCCESS = "#10b981"
    SUCCESS_HOVER = "#059669"
    WARNING = "#f59e0b"
    WARNING_HOVER = "#d97706"
    DANGER = "#ef4444"
    DANGER_HOVER = "#dc2626"
    INFO = "#3b82f6"

    # Surface colors (Light Mode)
    SURFACE_LIGHT = "#ffffff"
    SURFACE_HOVER_LIGHT = "#f8fafc"
    CARD_BG_LIGHT = "#f1f5f9"
    BORDER_LIGHT = "#e2e8f0"
    TEXT_PRIMARY_LIGHT = "#0f172a"
    TEXT_SECONDARY_LIGHT = "#64748b"

    # Surface colors (Dark Mode)
    SURFACE_DARK = "#1e293b"
    SURFACE_HOVER_DARK = "#334155"
    CARD_BG_DARK = "#0f172a"
    BORDER_DARK = "#334155"
    TEXT_PRIMARY_DARK = "#f8fafc"
    TEXT_SECONDARY_DARK = "#94a3b8"

    # Typography
    FONT_DISPLAY = ("Segoe UI", 36, "bold")
    FONT_HEADING = ("Segoe UI", 24, "bold")
    FONT_SUBHEADING = ("Segoe UI", 18, "bold")
    FONT_BODY_BOLD = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 14)
    FONT_CAPTION = ("Segoe UI", 12)
    FONT_MONO = ("Cascadia Code", 13)

    # Radii
    RADIUS_CARD = 12
    RADIUS_BUTTON = 8
    RADIUS_PILL = 20

    # Spacing
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 16
    PAD_LG = 24
    PAD_XL = 32
