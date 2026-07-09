"""
Home screen frame with hospital information and service overview.
"""

import logging
import os

import customtkinter as ctk
from PIL import Image
from src.wellcare.config import ASSETS_DIR

logger = logging.getLogger(__name__)


class HomeFrame(ctk.CTkFrame):
    """Landing page with hospital info, services, doctor cards, and emergency."""

    def __init__(self, master, controller) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self) -> None:
        # ── Logo ───────────────────────────────────────────────
        try:
            logo_pil_image = Image.open(ASSETS_DIR / "wellcare.png")
            big_logo = ctk.CTkImage(
                light_image=logo_pil_image,
                dark_image=logo_pil_image,
                size=(550, 650),
            )
            logo_label = ctk.CTkLabel(self, text="", image=big_logo)
            logo_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        except Exception as exc:
            logger.debug("Could not load logo: %s", exc)

        # Hospital Name & Tagline
        ctk.CTkLabel(
            self,
            text="WellCare Hospital",
            font=("Courier New", 50, "bold"),
            text_color="#1e3c72",
        ).grid(row=2, pady=(20, 10), columnspan=2)

        ctk.CTkLabel(
            self,
            text="Providing compassionate care 24/7",
            font=("Roboto", 20, "italic"),
            text_color="#3d3d3d",
        ).grid(row=3, pady=(0, 20), columnspan=2)

        # ── Info Bar ───────────────────────────────────────────
        info_frame = ctk.CTkFrame(self, fg_color="#edf5fd", corner_radius=5)
        info_frame.grid(row=4, column=0, padx=5, pady=20, columnspan=2, sticky="ew")
        info_frame.grid_columnconfigure((0, 1, 2), weight=1)

        info_font = ("Roboto", 18, "bold")

        ctk.CTkLabel(
            info_frame,
            text="🚨 Emergency: 24/7 Available\n📞 +91-1234567890",
            font=info_font,
            text_color="#d32f2f",
            justify="left",
        ).grid(row=0, column=0, padx=20, pady=20, sticky="w")

        ctk.CTkLabel(
            info_frame,
            text="🏥 OPD Timings\n🕒 9:00 AM - 8:00 PM",
            font=info_font,
            text_color="#1976d2",
            justify="center",
        ).grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(
            info_frame,
            text="📍 Location\nCareWell Clinic, Gandhi Nagar, Nagpur",
            font=info_font,
            text_color="#388e3c",
            justify="right",
        ).grid(row=0, column=2, padx=20, pady=20, sticky="e")

        # ── Services Section ───────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Our Specialist Services",
            font=("Roboto", 28, "bold"),
            text_color="#1e3c72",
        ).grid(row=5, column=0, columnspan=2, pady=(30, 10))

        self.services_frame = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=5,
            border_width=1,
            border_color="#acb0b3",
        )
        self.services_frame.grid(row=6, column=0, padx=5, pady=10, columnspan=2, sticky="ew")
        for i in range(6):
            self.services_frame.grid_columnconfigure(i, weight=1)

        services = [
            ("❤️ Cardiac Care", "#d32f2f", self._show_cardiac_info),
            ("🧠 Neurology", "#1e85da", self._show_neuro_info),
            ("🔬 Diagnostics", "#388e3c", self._show_diagnostic_info),
            ("👶 Maternity", "#8e24aa", self._show_maternity_info),
            ("🦴 Orthopedics", "#fbc02d", self._show_ortho_info),
            ("🧑‍🔬 Pathology", "#00838f", self._show_lab_info),
        ]

        for idx, (text, color, cmd) in enumerate(services):
            ctk.CTkButton(
                self.services_frame,
                text=text,
                font=("Roboto", 14, "bold"),
                text_color=color,
                fg_color="transparent",
                hover_color="#f0f0f0",
                cursor="hand2",
                command=cmd,
            ).grid(row=0, column=idx, padx=5, pady=15, sticky="ew")

        self.service_info_frame = ctk.CTkFrame(
            self,
            fg_color="#d4e2ff",
            corner_radius=15,
            border_width=2,
            border_color="#cfebf8",
        )
        self.service_info_frame.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(10, 50),
        )
        self.service_info_frame.grid_columnconfigure((0, 1), weight=1)

        # Doctor Section
        ctk.CTkLabel(
            self,
            text="Our Expert Doctors",
            font=("Roboto", 28, "bold"),
            text_color="#1e3c72",
        ).grid(row=8, column=0, columnspan=2, pady=(30, 10))

        self.lower_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lower_frame.grid(
            row=9,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(10, 50),
        )
        self.lower_frame.grid_columnconfigure((0, 1), weight=1)

        doctors = [
            {
                "name": "Dr. A. Sharma",
                "spec": "Cardiac Specialist",
                "img": "dr_sharma.jpg",
                "achievement": "🏆 500+ Successful Heart Surgeries",
            },
            {
                "name": "Dr. B. Verma",
                "spec": "Neurologist",
                "img": "dr_verma.jpg",
                "achievement": "🎓 Lead Researcher in Neuroplasticity",
            },
            {
                "name": "Dr. C. Gupta",
                "spec": "Orthopedic Surgeon",
                "img": "dr_gupta.jpg",
                "achievement": "🏅 Best Trauma Care Award 2023",
            },
            {
                "name": "Dr. D. Mehta",
                "spec": "Gynecologist",
                "img": "dr_mehta.jpg",
                "achievement": "👶 Delivered 2000+ Healthy Babies",
            },
        ]

        for idx, doc in enumerate(doctors):
            r, c = divmod(idx, 2)
            doc_card = ctk.CTkFrame(
                self.lower_frame,
                fg_color="#f8f9fa",
                corner_radius=10,
                border_width=1,
                border_color="#e0e0e0",
            )
            doc_card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
            doc_card.grid_columnconfigure(1, weight=1)

            try:
                img_path = ASSETS_DIR / doc["img"]
                if os.path.exists(img_path):
                    pil_img = Image.open(img_path)
                    ctk_img = ctk.CTkImage(
                        light_image=pil_img,
                        dark_image=pil_img,
                        size=(100, 100),
                    )
                    ctk.CTkLabel(doc_card, text="", image=ctk_img).grid(
                        row=0,
                        column=0,
                        rowspan=3,
                        padx=15,
                        pady=15,
                    )
                else:
                    ctk.CTkLabel(doc_card, text="📸", font=("", 40)).grid(
                        row=0,
                        column=0,
                        rowspan=3,
                        padx=15,
                        pady=15,
                    )
            except Exception:
                ctk.CTkLabel(doc_card, text="📸", font=("", 40)).grid(
                    row=0,
                    column=0,
                    rowspan=3,
                    padx=15,
                    pady=15,
                )

            ctk.CTkLabel(
                doc_card,
                text=doc["name"],
                font=("Roboto", 20, "bold"),
                text_color="#1a4c8f",
                justify="left",
            ).grid(row=0, column=1, sticky="sw", padx=(0, 15))

            ctk.CTkLabel(
                doc_card,
                text=doc["spec"],
                font=("Roboto", 16),
                text_color="#555555",
                justify="left",
            ).grid(row=1, column=1, sticky="nw", padx=(0, 15))

            ctk.CTkLabel(
                doc_card,
                text=doc["achievement"],
                font=("Roboto", 14, "italic"),
                text_color="#2e7d32",
                justify="left",
            ).grid(row=2, column=1, sticky="nw", padx=(0, 15), pady=(0, 10))

        # Emergency Section
        self.emergency_frame = ctk.CTkFrame(
            self,
            fg_color="#fff1f1",
            corner_radius=15,
            border_width=3,
            border_color="#ff4d4d",
        )
        self.emergency_frame.grid(
            row=10,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=30,
            pady=(20, 60),
        )
        self.emergency_frame.grid_columnconfigure(0, weight=2)
        self.emergency_frame.grid_columnconfigure(1, weight=3)

        try:
            emer_path = ASSETS_DIR / "emergency_service.jpg"
            if os.path.exists(emer_path):
                emer_img = Image.open(emer_path)
                ctk_emer_img = ctk.CTkImage(
                    light_image=emer_img,
                    dark_image=emer_img,
                    size=(500, 250),
                )
                ctk.CTkLabel(self.emergency_frame, text="", image=ctk_emer_img).grid(
                    row=0,
                    column=0,
                    padx=20,
                    pady=20,
                    sticky="nsew",
                )
            else:
                ctk.CTkLabel(self.emergency_frame, text="🚑", font=("", 100)).grid(
                    row=0,
                    column=0,
                    padx=20,
                    pady=20,
                )
        except Exception:
            ctk.CTkLabel(self.emergency_frame, text="🚑", font=("", 100)).grid(
                row=0,
                column=0,
                padx=20,
                pady=20,
            )

        emer_info_frame = ctk.CTkFrame(self.emergency_frame, fg_color="transparent")
        emer_info_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(
            emer_info_frame,
            text="🚨 24/7 Emergency Services",
            font=("Roboto", 32, "bold"),
            text_color="#d32f2f",
            justify="left",
        ).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(
            emer_info_frame,
            text="Immediate Response | Advanced Life Support | 24/7 Availability",
            font=("Roboto", 18, "italic"),
            text_color="#3d3d3d",
            justify="left",
        ).pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(
            emer_info_frame,
            text="📞 Ambulance Helpline: +91-9876543210",
            font=("Courier New", 24, "bold"),
            text_color="white",
            fg_color="#d32f2f",
            corner_radius=8,
            padx=15,
            pady=10,
        ).pack(anchor="w", pady=10)

        ctk.CTkLabel(
            emer_info_frame,
            text="Our team of trauma specialists and advanced paramedics are "
            "always ready to serve you in times of urgent need.",
            font=("Roboto", 16),
            text_color="#555555",
            justify="left",
            wraplength=450,
        ).pack(anchor="w", pady=(10, 0))

        self._show_cardiac_info()

    def _update_service_info(self, title: str, details: str, image_path: str = "") -> None:
        for widget in self.service_info_frame.winfo_children():
            widget.destroy()

        text_frame = ctk.CTkFrame(self.service_info_frame, fg_color="transparent")
        text_frame.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Courier New", 26, "bold"),
            text_color="#1a4c8f",
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            text_frame,
            text=details,
            font=("Roboto", 18),
            text_color="#3d3d3d",
            justify="left",
        ).pack(anchor="w")

        if image_path:
            full_path = ASSETS_DIR / image_path
            if os.path.exists(full_path):
                try:
                    pil_image = Image.open(full_path)
                    ctk_image = ctk.CTkImage(
                        light_image=pil_image,
                        dark_image=pil_image,
                        size=(250, 160),
                    )
                    ctk.CTkLabel(self.service_info_frame, text="", image=ctk_image).grid(
                        row=0,
                        column=1,
                        padx=20,
                        pady=20,
                        sticky="e",
                    )
                except Exception as exc:
                    logger.debug("Could not load service image: %s", exc)

    CARD_SERVICES = [
        (
            "❤️ 24/7 Cardiac Care Unit",
            "• Advanced cardiac monitoring systems\n"
            "• Emergency heart attack treatment (24/7)\n"
            "• ECG, Echo & cardiac life support\n"
            "• Dedicated cardiac specialists",
            "cardiology.jpg",
        ),
        (
            "🧠 Neurology & Stroke Unit",
            "• Stroke emergency management\n"
            "• Treatment for migraines & epilepsy\n"
            "• Nerve disorder diagnostics\n"
            "• MRI/CT integration with neuro-care",
            "neurology.jpg",
        ),
        (
            "🔬 Advanced Diagnostics (MRI/CT)",
            "• MRI, CT Scan, X-Ray, and Ultrasound\n"
            "• High-resolution, fast imaging\n"
            "• Quick report generation\n"
            "• Machine-assisted accurate diagnosis",
            "diagnostics.jpg",
        ),
        (
            "👶 Maternity & Pediatric Care",
            "• Prenatal & antenatal checkups\n"
            "• Delivery support with experts\n"
            "• Neonatal ICU (NICU)\n"
            "• Pediatric specialists for child care",
            "maternity.jpg",
        ),
        (
            "🦴 Orthopedics & Trauma Care",
            "• Treatment for fractures & joint pain\n"
            "• Sports injury management\n"
            "• Spinal problem diagnosis\n"
            "• 24/7 trauma emergency care",
            "orthopedics.jpg",
        ),
        (
            "💊 Pharmacy & Laboratory",
            "• 24/7 in-house pharmacy\n"
            "• Instant blood & urine tests\n"
            "• Accurate laboratory reporting\n"
            "• All medicines always in stock",
            "pathology.jpg",
        ),
    ]

    def _show_cardiac_info(self) -> None:
        name, details, img = self.CARD_SERVICES[0]
        self._update_service_info(name, details, img)

    def _show_neuro_info(self) -> None:
        name, details, img = self.CARD_SERVICES[1]
        self._update_service_info(name, details, img)

    def _show_diagnostic_info(self) -> None:
        name, details, img = self.CARD_SERVICES[2]
        self._update_service_info(name, details, img)

    def _show_maternity_info(self) -> None:
        name, details, img = self.CARD_SERVICES[3]
        self._update_service_info(name, details, img)

    def _show_ortho_info(self) -> None:
        name, details, img = self.CARD_SERVICES[4]
        self._update_service_info(name, details, img)

    def _show_lab_info(self) -> None:
        name, details, img = self.CARD_SERVICES[5]
        self._update_service_info(name, details, img)
