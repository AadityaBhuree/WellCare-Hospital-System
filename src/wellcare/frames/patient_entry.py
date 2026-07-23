from typing import Any, cast

import customtkinter as ctk
from src.wellcare.logger import logger
from src.wellcare.utils.pdf import generate_prescription
from src.wellcare.utils.validators import validate_patient_input


class PatientEntryFrame(ctk.CTkFrame):
    """Form to enter, validate, and save new patient records."""

    def __init__(self, master: Any, controller: Any) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="Customer Details",
            font=("", 28, "bold"),
        ).grid(pady=(20, 25), columnspan=2, row=0)

        self.status_label = ctk.CTkLabel(self, text="", font=("Roboto", 16, "bold"))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

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
        row_idx = 2

        for field in fields:
            label_text, var_name, widget_type = field[0], field[1], field[2]
            ctk.CTkLabel(
                self,
                text=f"{label_text}   -",
                font=("Roboto", 20),
                text_color="#3D3D3D",
            ).grid(row=row_idx, column=0, padx=100, pady=10, sticky="e")

            if widget_type == ctk.CTkComboBox:
                values = field[3] if len(field) > 3 else []
                widget = widget_type(
                    self,
                    values=values,
                    border_color="#dddddd",
                    width=250,
                )
                widget.set("Select Age" if label_text == "Age" else "Select")
            elif widget_type == ctk.CTkTextbox:
                widget = widget_type(
                    self,
                    border_color="#b1acac",
                    width=250,
                    height=80,
                    border_width=1,
                )
            else:
                widget = widget_type(
                    self,
                    border_color="#dddddd",
                    placeholder_text=f"Enter {label_text}",
                    width=250,
                    border_width=1,
                )

            widget.grid(row=row_idx, column=1, padx=10, pady=10, sticky="w")
            self.inputs[var_name] = widget
            row_idx += 1

        ctk.CTkButton(
            self,
            text="Clear",
            command=self._clear_entries,
            text_color="#e9e9e9",
            fg_color="#fa4c4c",
            hover_color="#e63636",
        ).grid(row=row_idx, column=0, padx=30, pady=30, sticky="e")

        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.grid(row=row_idx, column=1, padx=30, pady=30, sticky="w")

        ctk.CTkButton(
            btn_container,
            text="Save Only",
            command=self._save_action,
            text_color="#e9e9e9",
            fg_color="#52bb6c",
            hover_color="#447c3c",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_container,
            text="Save & Print PDF",
            command=self._save_and_print_action,
            text_color="#e9e9e9",
            fg_color="#374fb9",
            hover_color="#2a3c8e",
        ).pack(side="left", padx=5)

    def _display_status(self, message: str, color: str = "red") -> None:
        self.status_label.configure(text=message, text_color=color)
        self.after(4000, lambda: self.status_label.configure(text=""))

    def _get_val(self, key: str) -> str:
        widget = self.inputs[key]
        if isinstance(widget, ctk.CTkTextbox):
            return cast(str, widget.get("1.0", "end-1c")).strip()
        return cast(str, widget.get()).strip()

    def _save_action(self) -> None:
        vals = {k: self._get_val(k) for k in self.inputs}

        if not vals["first_name"] or not vals["last_name"] or not vals["mobile"]:
            self._display_status("First Name, Last Name, and Mobile are required.", "red")
            return

        err = validate_patient_input(vals["mobile"], vals["email"], vals["weight"], vals["age"])
        if err:
            self._display_status(err, "red")
            return

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
            success = self.controller.db.add_patient(data)
            if success:
                self._display_status("Patient Record Added Successfully!", "green")
                self._clear_entries()
                self.controller.refresh_dashboard_if_open()
            else:
                self._display_status("Failed to add record.", "red")
        else:
            self._display_status("Database is unavailable.", "red")

    def _save_and_print_action(self) -> None:
        first = self._get_val("first_name")
        last = self._get_val("last_name")
        age = self._get_val("age")
        mobile = self._get_val("mobile")

        if not first or not last or not mobile:
            self._display_status("Required elements missing.", "red")
            return

        self._save_action()
        if first:
            result = generate_prescription(first, last, age, mobile)
            if result:
                logger.info("PDF saved to: %s", result)
            else:
                self._display_status("Saved DB, but PDF failed.", "red")

    def _clear_entries(self) -> None:
        for k, v in self.inputs.items():
            if isinstance(v, ctk.CTkComboBox):
                v.set("Select Age" if k == "age" else "Select")
            elif isinstance(v, ctk.CTkTextbox):
                v.delete("1.0", "end")
            else:
                v.delete(0, "end")
