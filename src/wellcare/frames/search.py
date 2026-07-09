"""
Search screen for finding and managing patient records.
"""

from tkinter import messagebox

import customtkinter as ctk


class SearchFrame(ctk.CTkFrame):
    """Search page to look up and delete patient records."""

    def __init__(self, master, controller) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self, text="Search Patient Record",
            font=("Courier New", 30, "bold"),
        ).grid(row=0, column=0, pady=30)

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter Name", width=300)
        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(
            search_frame, text="Search",
            command=self._search_action,
            fg_color="#1e85da",
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            search_frame, text="Show All",
            command=lambda: self._search_action(show_all=True),
            fg_color="#388e3c", hover_color="#2e7d32",
        ).pack(side="left", padx=10)

        # Admin: delete controls
        if self.controller.current_user_role == "admin":
            action_frame = ctk.CTkFrame(self, fg_color="transparent")
            action_frame.grid(row=2, column=0, pady=10)

            self.delete_id_entry = ctk.CTkEntry(
                action_frame, placeholder_text="Patient ID to Delete", width=150,
            )
            self.delete_id_entry.pack(side="left", padx=10)

            ctk.CTkButton(
                action_frame, text="Delete Patient",
                fg_color="red", hover_color="#8b0000",
                command=self._delete_action,
            ).pack(side="left", padx=10)

        self.result_box = ctk.CTkTextbox(
            self, width=800, height=400, font=("Courier", 14),
        )
        self.result_box.grid(row=3, column=0, pady=30)
        self.result_box.insert("1.0", "Search by entering the patient's first or last name.")
        self.result_box.configure(state="disabled")

    def _search_action(self, show_all: bool = False) -> None:
        name = self.search_entry.get().strip() if not show_all else ""
        if not name and not show_all:
            messagebox.showwarning("Warning", "Please enter a name to search.")
            return

        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")

        if self.controller.db.conn:
            records = self.controller.db.search_patient(name)
            if records:
                self.result_box.insert(
                    "end",
                    f"Found {len(records)} database records:\n" + ("=" * 50) + "\n\n",
                )
                for r in records:
                    rid = str(r[0]) if r[0] is not None else ""
                    fname = str(r[1]) if r[1] is not None else ""
                    lname = str(r[2]) if r[2] is not None else ""
                    age = str(r[3]) if r[3] is not None else ""
                    mobile = str(r[4]) if r[4] is not None else ""
                    symptoms = str(r[5]) if r[5] is not None else ""

                    self.result_box.insert(
                        "end",
                        f"ID: {rid:<4} | Name: {fname} {lname:<15} | Age: {age:<4} | Mobile: {mobile}\n"
                        f"Symptoms: {symptoms}\n{'-' * 60}\n",
                    )
            else:
                self.result_box.insert("end", "No patient found.")

        self.result_box.configure(state="disabled")

    def _delete_action(self) -> None:
        pid = self.delete_id_entry.get().strip()
        if not pid.isdigit():
            messagebox.showwarning("Error", "Please enter a valid numeric ID.")
            return

        if messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to completely delete Patient ID {pid}?",
        ):
            if self.controller.db.delete_patient(pid):
                messagebox.showinfo("Success", f"Patient ID {pid} deleted.")
                self._search_action()
                self.controller.refresh_dashboard_if_open()
            else:
                messagebox.showerror("Error", "Failed to delete patient. Ensure ID exists.")
