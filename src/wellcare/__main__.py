"""Entry point for WellCare Hospital Management System.

Run with: python -m src.wellcare.
"""

from src.wellcare.app import ClinicApp


def main() -> None:
    """Initialize and run the main application event loop."""
    app = ClinicApp()
    app.mainloop()


if __name__ == "__main__":
    main()
