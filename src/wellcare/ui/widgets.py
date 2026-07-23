"""Custom reusable UI widgets for WellCare Hospital System."""

from typing import Any, cast


import customtkinter as ctk
from src.wellcare.ui.theme import Theme


class ToastNotification(ctk.CTkFrame):
    """Non-blocking slide-in toast notification banner."""

    def __init__(
        self,
        master: Any,
        message: str,
        toast_type: str = "info",  # "success" | "error" | "warning" | "info"
        duration_ms: int = 3500,
    ) -> None:
        color_map = {
            "success": (Theme.SUCCESS, "#ffffff"),
            "error": (Theme.DANGER, "#ffffff"),
            "warning": (Theme.WARNING, "#0f172a"),
            "info": (Theme.INFO, "#ffffff"),
        }
        bg_color, text_color = color_map.get(toast_type, (Theme.INFO, "#ffffff"))

        super().__init__(
            master,
            fg_color=bg_color,
            corner_radius=Theme.RADIUS_BUTTON,
        )
        self._message = message

        icon_map = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "💡",
        }
        icon = icon_map.get(toast_type, "💡")

        self.label = ctk.CTkLabel(
            self,
            text=f"{icon}  {message}",
            font=Theme.FONT_BODY_BOLD,
            text_color=text_color,
            padx=Theme.PAD_MD,
            pady=Theme.PAD_SM,
        )
        self.label.pack(fill="both", expand=True)

        # Place toast at bottom right of master window
        self.place(relx=0.98, rely=0.95, anchor="se")
        self.after(duration_ms, self._dismiss)

    def _dismiss(self) -> None:
        self.destroy()


class KPICard(ctk.CTkFrame):
    """Elevated metric card displaying key operational indicators."""

    def __init__(
        self,
        master: Any,
        title: str,
        value: str,
        icon: str = "📊",
        accent_color: str = Theme.PRIMARY_ACCENT,
        subtitle: str = "",
    ) -> None:
        super().__init__(
            master,
            fg_color=Theme.CARD_BG_LIGHT,
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
        )
        self.grid_columnconfigure(0, weight=1)

        # Header row with Icon + Title
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=Theme.PAD_MD, pady=(Theme.PAD_MD, 4))

        ctk.CTkLabel(
            top_frame,
            text=icon,
            font=("Segoe UI", 22),
        ).pack(side="left", padx=(0, Theme.PAD_SM))

        ctk.CTkLabel(
            top_frame,
            text=title,
            font=Theme.FONT_CAPTION,
            text_color=Theme.TEXT_SECONDARY_LIGHT,
        ).pack(side="left")

        # Metric value
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=Theme.FONT_DISPLAY,
            text_color=accent_color,
        )
        self.value_label.pack(anchor="w", padx=Theme.PAD_MD, pady=(0, 4))

        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=Theme.FONT_CAPTION,
                text_color=Theme.TEXT_SECONDARY_LIGHT,
            ).pack(anchor="w", padx=Theme.PAD_MD, pady=(0, Theme.PAD_MD))

    def update_value(self, new_value: str) -> None:
        self.value_label.configure(text=new_value)


class StatusBadge(ctk.CTkFrame):
    """Colored status pill badge component."""

    def __init__(
        self,
        master: Any,
        text: str,
        status_type: str = "info",
    ) -> None:
        color_map = {
            "success": (Theme.SUCCESS, "#ffffff"),
            "error": (Theme.DANGER, "#ffffff"),
            "warning": (Theme.WARNING, "#0f172a"),
            "info": (Theme.INFO, "#ffffff"),
        }
        bg, fg = color_map.get(status_type, (Theme.INFO, "#ffffff"))
        super().__init__(master, fg_color=bg, corner_radius=Theme.RADIUS_PILL)

        ctk.CTkLabel(
            self,
            text=text,
            font=Theme.FONT_CAPTION,
            text_color=fg,
            padx=10,
            pady=2,
        ).pack()


class FormField(ctk.CTkFrame):
    """Standardized labeled form field with optional error state."""

    def __init__(
        self,
        master: Any,
        label: str,
        placeholder: str = "",
        widget_type: str = "entry",  # "entry" | "combo" | "textbox"
        values: list[str] | None = None,
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=label,
            font=Theme.FONT_BODY_BOLD,
            text_color=Theme.TEXT_PRIMARY_LIGHT,
        ).pack(anchor="w", pady=(0, Theme.PAD_XS))

        self.widget_type = widget_type
        if widget_type == "combo":
            self.input_widget: Any = ctk.CTkComboBox(
                self,
                values=values or [],
                border_color=Theme.BORDER_LIGHT,
                height=36,
            )
            if values:
                self.input_widget.set(placeholder or values[0])
        elif widget_type == "textbox":
            self.input_widget = ctk.CTkTextbox(
                self,
                border_color=Theme.BORDER_LIGHT,
                border_width=1,
                height=70,
            )
        else:
            self.input_widget = ctk.CTkEntry(
                self,
                placeholder_text=placeholder,
                border_color=Theme.BORDER_LIGHT,
                height=36,
            )

        self.input_widget.pack(fill="x", expand=True)

        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=Theme.FONT_CAPTION,
            text_color=Theme.DANGER,
        )
        self.error_label.pack(anchor="w", pady=(2, 0))

    def get_value(self) -> str:
        if self.widget_type == "textbox":
            return cast(str, self.input_widget.get("1.0", "end-1c")).strip()
        return cast(str, self.input_widget.get()).strip()


    def set_error(self, message: str) -> None:
        self.error_label.configure(text=message)
        if message:
            self.input_widget.configure(border_color=Theme.DANGER)
        else:
            self.input_widget.configure(border_color=Theme.BORDER_LIGHT)

    def clear(self) -> None:
        self.set_error("")

        if self.widget_type == "combo":
            pass
        elif self.widget_type == "textbox":
            self.input_widget.delete("1.0", "end")
        else:
            self.input_widget.delete(0, "end")
