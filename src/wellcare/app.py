"""
Central application controller for WellCare Hospital Management System.

Implements the Controller-Frame pattern to manage navigation and global state.
"""

import datetime
from tkinter import messagebox
from typing import Any

import customtkinter as ctk
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
    AppointmentsFrame,
    BillingFrame,
    DashboardFrame,
    DoctorsFrame,
    HomeFrame,
    LoginFrame,
    MedicalRecordsFrame,
    PatientEntryFrame,
    SearchFrame,
)
from src.wellcare.logger import logger
from src.wellcare.utils.image_loader import load_ctk_image


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
        self.current_frame: ctk.CTkFrame | None = None

        self._build_ui()
        self.update_nav_buttons()
        self.show_frame_by_name("HomeFrame")

    def _build_ui(self) -> None:
        # ── Header Frame ─────────────────────────────────────
        # ── Header Frame ─────────────────────────────────────
        self.upper_frame = ctk.CTkFrame(self, fg_color="#1e3c72", height=95, corner_radius=0)
        self.upper_frame.pack(side="top", fill="x")
        self.upper_frame.pack_propagate(False)

        logo_image = load_ctk_image(ASSETS_DIR / "wellcare.png", size=(75, 75))
        if logo_image:
            self.logo_label = ctk.CTkLabel(
                self.upper_frame,
                image=logo_image,
                text="",
            )
            self.logo_label.pack(side="left", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(
            self.upper_frame,
            text="WellCare Hospital Management System",
            font=("Segoe UI", 24, "bold"),
            text_color="white",
        )
        self.title_label.pack(side="left", padx=10, pady=10)

        self.date_label = ctk.CTkLabel(
            self.upper_frame,
            text="",
            font=("Segoe UI", 13, "bold"),
            text_color="#e0e8f5",
        )
        self.date_label.pack(side="right", padx=25, pady=10)
        self._update_time()

        # ── Navigation Frame ─────────────────────────────────
        self.button_frame = ctk.CTkFrame(self, fg_color="#2a5298", height=50, corner_radius=0)
        self.button_frame.pack(side="top", fill="x")

        # Dark Mode Switcher
        self.mode_switch = ctk.CTkSwitch(
            self.button_frame,
            text="Dark Mode",
            command=self._toggle_mode,
            text_color="white",
            font=("Segoe UI", 12, "bold"),
            progress_color="#1e3c72",
        )
        self.mode_switch.grid(column=0, row=0, padx=15, pady=10)

        nav_args = {
            "font": ("Segoe UI", 13, "bold"),
            "fg_color": "transparent",
            "text_color": "white",
            "hover_color": "#1e85da",
            "cursor": "hand2",
        }

        self.home_screen_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("HomeFrame"),
            text="HOME",
            **nav_args,
        )
        self.about_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("AboutFrame"),
            text="ABOUT",
            **nav_args,
        )
        self.login_screen_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("LoginFrame"),
            text="LOGIN",
            **nav_args,
        )
        self.dashboard_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("DashboardFrame"),
            text="DASHBOARD",
            **nav_args,
        )
        self.new_patient_record_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("PatientEntryFrame"),
            text="NEW PATIENT",
            **nav_args,
        )
        self.search_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("SearchFrame"),
            text="SEARCH",
            **nav_args,
        )
        self.appointments_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("AppointmentsFrame"),
            text="APPOINTMENTS",
            **nav_args,
        )
        self.doctors_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("DoctorsFrame"),
            text="DOCTORS",
            **nav_args,
        )
        self.billing_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("BillingFrame"),
            text="BILLING",
            **nav_args,
        )
        self.medical_records_button = ctk.CTkButton(
            self.button_frame,
            command=lambda: self.show_frame_by_name("MedicalRecordsFrame"),
            text="RECORDS",
            **nav_args,
        )
        self.logout_button = ctk.CTkButton(
            self.button_frame,
            command=self._logout_action,
            text="LOGOUT",
            fg_color="#e25353",
            font=("Segoe UI", 13, "bold"),
            hover_color="#c44545",
            cursor="hand2",
        )

        # ── Content Area ──────────────────────────────────────
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("#ffffff", "#1b263b"),
            corner_radius=0,
        )
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def _update_time(self) -> None:
        self.date_label.configure(
            text=datetime.datetime.now().strftime("Date: %d/%m/%Y \nTime: %H:%M:%S"),
        )
        self.after(1000, self._update_time)

    def refresh_dashboard_if_open(self) -> None:
        """Trigger chart re-rendering if the active frame is DashboardFrame."""
        if isinstance(self.current_frame, DashboardFrame):
            self.current_frame._render_charts()

    def update_nav_buttons(self) -> None:
        """Show or hide top navigation menu options based on auth state and user role."""
        # Always display HOME button at column 1
        self.home_screen_button.grid(column=1, row=0, padx=10)

        if self.is_logged_in:
            self.login_screen_button.grid_forget()
            c_idx = 2

            if self.current_user_role == "admin":
                self.dashboard_button.grid(column=c_idx, row=0, padx=10)
                c_idx += 1
            else:
                self.dashboard_button.grid_forget()

            self.new_patient_record_button.grid(column=c_idx, row=0, padx=10)
            self.search_button.grid(column=c_idx + 1, row=0, padx=10)
            self.appointments_button.grid(column=c_idx + 2, row=0, padx=10)
            self.doctors_button.grid(column=c_idx + 3, row=0, padx=10)
            self.billing_button.grid(column=c_idx + 4, row=0, padx=10)
            self.medical_records_button.grid(column=c_idx + 5, row=0, padx=10)
            self.about_button.grid(column=c_idx + 6, row=0, padx=10)
            self.logout_button.grid(column=c_idx + 7, row=0, padx=10)
        else:
            self.dashboard_button.grid_forget()
            self.new_patient_record_button.grid_forget()
            self.search_button.grid_forget()
            self.appointments_button.grid_forget()
            self.doctors_button.grid_forget()
            self.billing_button.grid_forget()
            self.medical_records_button.grid_forget()
            self.logout_button.grid_forget()

            self.about_button.grid(column=2, row=0, padx=10)
            self.login_screen_button.grid(column=3, row=0, padx=10)

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
            "AppointmentsFrame": AppointmentsFrame,
            "DoctorsFrame": DoctorsFrame,
            "BillingFrame": BillingFrame,
            "MedicalRecordsFrame": MedicalRecordsFrame,
        }

        frame_class: Any = frame_map.get(frame_class_name)

        if frame_class is None:
            logger.error("Unknown frame: %s", frame_class_name)
            return

        if not self.is_logged_in and frame_class in (
            DashboardFrame,
            PatientEntryFrame,
            SearchFrame,
            AppointmentsFrame,
            DoctorsFrame,
            BillingFrame,
            MedicalRecordsFrame,
        ):
            messagebox.showwarning("Access Denied", "Please login first.")
            return self.show_frame_by_name("LoginFrame")

        # ── Highlight Active Navigation Button ─────────────────
        nav_button_map = {
            "HomeFrame": self.home_screen_button,
            "AboutFrame": self.about_button,
            "LoginFrame": self.login_screen_button,
            "DashboardFrame": self.dashboard_button,
            "PatientEntryFrame": self.new_patient_record_button,
            "SearchFrame": self.search_button,
            "AppointmentsFrame": self.appointments_button,
            "DoctorsFrame": self.doctors_button,
            "BillingFrame": self.billing_button,
            "MedicalRecordsFrame": self.medical_records_button,
        }
        for f_name, btn in nav_button_map.items():
            if f_name == frame_class_name:
                btn.configure(fg_color="#1e3c72")
            else:
                btn.configure(fg_color="transparent")

        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame_class(master=self.main_frame, controller=self)
        self.current_frame.pack(fill="both", expand=True)

    def _logout_action(self) -> None:
        self.is_logged_in = False
        self.current_user_role = None
        self.update_nav_buttons()
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        self.show_frame_by_name("HomeFrame")
