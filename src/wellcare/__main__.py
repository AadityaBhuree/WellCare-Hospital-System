"""
Entry point for WellCare Hospital Management System.
Run with: python -m src.wellcare
"""

from src.wellcare.app import ClinicApp


def main() -> None:
    app = ClinicApp()
    app.mainloop()


if __name__ == "__main__":
    main()
