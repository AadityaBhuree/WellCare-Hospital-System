"""
Central application controller for WellCare Hospital Management System.

Implements the Controller-Frame pattern to manage navigation and global state.
"""

import datetime
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image
from src.wellcare.config import (
    APP_GEOMETRY,
    APP_MIN_HEIGHT,
    APP_MIN_WIDTH,
    APP_TITLE,
    ASSETS_DIR,
    DEFAULT_APPEARANCE_MODE,
    DEFAULT_COLOR_THEME,
)
from src.wellcare.database import Database
from src.wellcare.frames import (
    AboutFrame,
    DashboardFrame,
    HomeFrame,
    LoginFrame,
    PatientEntryFrame,
    SearchFrame,
)
from src.wellcare.logger import logger


class ClinicApp(ctk.CTk):
    """Main controller managing navigation, state, and frame transitions."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode(DEFAULT_APPEARANCE_MODE)
        ctk.set_default_color_theme(DEFAULT_COLOR_THEME)

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(APP_MIN_WIDTH, APP_MIN_HEIGHT)

        self.db = Database()
        if not self.db.conn:
            messagebox.showwarning(
                "Database Error",
                "SQLite database connection failed.\n"
                "Please ensure 'clinic.db' exists and is accessible.",
            )

        self.is_logged_in = False
        self.current_user_role: str | None = None  # "admin" | "staff"
        self.current_frame = None

        self._build_ui()
        self.update_nav_buttons()
        self.show_frame_by_name("HomeFrame")

    def _build_ui(self) -> None:
        # ── Top Banner ────────────────────────────────────────
        self.upper_frame = ctk.CTkFrame(self, fg_color="#1e85da", height=120)
        self.upper_frame.pack(fill="x")

        try:
            img = Image.open(ASSETS_DIR / "wellcare.png")
            logo = ctk.CTkImage(dark_image=img, light_image=img, size=(200, 190))
            ctk.CTkLabel(
                self.upper_frame, text="", image=logo,
            ).place(anchor="nw", rely=-0.19, relx=0.02)
        except Exception as e:
            logger.warning("Could not load logo: %s", e)

        ctk.CTkLabel(
            self.upper_frame,
            text="WellCare Hospital",
            font=("courier new", 55, "bold"),
            text_color="white",
        ).pack(pady=10)

        ctk.CTkLabel(
            self.upper_frame,
            text="Your health, our priority.",
            font=("Roboto", 15, "bold"),
            text_color="#e7dada",
        ).pack(pady=(0, 5))

        self.date_label = ctk.CTkLabel(
            self.upper_frame, font=("", 14), text_color="#e7dada",
        )
        self.date_label.place(relx=0.98, rely=0.03, anchor="ne")

        self.mode_switch = ctk.CTkSwitch(
            self.upper_frame,
            text="Dark Mode",
            text_color="white",
            progress_color="#52bb6c",
            command=self._toggle_mode,
        )
        self.mode_switch.place(relx=0.98, rely=0.3, anchor="ne")

        self._update_time()

        # ── Navigation Buttons ────────────────────────────────
        self.button_frame = ctk.CTkFrame(self.upper_frame, fg_color="transparent")
        self.button_frame.pack(pady=(5, 10))

        nav_args = {
            "fg_color": "transparent",
            "font": ("Roboto", 15, "bold"),
            "hover": True,
            "cursor": "hand2",
        }

        self.home_screen_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("HomeFrame"),
            text="HOME", **nav_args,
        )
        self.home_screen_button.grid(column=0, row=0, padx=15)

        self.about_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("AboutFrame"),
            text="ABOUT", **nav_args,
        )
        self.login_screen_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("LoginFrame"),
            text="LOGIN", **nav_args,
        )
        self.dashboard_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("DashboardFrame"),
            text="DASHBOARD", **nav_args,
        )
        self.new_patient_record_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("PatientEntryFrame"),
            text="NEW PATIENT", **nav_args,
        )
        self.search_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("SearchFrame"),
            text="SEARCH", **nav_args,
        )
        self.logout_button = ctk.CTkButton(
            self.button_frame,
            command=self._logout_action,
            text="LOGOUT",
            fg_color="#e25353",
            font=("Roboto", 15, "bold"),
            hover_color="#c44545",
            cursor="hand2",
        )

        # ── Content Area ──────────────────────────────────────
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def _update_time(self) -> None:
        self.date_label.configure(
            text=datetime.datetime.now().strftime("Date: %d/%m/%Y \nTime: %H:%M:%S"),
        )
        self.after(1000, self._update_time)

    def refresh_dashboard_if_open(self) -> None:
        if isinstance(self.current_frame, DashboardFrame):
            self.current_frame._render_charts()

    def update_nav_buttons(self) -> None:
        if self.is_logged_in:
            self.login_screen_button.grid_forget()
            c_idx = 1

            if self.current_user_role == "admin":
                self.dashboard_button.grid(column=c_idx, row=0, padx=15)
                c_idx += 1
            else:
                self.dashboard_button.grid_forget()

            self.new_patient_record_button.grid(column=c_idx, row=0, padx=15)
            self.search_button.grid(column=c_idx + 1, row=0, padx=15)
            self.about_button.grid(column=c_idx + 2, row=0, padx=15)
            self.logout_button.grid(column=c_idx + 3, row=0, padx=15)
        else:
            self.dashboard_button.grid_forget()
            self.new_patient_record_button.grid_forget()
            self.search_button.grid_forget()
            self.logout_button.grid_forget()

            self.about_button.grid(column=1, row=0, padx=15)
            self.login_screen_button.grid(column=2, row=0, padx=15)

    def _toggle_mode(self) -> None:
        mode = "Dark" if self.mode_switch.get() else "Light"
        ctk.set_appearance_mode(mode)
        if isinstance(self.current_frame, DashboardFrame):
            self.current_frame._render_charts()

    def show_frame_by_name(self, frame_class_name: str) -> None:
        """Show a frame by its class name string."""
        frame_map = {
            "HomeFrame": HomeFrame,
            "AboutFrame": AboutFrame,
            "LoginFrame": LoginFrame,
            "DashboardFrame": DashboardFrame,
            "PatientEntryFrame": PatientEntryFrame,
            "SearchFrame": SearchFrame,
        }

        frame_class = frame_map.get(frame_class_name)
        if frame_class is None:
            logger.error("Unknown frame: %s", frame_class_name)
            return

        if not self.is_logged_in and frame_class in (
            DashboardFrame, PatientEntryFrame, SearchFrame,
        ):
            messagebox.showwarning("Access Denied", "Please login first.")
            return self.show_frame_by_name("LoginFrame")

        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = frame_class(master=self.main_frame, controller=self)
        self.current_frame.pack(fill="both", expand=True)

    def _logout_action(self) -> None:
        self.is_logged_in = False
        self.current_user_role = None
        self.update_nav_buttons()
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        self.show_frame_by_name("HomeFrame")
