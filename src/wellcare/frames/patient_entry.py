"""Patient entry form for creating and saving patient records with PDF generation."""

from typing import Any, cast

import customtkinter as ctk
from src.wellcare.logger import logger
from src.wellcare.ui import Theme, ToastNotification
from src.wellcare.utils.pdf import generate_prescription
from src.wellcare.utils.validators import validate_patient_input


class PatientEntryFrame(ctk.CTkFrame):
    """Form to enter, validate, and save new patient records."""

    def __init__(self, master: Any, controller: Any) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.editing_patient_id: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="Patient Details & Registration",
            font=Theme.FONT_HEADING,
            text_color=Theme.PRIMARY,
        ).grid(pady=(15, 10), columnspan=2, row=0)

        # Lookup/Edit Bar
        edit_bar = ctk.CTkFrame(self, fg_color="transparent")
        edit_bar.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        self.edit_id_entry = ctk.CTkEntry(
            edit_bar, placeholder_text="Patient ID to Edit", width=140, height=32
        )
        self.edit_id_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            edit_bar,
            text="Load Patient",
            command=self._load_patient_for_edit,
            fg_color=Theme.PRIMARY_ACCENT,
            height=32,
            width=100,
        ).pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(self, text="", font=Theme.FONT_BODY_BOLD)
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        fields: list[tuple[str, str, Any, list[str]] | tuple[str, str, Any]] = [
            ("First Name", "first_name", ctk.CTkEntry),
            ("Last Name", "last_name", ctk.CTkEntry),
            ("Age", "age", ctk.CTkComboBox, [str(i) for i in range(1, 121)]),
            ("Gender", "gender", ctk.CTkComboBox, ["Male", "Female", "Other"]),
            (
                "Blood Group",
                "blood",
                ctk.CTkComboBox,
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            ),
            ("Weight (KG)", "weight", ctk.CTkEntry),
            ("Symptoms", "symptoms", ctk.CTkTextbox),
            ("Address", "address", ctk.CTkTextbox),
            ("Pincode", "pincode", ctk.CTkEntry),
            ("Email ID", "email", ctk.CTkEntry),
            ("Mobile No", "mobile", ctk.CTkEntry),
        ]

        self.inputs: dict[str, Any] = {}
        row_idx = 3

        for field in fields:
            label_text, var_name, widget_type = field[0], field[1], field[2]
            ctk.CTkLabel(
                self,
                text=f"{label_text}   -",
                font=Theme.FONT_BODY_BOLD,
                text_color=Theme.TEXT_PRIMARY_LIGHT,
            ).grid(row=row_idx, column=0, padx=100, pady=8, sticky="e")

            if widget_type == ctk.CTkComboBox:
                values = field[3] if len(field) > 3 else []
                widget = widget_type(
                    self,
                    values=values,
                    border_color=Theme.BORDER_LIGHT,
                    width=250,
                )
                widget.set("Select Age" if label_text == "Age" else "Select")
            elif widget_type == ctk.CTkTextbox:
                widget = widget_type(
                    self,
                    border_color=Theme.BORDER_LIGHT,
                    width=250,
                    height=70,
                    border_width=1,
                )
            else:
                widget = widget_type(
                    self,
                    border_color=Theme.BORDER_LIGHT,
                    placeholder_text=f"Enter {label_text}",
                    width=250,
                    border_width=1,
                )

            widget.grid(row=row_idx, column=1, padx=10, pady=8, sticky="w")
            self.inputs[var_name] = widget
            row_idx += 1

        ctk.CTkButton(
            self,
            text="Clear",
            command=self._clear_entries,
            text_color="#e9e9e9",
            fg_color=Theme.DANGER,
            hover_color=Theme.DANGER_HOVER,
        ).grid(row=row_idx, column=0, padx=30, pady=20, sticky="e")

        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.grid(row=row_idx, column=1, padx=30, pady=20, sticky="w")

        ctk.CTkButton(
            btn_container,
            text="Save Record",
            command=self._save_action,
            text_color="#e9e9e9",
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_container,
            text="Save & Print PDF",
            command=self._save_and_print_action,
            text_color="#e9e9e9",
            fg_color=Theme.PRIMARY_ACCENT,
            hover_color=Theme.PRIMARY_LIGHT,
        ).pack(side="left", padx=5)

    def _display_status(self, message: str, color: str = "red") -> None:
        self.status_label.configure(text=message, text_color=color)
        self.after(4000, lambda: self.status_label.configure(text=""))

    def _get_val(self, key: str) -> str:
        widget = self.inputs[key]
        if isinstance(widget, ctk.CTkTextbox):
            return cast(str, widget.get("1.0", "end-1c")).strip()
        return cast(str, widget.get()).strip()

    def _load_patient_for_edit(self) -> None:
        pid_str = self.edit_id_entry.get().strip()
        if not pid_str.isdigit():
            self._display_status("Enter a valid numeric Patient ID.", "red")
            return

        patient = self.controller.db.get_patient_by_id(int(pid_str))
        if not patient:
            self._display_status(f"Patient ID #{pid_str} not found.", "red")
            return

        self.editing_patient_id = patient.id
        self._clear_entries(keep_edit_id=True)

        self.inputs["first_name"].insert(0, patient.first_name)
        self.inputs["last_name"].insert(0, patient.last_name)
        self.inputs["age"].set(str(patient.age) if patient.age > 0 else "Select Age")
        self.inputs["gender"].set(patient.gender if patient.gender else "Select")
        self.inputs["blood"].set(patient.blood_group if patient.blood_group else "Select")
        self.inputs["weight"].insert(0, str(patient.weight) if patient.weight > 0 else "")
        self.inputs["symptoms"].insert("1.0", patient.symptoms)
        self.inputs["address"].insert("1.0", patient.address)
        self.inputs["pincode"].insert(0, patient.pincode)
        self.inputs["email"].insert(0, patient.email)
        self.inputs["mobile"].insert(0, patient.mobile)

        self._display_status(f"Loaded Patient #{patient.id} for editing.", "green")

    def _save_action(self) -> bool:
        vals = {k: self._get_val(k) for k in self.inputs}

        if not vals["first_name"] or not vals["last_name"] or not vals["mobile"]:
            self._display_status("First Name, Last Name, and Mobile are required.", "red")
            return False

        err = validate_patient_input(vals["mobile"], vals["email"], vals["weight"], vals["age"])
        if err:
            self._display_status(err, "red")
            return False

        if self.controller.db.conn:
            data = (
                vals["first_name"],
                vals["last_name"],
                vals["age"],
                vals["gender"],
                vals["blood"],
                vals["weight"],
                vals["mobile"],
                vals["email"],
                vals["address"],
                vals["pincode"],
                vals["symptoms"],
            )

            if self.editing_patient_id is not None:
                success = self.controller.db.update_patient(self.editing_patient_id, data)
                msg = f"Patient #{self.editing_patient_id} Updated Successfully!"
                err_msg = "Failed to update record."
            else:
                success = self.controller.db.add_patient(data)
                msg = "Patient Record Added Successfully!"
                err_msg = "Failed to add record."

            if success:
                self._display_status(msg, "green")
                ToastNotification(self.controller, msg, toast_type="success")
                self._clear_entries()
                self.controller.refresh_dashboard_if_open()
                return True

            self._display_status(err_msg, "red")
            return False


        self._display_status("Database is unavailable.", "red")
        return False

    def _save_and_print_action(self) -> None:
        first = self._get_val("first_name")
        last = self._get_val("last_name")
        age = self._get_val("age")
        mobile = self._get_val("mobile")

        if not first or not last or not mobile:
            self._display_status("Required elements missing.", "red")
            return

        save_success = self._save_action()
        if save_success:
            result = generate_prescription(first, last, age, mobile)
            if result:
                logger.info("PDF saved to: %s", result)
                ToastNotification(
                    self.controller,
                    "PDF Prescription generated successfully!",
                    toast_type="info",
                )
            else:
                self._display_status("Saved DB, but PDF failed.", "red")

    def _clear_entries(self, keep_edit_id: bool = False) -> None:
        if not keep_edit_id:
            self.editing_patient_id = None
            if hasattr(self, "edit_id_entry"):
                self.edit_id_entry.delete(0, "end")

        for k, v in self.inputs.items():
            if isinstance(v, ctk.CTkComboBox):
                v.set("Select Age" if k == "age" else "Select")
            elif isinstance(v, ctk.CTkTextbox):
                v.delete("1.0", "end")
            else:
                v.delete(0, "end")

