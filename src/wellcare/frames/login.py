"""
Login screen with authentication logic.
"""

from tkinter import messagebox

import customtkinter as ctk
from src.wellcare.logger import logger
from src.wellcare.utils.auth import authenticate_user


class LoginFrame(ctk.CTkFrame):
    """Login page for authentication."""

    def __init__(self, master, controller) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="Clinic System Login",
            font=("", 28, "bold"),
        ).grid(pady=(50, 40), columnspan=2, column=0, row=0)

        ctk.CTkLabel(
            self,
            text="ID:",
            font=("Roboto", 20),
            text_color="#3D3D3D",
        ).grid(row=2, column=0, padx=10, pady=15, sticky="e")

        self.id_entry = ctk.CTkEntry(
            self,
            placeholder_text="Admin ('admin') or Staff ('staff')",
            width=250,
        )
        self.id_entry.grid(row=2, column=1, padx=10, pady=15, sticky="w")

        ctk.CTkLabel(
            self,
            text="Password:",
            font=("Roboto", 20),
            text_color="#3D3D3D",
        ).grid(row=3, column=0, padx=10, pady=15, sticky="e")

        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter Password ('123')",
            width=250,
            show="*",
        )
        self.password_entry.grid(row=3, column=1, padx=10, pady=15, sticky="w")

        ctk.CTkButton(
            self,
            text="Login",
            command=self._login_check,
            font=("Roboto", 18, "bold"),
            fg_color="#374fb9",
            hover_color="#2a3c8e",
        ).grid(row=4, column=0, padx=30, pady=40, columnspan=2)

    def _login_check(self) -> None:
        uid = self.id_entry.get().strip()
        pwd = self.password_entry.get().strip()

        role = authenticate_user(uid, pwd)

        if role == "admin":
            self.controller.is_logged_in = True
            self.controller.current_user_role = "admin"
            self.controller.update_nav_buttons()
            messagebox.showinfo(
                "Admin Login",
                "Welcome Administrator!\nFull system dashboard unlocked.",
            )
            self.controller.show_frame_by_name("HomeFrame")

        elif role == "staff":
            self.controller.is_logged_in = True
            self.controller.current_user_role = "staff"
            self.controller.update_nav_buttons()
            messagebox.showinfo(
                "Staff Login",
                "Login Successful. Redirecting to Home.",
            )
            self.controller.show_frame_by_name("HomeFrame")

        else:
            logger.warning("Failed login attempt: %s", uid)
            messagebox.showwarning("Warning", "Invalid User ID or Password!")
