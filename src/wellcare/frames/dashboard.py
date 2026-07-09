"""
Dashboard screen with analytics and charts for admin users.
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.wellcare.config import (
    AUTO_REFRESH_INTERVAL_MS,
    COLOR_DARK_BG,
    COLOR_LIGHT_BG,
    COLOR_WARNING,
)


class DashboardFrame(ctk.CTkFrame):
    """Analytics dashboard with KPI cards and dynamic charts."""

    def __init__(self, master, controller) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._chart_view = "Demographics View"
        self._build_ui()

    def _build_ui(self) -> None:
        if self.controller.current_user_role != "admin":
            ctk.CTkLabel(
                self,
                text="Unauthorized: Admins Only",
                text_color="red",
                font=("", 20),
            ).pack()
            return

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            header_frame,
            text="Clinic Analytics Dashboard",
            font=("Courier New", 40, "bold"),
            text_color="#1e3c72",
        ).grid(row=0, column=1)

        self.chart_view_var = ctk.StringVar(value="Demographics View")
        view_menu = ctk.CTkOptionMenu(
            header_frame,
            variable=self.chart_view_var,
            values=["Demographics View", "Medical View", "Trend & History View"],
            command=self._render_charts,
        )
        view_menu.grid(row=0, column=2, sticky="e", padx=(20, 100))

        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            command=self._render_charts,
            fg_color="#388e3c",
            hover_color="#2e7d32",
        ).grid(row=0, column=2, sticky="e", padx=20)

        self.kpi_frame = ctk.CTkFrame(self, fg_color="#1e85da", corner_radius=10)
        self.kpi_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=10,
            ipady=10,
            ipadx=40,
        )

        self.chart_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_container.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=(10, 30),
            padx=20,
            sticky="nsew",
        )

        ctk.CTkLabel(
            self,
            text="Graphical Representation",
            font=("Roboto", 24, "bold"),
            text_color="#1e3c72",
        ).grid(row=2, column=0, columnspan=2, pady=(30, 0))

        self._render_charts()
        self._auto_refresh()

    def _render_charts(self, _choice: str | None = None) -> None:
        for w in self.kpi_frame.winfo_children():
            w.destroy()
        for w in self.chart_container.winfo_children():
            w.destroy()

        stats = self.controller.db.get_dashboard_stats()

        # KPI Layout
        self.kpi_frame.grid_columnconfigure((0, 1), weight=1)

        total_card = ctk.CTkFrame(self.kpi_frame, fg_color="transparent")
        total_card.grid(row=0, column=0, padx=40, pady=10)
        ctk.CTkLabel(
            total_card,
            text="Total Patients",
            font=("Roboto", 18),
            text_color="white",
        ).pack()
        ctk.CTkLabel(
            total_card,
            text=str(stats["total"]),
            font=("Roboto", 45, "bold"),
            text_color="white",
        ).pack()

        today_card = ctk.CTkFrame(self.kpi_frame, fg_color="transparent")
        today_card.grid(row=0, column=1, padx=40, pady=10)
        ctk.CTkLabel(
            today_card,
            text="New Patients (Today)",
            font=("Roboto", 18),
            text_color="white",
        ).pack()
        ctk.CTkLabel(
            today_card,
            text=str(stats["today"]),
            font=("Roboto", 45, "bold"),
            text_color=COLOR_WARNING,
        ).pack()

        if stats["total"] == 0:
            ctk.CTkLabel(
                self.chart_container,
                text="No patients in database yet.",
                font=("Roboto", 18),
            ).pack(pady=100)
            return

        fig = None
        sns.set_theme(style="whitegrid")
        current_view = self.chart_view_var.get()

        bg_col = COLOR_DARK_BG if ctk.get_appearance_mode() == "Dark" else COLOR_LIGHT_BG
        text_col = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        plt.rcParams.update({"text.color": text_col, "axes.labelcolor": text_col})

        if current_view == "Demographics View":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor=bg_col)
            fig.tight_layout(pad=3.0)

            valid_genders = [
                (g[0] if g[0] not in ("", "Select") else "Unknown", g[1]) for g in stats["genders"]
            ]
            labels1 = [item[0] for item in valid_genders]
            sizes1 = [item[1] for item in valid_genders]
            if sizes1:
                colors = sns.color_palette("pastel")[0 : len(sizes1)]
                ax1.pie(sizes1, labels=labels1, autopct="%1.1f%%", startangle=90, colors=colors)
                ax1.set_title("Patient Demographics")
                ax1.axis("equal")

            age_groups: dict[str, int] = {"0-18": 0, "19-35": 0, "36-50": 0, "51+": 0}
            for age_str in stats.get("ages", []):
                try:
                    a = int(age_str)
                    if a <= 18:
                        age_groups["0-18"] += 1
                    elif a <= 35:
                        age_groups["19-35"] += 1
                    elif a <= 50:
                        age_groups["36-50"] += 1
                    else:
                        age_groups["51+"] += 1
                except (ValueError, TypeError):
                    pass
            if any(age_groups.values()):
                sns.barplot(
                    x=list(age_groups.keys()),
                    y=list(age_groups.values()),
                    ax=ax2,
                    palette="viridis",
                )
                ax2.set_title("Age Categories")
                ax2.set_ylabel("Count")

        elif current_view == "Medical View":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor=bg_col)
            fig.tight_layout(pad=3.0)

            valid_bloods = [
                (b[0] if b[0] not in ("", "Select") else "Unk", b[1]) for b in stats["blood_groups"]
            ]
            labels2 = [item[0] for item in valid_bloods]
            values2 = [item[1] for item in valid_bloods]
            if values2:
                sns.barplot(x=labels2, y=values2, ax=ax1, palette="magma")
                ax1.set_title("Blood Group Distribution")
                ax1.set_ylabel("Count")

            top_symp = self.controller.db.get_symptom_frequencies(5)
            if top_symp:
                sns.barplot(
                    x=[x[0].capitalize() for x in top_symp],
                    y=[x[1] for x in top_symp],
                    ax=ax2,
                    palette="rocket",
                )
                ax2.set_title("Top 5 Report Keywords")
                ax2.set_ylabel("Frequency")
            else:
                ax2.text(0.5, 0.5, "No Symptom Data", ha="center", va="center", fontsize=12)
                ax2.set_axis_off()

        elif current_view == "Trend & History View":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor=bg_col)
            fig.tight_layout(pad=3.0)

            if stats["trends"]:
                dates = [t[0] for t in stats["trends"]]
                counts = [t[1] for t in stats["trends"]]
                sns.lineplot(x=dates, y=counts, marker="o", ax=ax1, color="#1e85da")
                ax1.set_title("Registration Trends (Last 7 Days)")
                ax1.set_ylabel("New Patients")
                plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment="right")
            else:
                ax1.text(0.5, 0.5, "No Trend Data", ha="center", va="center")

            recent_text = "Recent Registrations:\n" + ("-" * 30) + "\n"
            for r in stats["recent"]:
                recent_text += f"ID: {r[0]} | {r[1]} {r[2]} | {r[3]}\n"

            ax2.text(
                0.1,
                0.9,
                recent_text,
                ha="left",
                va="top",
                fontname="Courier New",
                fontsize=10,
                transform=ax2.transAxes,
            )
            ax2.set_title("Last 5 Patients")
            ax2.set_axis_off()

        if fig:
            for ax in fig.axes:
                ax.set_facecolor(bg_col)
                ax.tick_params(colors=text_col)

            canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

    def _auto_refresh(self) -> None:
        if self.controller.current_frame is self:
            self._render_charts()
            self.after(AUTO_REFRESH_INTERVAL_MS, self._auto_refresh)
