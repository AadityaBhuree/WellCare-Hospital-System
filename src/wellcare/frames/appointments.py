"""Appointment Scheduling frame for WellCare Hospital System."""

import datetime
from tkinter import messagebox
from typing import Any

import customtkinter as ctk
from src.wellcare.models import Appointment, AppointmentStatus
from src.wellcare.ui import Theme, ToastNotification


class AppointmentsFrame(ctk.CTkFrame):
    """Frame for scheduling and managing patient appointments."""

    def __init__(self, master: Any, controller: Any) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="📅 Appointment Management",
            font=Theme.FONT_HEADING,
            text_color=Theme.PRIMARY,
        ).grid(row=0, column=0, columnspan=2, pady=(20, 15))

        # Left Column: New Appointment Form Card
        form_card = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
        )
        form_card.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")

        ctk.CTkLabel(
            form_card,
            text="Book New Appointment",
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.PRIMARY_ACCENT,
        ).pack(anchor="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(form_card, text="Patient ID:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.patient_id_entry = ctk.CTkEntry(form_card, placeholder_text="e.g. 1", height=34)
        self.patient_id_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Doctor:", font=Theme.FONT_BODY_BOLD).pack(anchor="w", padx=15)
        self.doctor_combo = ctk.CTkComboBox(
            form_card,
            values=[
                "Dr. A. Sharma (Cardiology)",
                "Dr. B. Verma (Neurology)",
                "Dr. C. Gupta (Orthopedics)",
                "Dr. D. Mehta (Gynecology)",
            ],
            height=34,
        )
        self.doctor_combo.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Date (YYYY-MM-DD):", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.date_entry = ctk.CTkEntry(form_card, placeholder_text=today_str, height=34)
        self.date_entry.insert(0, today_str)
        self.date_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Time Slot:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.slot_combo = ctk.CTkComboBox(
            form_card,
            values=[
                "09:00 - 09:30 AM",
                "10:00 - 10:30 AM",
                "11:00 - 11:30 AM",
                "02:00 - 02:30 PM",
                "04:00 - 04:30 PM",
                "06:00 - 06:30 PM",
            ],
            height=34,
        )
        self.slot_combo.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Notes / Reason:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.notes_entry = ctk.CTkEntry(
            form_card, placeholder_text="e.g. Regular Checkup", height=34
        )
        self.notes_entry.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            form_card,
            text="Schedule Appointment",
            command=self._schedule_action,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.FONT_BODY_BOLD,
            height=38,
        ).pack(fill="x", padx=15, pady=(0, 20))

        # Right Column: Appointments List
        list_card = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
        )
        list_card.grid(row=1, column=1, padx=15, pady=10, sticky="nsew")
        list_card.grid_columnconfigure(0, weight=1)

        filter_frame = ctk.CTkFrame(list_card, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            filter_frame,
            text="Scheduled Appointments",
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.PRIMARY_ACCENT,
        ).pack(side="left")

        ctk.CTkButton(
            filter_frame,
            text="🔄 Refresh",
            width=80,
            command=self._load_appointments,
            fg_color=Theme.PRIMARY_ACCENT,
            height=30,
        ).pack(side="right")

        self.list_box = ctk.CTkTextbox(
            list_card,
            font=Theme.FONT_MONO,
            height=350,
        )
        self.list_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Action bar at bottom right
        action_bar = ctk.CTkFrame(list_card, fg_color="transparent")
        action_bar.pack(fill="x", padx=15, pady=(0, 15))

        self.status_id_entry = ctk.CTkEntry(
            action_bar, placeholder_text="Appt ID", width=90, height=32
        )
        self.status_id_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_bar,
            text="Mark Completed",
            command=lambda: self._update_status(AppointmentStatus.COMPLETED.value),
            fg_color=Theme.SUCCESS,
            height=32,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar,
            text="Cancel Appt",
            command=lambda: self._update_status(AppointmentStatus.CANCELLED.value),
            fg_color=Theme.DANGER,
            height=32,
        ).pack(side="left", padx=5)

        self._load_appointments()

    def _schedule_action(self) -> None:
        pid_str = self.patient_id_entry.get().strip()
        doc = self.doctor_combo.get().strip()
        date_str = self.date_entry.get().strip()
        slot = self.slot_combo.get().strip()
        notes = self.notes_entry.get().strip()

        if not pid_str.isdigit():
            ToastNotification(
                self.controller, "Please enter a valid numeric Patient ID.", toast_type="error"
            )
            messagebox.showerror("Error", "Please enter a valid numeric Patient ID.")
            return

        patient = self.controller.db.get_patient_by_id(int(pid_str))
        if not patient:
            ToastNotification(
                self.controller, f"Patient ID {pid_str} not found in database.", toast_type="error"
            )
            messagebox.showerror("Error", f"Patient ID {pid_str} not found.")
            return

        dept = doc.split("(")[1].replace(")", "") if "(" in doc else "General"
        appt = Appointment(
            patient_id=int(pid_str),
            doctor_name=doc.split("(")[0].strip(),
            department=dept,
            date=date_str,
            time_slot=slot,
            status=AppointmentStatus.SCHEDULED.value,
            notes=notes,
        )

        if self.controller.db.add_appointment(appt):
            ToastNotification(
                self.controller,
                f"Appointment booked for {patient.full_name}!",
                toast_type="success",
            )
            messagebox.showinfo("Success", f"Appointment booked for {patient.full_name}!")
            self.patient_id_entry.delete(0, "end")
            self.notes_entry.delete(0, "end")
            self._load_appointments()
        else:
            ToastNotification(self.controller, "Failed to book appointment.", toast_type="error")

    def _load_appointments(self) -> None:
        self.list_box.configure(state="normal")
        self.list_box.delete("1.0", "end")

        records = self.controller.db.get_appointments()
        if records:
            h1 = f"{'ID':<4} | {'Patient Name':<18} | "
            h2 = f"{'Doctor':<18} | {'Time Slot':<15} | {'Status'}\n"
            self.list_box.insert("end", h1 + h2 + ("─" * 70) + "\n")
            for r in records:
                aid, pname, doc, _dept, _date_val, slot, status, _notes = r
                line = f"{aid:<4} | {pname[:18]:<18} | {doc[:18]:<18} | {slot:<15} | {status}\n"
                self.list_box.insert("end", line)

        else:
            self.list_box.insert("end", "No appointments scheduled.")

        self.list_box.configure(state="disabled")

    def _update_status(self, new_status: str) -> None:
        aid = self.status_id_entry.get().strip()
        if not aid.isdigit():
            ToastNotification(
                self.controller, "Enter a valid numeric Appointment ID.", toast_type="warning"
            )
            return

        if self.controller.db.update_appointment_status(aid, new_status):
            ToastNotification(
                self.controller, f"Appt #{aid} marked as {new_status}.", toast_type="success"
            )
            self.status_id_entry.delete(0, "end")
            self._load_appointments()
        else:
            ToastNotification(self.controller, "Failed to update appointment.", toast_type="error")
