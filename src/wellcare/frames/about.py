"""
About screen frame with hospital information.
"""
import logging
import webbrowser

import customtkinter as ctk
from PIL import Image
from src.wellcare.config import ASSETS_DIR

logger = logging.getLogger(__name__)


class AboutFrame(ctk.CTkFrame):
    """About page showing hospital information and version details."""

    def __init__(self, master, controller) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        try:
            logo_pil_image = Image.open(ASSETS_DIR / "wellcare.png")
            logo = ctk.CTkImage(
                light_image=logo_pil_image,
                dark_image=logo_pil_image,
                size=(200, 200),
            )
            ctk.CTkLabel(self, text="", image=logo).grid(
                columnspan=2, row=0, column=0, pady=(10, 10),
            )
        except Exception as exc:
            logger.debug("Could not load logo: %s", exc)

        ctk.CTkLabel(
            self,
            text="About WellCare Hospital",
            font=("Courier New", 40, "bold"),
            text_color="#1e3c72",
        ).grid(columnspan=2, row=1, column=0, pady=(20, 20))

        info_text = (
            "WellCare Hospital is a leading healthcare provider dedicated to offering\n"
            "comprehensive medical services with compassion and excellence.\n\n"
            "Our facility is equipped with state-of-the-art technology and staffed\n"
            "by highly trained professionals committed to the well-being of our community.\n\n"
            "Version: 1.0.0 | Clinic Management System"
        )

        ctk.CTkLabel(
            self, text=info_text,
            font=("Roboto", 18), justify="center",
        ).grid(columnspan=2, row=2, column=0, pady=20)

        ctk.CTkButton(
            self,
            text="Visit Website",
            command=lambda: webbrowser.open("https://github.com/"),
            font=("Roboto", 18, "bold"),
            fg_color="#1e85da",
            hover_color="#1565c0",
        ).grid(columnspan=2, row=3, column=0, pady=30)
