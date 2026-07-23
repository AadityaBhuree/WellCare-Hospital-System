"""Login screen with authentication logic."""

from tkinter import messagebox
from typing import Any

import customtkinter as ctk
from src.wellcare.logger import logger
from src.wellcare.ui import Theme, ToastNotification
from src.wellcare.utils.auth import authenticate_user


class LoginFrame(ctk.CTkFrame):
    """Login page for authentication."""

    def __init__(self, master: Any, controller: Any) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="Clinic System Login",
            font=Theme.FONT_HEADING,
            text_color=Theme.PRIMARY,
        ).grid(pady=(50, 40), columnspan=2, column=0, row=0)

        ctk.CTkLabel(
            self,
            text="User ID:",
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_PRIMARY_LIGHT,
        ).grid(row=2, column=0, padx=10, pady=15, sticky="e")

        self.id_entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter Admin or Staff ID",
            width=250,
            height=38,
            border_color=Theme.BORDER_LIGHT,
        )
        self.id_entry.grid(row=2, column=1, padx=10, pady=15, sticky="w")

        ctk.CTkLabel(
            self,
            text="Password:",
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_PRIMARY_LIGHT,
        ).grid(row=3, column=0, padx=10, pady=15, sticky="e")

        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter Password",
            width=250,
            height=38,
            border_color=Theme.BORDER_LIGHT,
            show="*",
        )
        self.password_entry.grid(row=3, column=1, padx=10, pady=15, sticky="w")

        ctk.CTkButton(
            self,
            text="Login",
            command=self._login_check,
            font=Theme.FONT_BODY_BOLD,
            fg_color=Theme.PRIMARY_ACCENT,
            hover_color=Theme.PRIMARY_LIGHT,
            height=40,
            width=250,
            corner_radius=Theme.RADIUS_BUTTON,
        ).grid(row=4, column=0, padx=30, pady=40, columnspan=2)

    def _login_check(self) -> None:
        uid = self.id_entry.get().strip()
        pwd = self.password_entry.get().strip()

        role = authenticate_user(uid, pwd)

        if role == "admin":
            self.controller.is_logged_in = True
            self.controller.current_user_role = "admin"
            self.controller.update_nav_buttons()
            ToastNotification(
                self.controller,
                "Welcome Administrator! Full dashboard unlocked.",
                toast_type="success",
            )
            messagebox.showinfo(
                "Admin Login",
                "Welcome Administrator!\nFull system dashboard unlocked.",
            )
            self.controller.show_frame_by_name("HomeFrame")

        elif role == "staff":
            self.controller.is_logged_in = True
            self.controller.current_user_role = "staff"
            self.controller.update_nav_buttons()
            ToastNotification(
                self.controller,
                "Login Successful. Redirecting to Home.",
                toast_type="success",
            )
            messagebox.showinfo(
                "Staff Login",
                "Login Successful. Redirecting to Home.",
            )
            self.controller.show_frame_by_name("HomeFrame")

        else:
            logger.warning("Failed login attempt: %s", uid)
            ToastNotification(
                self.controller,
                "Invalid User ID or Password!",
                toast_type="error",
            )
            messagebox.showwarning("Warning", "Invalid User ID or Password!")
