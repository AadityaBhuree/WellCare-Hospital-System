"""Medical Records and Consultation history frame for WellCare Hospital System."""

from tkinter import messagebox
from typing import Any

import customtkinter as ctk
from src.wellcare.ui import Theme, ToastNotification


class MedicalRecordsFrame(ctk.CTkFrame):
    """Frame for recording consultations and viewing patient medical history."""

    def __init__(self, master: Any, controller: Any) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self._build_ui()
        self.load_records()

    def _build_ui(self) -> None:
        # Header
        ctk.CTkLabel(
            self,
            text="📋 Patient Medical Consultation & History",
            font=Theme.FONT_HEADING,
            text_color=Theme.PRIMARY,
        ).grid(row=0, column=0, columnspan=2, pady=(20, 15))

        # Left Column: Add Consultation Record Form
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
            text="Add Consultation Entry",
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.PRIMARY_ACCENT,
        ).pack(anchor="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(form_card, text="Patient ID:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.patient_id_entry = ctk.CTkEntry(form_card, placeholder_text="e.g. 1", height=34)
        self.patient_id_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Attending Doctor:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.doctor_entry = ctk.CTkEntry(
            form_card, placeholder_text="e.g. Dr. A. Sharma", height=34
        )
        self.doctor_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Diagnosis:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.diagnosis_entry = ctk.CTkEntry(
            form_card, placeholder_text="e.g. Acute Bronchitis", height=34
        )
        self.diagnosis_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Treatment / Prescription:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.treatment_entry = ctk.CTkEntry(
            form_card, placeholder_text="e.g. Amoxicillin 500mg, Rest", height=34
        )
        self.treatment_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Clinical Notes:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.notes_entry = ctk.CTkEntry(
            form_card, placeholder_text="e.g. Follow-up in 7 days", height=34
        )
        self.notes_entry.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            form_card,
            text="💾 Save Medical Record",
            command=self._save_record_action,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.FONT_BODY_BOLD,
            height=38,
        ).pack(fill="x", padx=15, pady=(0, 20))

        # Right Column: Patient History Timeline
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
            text="Patient Medical History Timeline",
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.PRIMARY_ACCENT,
        ).pack(side="left")

        ctk.CTkButton(
            filter_frame,
            text="🔄 Refresh",
            width=80,
            command=self.load_records,
            fg_color=Theme.PRIMARY_ACCENT,
            height=30,
        ).pack(side="right")

        self.list_box = ctk.CTkTextbox(
            list_card,
            font=Theme.FONT_MONO,
            height=380,
        )
        self.list_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def load_records(self) -> None:
        """Fetch medical records and format timeline."""
        self.list_box.configure(state="normal")
        self.list_box.delete("1.0", "end")

        records = self.controller.db.get_patient_medical_history()
        if records:
            h = (
                f"{'Rec#':<5} | {'Patient Name':<18} | {'Doctor':<16} | "
                f"{'Diagnosis':<16} | {'Treatment'}\n"
            )
            self.list_box.insert("end", h + ("─" * 80) + "\n")
            for r in records:
                rid, _pid, pname, doc, diag, treat, _notes, _vdate = r
                pname_str = pname or "Unknown"
                line = (
                    f"{rid:<5} | {pname_str[:18]:<18} | {doc[:16]:<16} | "
                    f"{diag[:16]:<16} | {treat}\n"
                )
                self.list_box.insert("end", line)
        else:
            self.list_box.insert("end", "No medical consultation records found.")

        self.list_box.configure(state="disabled")

    def _save_record_action(self) -> None:
        pid_str = self.patient_id_entry.get().strip()
        doc = self.doctor_entry.get().strip()
        diag = self.diagnosis_entry.get().strip()
        treat = self.treatment_entry.get().strip()
        notes = self.notes_entry.get().strip()

        if not pid_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric Patient ID.")
            return

        if not doc or not diag or not treat:
            messagebox.showerror(
                "Error", "Attending Doctor, Diagnosis, and Treatment fields are required!"
            )
            return

        patient = self.controller.db.get_patient_by_id(int(pid_str))
        if not patient:
            messagebox.showerror("Error", f"Patient ID {pid_str} not found in database.")
            return

        rec_id = self.controller.db.add_medical_record(
            patient_id=int(pid_str),
            doctor_name=doc,
            diagnosis=diag,
            treatment=treat,
            notes=notes,
        )

        if rec_id:
            ToastNotification(
                self.controller,
                f"Medical Record #{rec_id} saved for {patient.full_name}!",
                toast_type="success",
            )
            self.patient_id_entry.delete(0, "end")
            self.doctor_entry.delete(0, "end")
            self.diagnosis_entry.delete(0, "end")
            self.treatment_entry.delete(0, "end")
            self.notes_entry.delete(0, "end")
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to save medical record.")
