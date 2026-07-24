"""Doctor directory and management frame."""

from typing import Any

import customtkinter as ctk

from src.wellcare.ui import Theme, ToastNotification
from src.wellcare.utils.validators import validate_email, validate_mobile


class DoctorsFrame(ctk.CTkFrame):
    """UI frame for viewing and managing doctor directory and schedules."""

    def __init__(self, master: Any, controller: Any) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        # Title
        ctk.CTkLabel(
            self,
            text="Doctor Directory & Schedules",
            font=Theme.FONT_HEADING,
            text_color=Theme.PRIMARY,
        ).grid(row=0, column=0, pady=20)

        # Search Bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, pady=10)

        self.spec_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Filter by Specialization (e.g. Cardiology)",
            width=320,
            height=38,
            border_color=Theme.BORDER_LIGHT,
        )
        self.spec_entry.pack(side="left", padx=10)

        ctk.CTkButton(
            search_frame,
            text="Filter",
            command=self._filter_doctors,
            fg_color=Theme.PRIMARY_ACCENT,
            hover_color=Theme.PRIMARY_LIGHT,
            height=38,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Show All",
            command=self.load_doctors,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            height=38,
        ).pack(side="left", padx=5)

        # Scrollable list container
        self.list_frame = ctk.CTkScrollableFrame(
            self,
            width=750,
            height=250,
            fg_color=Theme.CARD_BG,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
        )
        self.list_frame.grid(row=2, column=0, pady=15)

        # Add Doctor section (Admin only)
        if self.controller.current_user_role == "admin":
            add_card = ctk.CTkFrame(
                self,
                fg_color=Theme.CARD_BG,
                border_width=1,
                border_color=Theme.BORDER_LIGHT,
            )
            add_card.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

            ctk.CTkLabel(
                add_card,
                text="Register New Doctor",
                font=Theme.FONT_SUBHEADING,
                text_color=Theme.PRIMARY,
            ).pack(pady=10)

            fields_frame = ctk.CTkFrame(add_card, fg_color="transparent")
            fields_frame.pack(pady=5, padx=10)

            self.name_input = ctk.CTkEntry(
                fields_frame, placeholder_text="Doctor Name (e.g. Dr. John)", width=200
            )
            self.name_input.grid(row=0, column=0, padx=5, pady=5)

            self.spec_input = ctk.CTkEntry(
                fields_frame, placeholder_text="Specialization", width=180
            )
            self.spec_input.grid(row=0, column=1, padx=5, pady=5)

            self.phone_input = ctk.CTkEntry(
                fields_frame, placeholder_text="Phone Number", width=150
            )
            self.phone_input.grid(row=0, column=2, padx=5, pady=5)

            self.email_input = ctk.CTkEntry(
                fields_frame, placeholder_text="Email Address", width=180
            )
            self.email_input.grid(row=1, column=0, padx=5, pady=5)

            self.days_input = ctk.CTkEntry(
                fields_frame, placeholder_text="Available Days (Mon-Fri)", width=180
            )
            self.days_input.grid(row=1, column=1, padx=5, pady=5)

            ctk.CTkButton(
                fields_frame,
                text="Save Doctor",
                command=self._add_doctor_action,
                fg_color=Theme.SUCCESS,
                hover_color=Theme.SUCCESS_HOVER,
                width=140,
            ).grid(row=1, column=2, padx=5, pady=5)

    def load_doctors(self) -> None:
        """Load and display active doctors list."""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        doctors = self.controller.db.get_all_doctors(active_only=True)
        self._render_doctors(doctors)

    def _filter_doctors(self) -> None:
        spec = self.spec_entry.get().strip()
        if not spec:
            self.load_doctors()
            return
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        doctors = self.controller.db.get_doctors_by_specialization(spec)
        self._render_doctors(doctors)

    def _render_doctors(self, doctors: list[tuple[Any, ...]]) -> None:
        if not doctors:
            ctk.CTkLabel(
                self.list_frame,
                text="No doctors found matching criteria.",
                font=Theme.FONT_BODY,
                text_color=Theme.TEXT_SECONDARY,
            ).pack(pady=20)
            return

        headers = ["ID", "Name", "Specialization", "Phone", "Email", "Schedule"]
        header_frame = ctk.CTkFrame(self.list_frame, fg_color=Theme.PRIMARY, height=30)
        header_frame.pack(fill="x", pady=2)

        widths = [40, 150, 140, 110, 150, 120]
        for idx, text in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=text,
                font=Theme.FONT_BUTTON,
                text_color="#FFFFFF",
                width=widths[idx],
            ).pack(side="left", padx=2)

        for doc in doctors:
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            doc_id, name, spec, phone, email, days, _ = doc
            values = [str(doc_id), name, spec, phone or "N/A", email or "N/A", days or "N/A"]
            for idx, val in enumerate(values):
                ctk.CTkLabel(
                    row,
                    text=val,
                    font=Theme.FONT_BODY,
                    text_color=Theme.TEXT_PRIMARY,
                    width=widths[idx],
                ).pack(side="left", padx=2)

    def _add_doctor_action(self) -> None:
        name = self.name_input.get().strip()
        spec = self.spec_input.get().strip()
        phone = self.phone_input.get().strip()
        email = self.email_input.get().strip()
        days = self.days_input.get().strip() or "Mon,Tue,Wed,Thu,Fri"

        if not name or not spec:
            ToastNotification.show(
                self, "Doctor Name and Specialization are required!", is_error=True
            )
            return

        if phone and not validate_mobile(phone):
            ToastNotification.show(self, "Invalid 10-digit mobile phone number!", is_error=True)
            return

        if email and not validate_email(email):
            ToastNotification.show(self, "Invalid email address format!", is_error=True)
            return

        if self.controller.db.add_doctor(name, spec, phone, email, days):
            ToastNotification.show(self, f"Doctor {name} registered successfully!")
            self.name_input.delete(0, "end")
            self.spec_input.delete(0, "end")
            self.phone_input.delete(0, "end")
            self.email_input.delete(0, "end")
            self.days_input.delete(0, "end")
            self.load_doctors()
        else:
            ToastNotification.show(self, "Failed to register doctor into database.", is_error=True)
