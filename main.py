import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from fpdf import FPDF
from PIL import Image
import datetime
import os
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns


# ================= DATABASE CLASS =================
class Database:
    """
    Handles all persistent data operations for the WellCare Hospital Management System.
    Uses SQLite for efficient, lightweight local data storage.
    """
    def __init__(self):
        try:
            self.conn = sqlite3.connect("clinic.db", check_same_thread=False)
            self.cur = self.conn.cursor()
            self._create_table()
        except Exception as err:
            print(f"Database Connection Error: {err}")
            self.conn = None
            self.cur = None

    def _create_table(self):
        if self.cur:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT,
                    age TEXT,
                    gender TEXT,
                    blood_group TEXT,
                    weight TEXT,
                    mobile TEXT,
                    email TEXT,
                    address TEXT,
                    pincode TEXT,
                    symptoms TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()

    def add_patient(self, data):
        if self.cur:
            try:
                self.cur.execute("""
                    INSERT INTO patients(
                        first_name, last_name, age, gender, blood_group, weight, 
                        mobile, email, address, pincode, symptoms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
                self.conn.commit()
                return True
            except Exception as e:
                print(e)
                return False
        return False

    def search_patient(self, keyword):
        if self.cur:
            self.cur.execute("""
                SELECT id, first_name, last_name, age, mobile, symptoms 
                FROM patients
                WHERE first_name LIKE ? OR last_name LIKE ?
            """, (f"%{keyword}%", f"%{keyword}%"))
            return self.cur.fetchall()
        return []

    def delete_patient(self, patient_id):
        if self.cur:
            try:
                self.cur.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                self.conn.commit()
                return self.cur.rowcount > 0
            except Exception:
                return False
        return False

    def get_dashboard_stats(self):
        if not self.cur:
            return {"total": 0, "genders": [], "blood_groups": [], "ages": []}
            
        self.cur.execute("SELECT COUNT(*) FROM patients")
        total = self.cur.fetchone()[0]
        
        self.cur.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
        genders = self.cur.fetchall()
        
        self.cur.execute("SELECT blood_group, COUNT(*) FROM patients GROUP BY blood_group")
        blood_groups = self.cur.fetchall()
        
        self.cur.execute("SELECT age FROM patients")
        ages = [row[0] for row in self.cur.fetchall()]
        
        # Today's Patients
        self.cur.execute("SELECT COUNT(*) FROM patients WHERE date(created_at) = date('now')")
        today = self.cur.fetchone()[0]
        
        # Trends (Last 7 Days - Proper Order)
        self.cur.execute("""
            SELECT date(created_at) as d, COUNT(*) 
            FROM patients
            WHERE created_at >= date('now', '-6 days')
            GROUP BY d
            ORDER BY d ASC
        """)
        trends = self.cur.fetchall()
        
        # Recent Patients (Last 5)
        self.cur.execute("SELECT id, first_name, last_name, mobile FROM patients ORDER BY id DESC LIMIT 5")
        recent = self.cur.fetchall()
        
        self.cur.execute("SELECT symptoms FROM patients")
        symptoms = [row[0] for row in self.cur.fetchall() if row[0]]
        
        return {
            "total": total,
            "today": today,
            "genders": genders,
            "blood_groups": blood_groups,
            "ages": ages,
            "symptoms": symptoms,
            "trends": trends,
            "recent": recent
        }


# ================= UI FRAMES (OOP STRUCTURE) =================

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.build_ui()

    def build_ui(self):
        try:
            logo_pil_image = Image.open("assets/wellcare.png")
            big_logo = ctk.CTkImage(light_image=logo_pil_image, dark_image=logo_pil_image, size=(350, 350))
            logo_label = ctk.CTkLabel(self, text="", image=big_logo)
            logo_label.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        except Exception:
            pass

        ctk.CTkLabel(self, text="WellCare Hospital", font=("Courier New", 50, "bold"), text_color="#1e3c72").grid(row=2, pady=(20, 10), columnspan=2)
        ctk.CTkLabel(self, text="Providing compassionate care 24/7", font=("Roboto", 20, "italic"), text_color="#3d3d3d").grid(row=3, pady=(0, 20), columnspan=2)

        info_frame = ctk.CTkFrame(self, fg_color="#edf5fd", corner_radius=5)
        info_frame.grid(row=4, column=0, padx=5, pady=20, columnspan=2, sticky="ew")
        info_frame.grid_columnconfigure((0, 1, 2), weight=1)

        info_font = ("Roboto", 18, "bold")
        
        ctk.CTkLabel(info_frame, text="🚨 Emergency: 24/7 Available\n📞 +91-1234567890", font=info_font, text_color="#d32f2f", justify="left").grid(row=0, column=0, padx=20, pady=20, sticky="w")
        ctk.CTkLabel(info_frame, text="🏥 OPD Timings\n🕒 9:00 AM - 8:00 PM", font=info_font, text_color="#1976d2", justify="center").grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(info_frame, text="📍 Location\nCareWell Clinic, Gandhi Nagar, Nagpur", font=info_font, text_color="#388e3c", justify="right").grid(row=0, column=2, padx=20, pady=20, sticky="e")

        ctk.CTkLabel(self, text="Our Specialist Services", font=("Roboto", 28, "bold"), text_color="#1e3c72").grid(row=5, column=0, columnspan=2, pady=(30, 10))

        self.services_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=5, border_width=1, border_color="#acb0b3")
        self.services_frame.grid(row=6, column=0, padx=5, pady=10, columnspan=2, sticky="ew")
        for i in range(6): self.services_frame.grid_columnconfigure(i, weight=1)

        services = [
            ("❤️ Cardiac Care", "#d32f2f", self.show_cardiac_info), ("🧠 Neurology", "#1e85da", self.show_neuro_info), ("🔬 Diagnostics", "#388e3c", self.show_diagnostic_info),
            ("👶 Maternity", "#8e24aa", self.show_maternity_info), ("🦴 Orthopedics", "#fbc02d", self.show_ortho_info), ("🧑‍🔬 Pathology", "#00838f", self.show_lab_info)
        ]

        for idx, (text, color, cmd) in enumerate(services):
            ctk.CTkButton(self.services_frame, text=text, font=("Roboto", 14, "bold"), text_color=color, fg_color="transparent", hover_color="#f0f0f0", cursor="hand2", command=cmd).grid(row=0, column=idx, padx=5, pady=15, sticky="ew")

        self.service_info_frame = ctk.CTkFrame(self, fg_color="#d4e2ff", corner_radius=15, border_width=2, border_color="#cfebf8")
        self.service_info_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=30, pady=(10, 50))
        self.service_info_frame.grid_columnconfigure((0, 1), weight=1)
        
        # --- Doctor Speciality Section (2x2 Matrix) ---
        ctk.CTkLabel(self, text="Our Expert Doctors", font=("Roboto", 28, "bold"), text_color="#1e3c72").grid(row=8, column=0, columnspan=2, pady=(30, 10))
        
        self.lower_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lower_frame.grid(row=9, column=0, columnspan=2, sticky="ew", padx=30, pady=(10, 50))
        self.lower_frame.grid_columnconfigure((0, 1), weight=1)

        doctors = [
            {"name": "Dr. A. Sharma", "spec": "Cardiac Specialist", "img": "assets/dr_sharma.jpg", "achievement": "🏆 500+ Successful Heart Surgeries"},
            {"name": "Dr. B. Verma", "spec": "Neurologist", "img": "assets/dr_verma.jpg", "achievement": "🎓 Lead Researcher in Neuroplasticity"},
            {"name": "Dr. C. Gupta", "spec": "Orthopedic Surgeon", "img": "assets/dr_gupta.jpg", "achievement": "🏅 Best Trauma Care Award 2023"},
            {"name": "Dr. D. Mehta", "spec": "Gynecologist", "img": "assets/dr_mehta.jpg", "achievement": "👶 Delivered 2000+ Healthy Babies"}
        ]

        for idx, doc in enumerate(doctors):
            r, c = divmod(idx, 2)
            doc_card = ctk.CTkFrame(self.lower_frame, fg_color="#f8f9fa", corner_radius=10, border_width=1, border_color="#e0e0e0")
            doc_card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
            doc_card.grid_columnconfigure(1, weight=1)

            # Profile Image
            try:
                if os.path.exists(doc["img"]):
                    pil_img = Image.open(doc["img"])
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(100, 100))
                    ctk.CTkLabel(doc_card, text="", image=ctk_img).grid(row=0, column=0, rowspan=3, padx=15, pady=15)
                else:
                    ctk.CTkLabel(doc_card, text="📸", font=("", 40)).grid(row=0, column=0, rowspan=3, padx=15, pady=15)
            except:
                ctk.CTkLabel(doc_card, text="📸", font=("", 40)).grid(row=0, column=0, rowspan=3, padx=15, pady=15)

            # Name, Speciality & Achievement
            ctk.CTkLabel(doc_card, text=doc["name"], font=("Roboto", 20, "bold"), text_color="#1a4c8f", justify="left").grid(row=0, column=1, sticky="sw", padx=(0, 15))
            ctk.CTkLabel(doc_card, text=doc["spec"], font=("Roboto", 16), text_color="#555555", justify="left").grid(row=1, column=1, sticky="nw", padx=(0, 15))
            ctk.CTkLabel(doc_card, text=doc["achievement"], font=("Roboto", 14, "italic"), text_color="#2e7d32", justify="left").grid(row=2, column=1, sticky="nw", padx=(0, 15), pady=(0, 10))

        # --- Emergency Service Section (Bottom Frame) ---
        self.emergency_frame = ctk.CTkFrame(self, fg_color="#fff1f1", corner_radius=15, border_width=3, border_color="#ff4d4d")
        self.emergency_frame.grid(row=10, column=0, columnspan=2, sticky="ew", padx=30, pady=(20, 60))
        self.emergency_frame.grid_columnconfigure(0, weight=2)
        self.emergency_frame.grid_columnconfigure(1, weight=3)

        # Emergency Image
        try:
            if os.path.exists("assets/emergency_service.jpg"):
                emer_img = Image.open("assets/emergency_service.jpg")
                ctk_emer_img = ctk.CTkImage(light_image=emer_img, dark_image=emer_img, size=(500, 250))
                ctk.CTkLabel(self.emergency_frame, text="", image=ctk_emer_img).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
            else:
                ctk.CTkLabel(self.emergency_frame, text="🚑", font=("", 100)).grid(row=0, column=0, padx=20, pady=20)
        except:
            ctk.CTkLabel(self.emergency_frame, text="🚑", font=("", 100)).grid(row=0, column=0, padx=20, pady=20)

        # Emergency Info
        emer_info_frame = ctk.CTkFrame(self.emergency_frame, fg_color="transparent")
        emer_info_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(emer_info_frame, text="🚨 24/7 Emergency Services", font=("Roboto", 32, "bold"), text_color="#d32f2f", justify="left").pack(anchor="w", pady=(10, 5))
        ctk.CTkLabel(emer_info_frame, text="Immediate Response | Advanced Life Support | 24/7 Availability", font=("Roboto", 18, "italic"), text_color="#3d3d3d", justify="left").pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(emer_info_frame, text="📞 Ambulance Helpline: +91-9876543210", font=("Courier New", 24, "bold"), text_color="white", fg_color="#d32f2f", corner_radius=8, padx=15, pady=10).pack(anchor="w", pady=10)
        ctk.CTkLabel(emer_info_frame, text="Our team of trauma specialists and advanced paramedics are always ready to serve you in times of urgent need.", font=("Roboto", 16), text_color="#555555", justify="left", wraplength=450).pack(anchor="w", pady=(10, 0))

        self.show_cardiac_info()

    def update_service_info(self, title, details, image_path=None):
        for widget in self.service_info_frame.winfo_children(): widget.destroy()

        text_frame = ctk.CTkFrame(self.service_info_frame, fg_color="transparent")
        text_frame.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        ctk.CTkLabel(text_frame, text=title, font=("Courier New", 26, "bold"), text_color="#1a4c8f", justify="left").pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(text_frame, text=details, font=("Roboto", 18), text_color="#3d3d3d", justify="left").pack(anchor="w")

        if image_path and os.path.exists(image_path):
            try:
                pil_image = Image.open(image_path)
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(250, 160))
                ctk.CTkLabel(self.service_info_frame, text="", image=ctk_image).grid(row=0, column=1, padx=20, pady=20, sticky="e")
            except: pass

    def show_cardiac_info(self): self.update_service_info("❤️ 24/7 Cardiac Care Unit", "• Advanced cardiac monitoring systems\n• Emergency heart attack treatment (24/7)\n• ECG, Echo & cardiac life support\n• Dedicated cardiac specialists", "assets/cardiology.jpg")
    def show_neuro_info(self): self.update_service_info("🧠 Neurology & Stroke Unit", "• Stroke emergency management\n• Treatment for migraines & epilepsy\n• Nerve disorder diagnostics\n• MRI/CT integration with neuro-care", "assets/neurology.jpg")
    def show_diagnostic_info(self): self.update_service_info("🔬 Advanced Diagnostics (MRI/CT)", "• MRI, CT Scan, X-Ray, and Ultrasound\n• High-resolution, fast imaging\n• Quick report generation\n• Machine-assisted accurate diagnosis", "assets/diagnostics.jpg")
    def show_maternity_info(self): self.update_service_info("👶 Maternity & Pediatric Care", "• Prenatal & antenatal checkups\n• Delivery support with experts\n• Neonatal ICU (NICU)\n• Pediatric specialists for child care", "assets/maternity.jpg")
    def show_ortho_info(self): self.update_service_info("🦴 Orthopedics & Trauma Care", "• Treatment for fractures & joint pain\n• Sports injury management\n• Spinal problem diagnosis\n• 24/7 trauma emergency care", "assets/orthopedics.jpg")
    def show_lab_info(self): self.update_service_info("💊 Pharmacy & Laboratory", "• 24/7 in-house pharmacy\n• Instant blood & urine tests\n• Accurate laboratory reporting\n• All medicines always in stock", "assets/pathology.jpg")


class AboutFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.build_ui()

    def build_ui(self):
        try:
            logo_pil_image = Image.open("assets/wellcare.png")
            logo = ctk.CTkImage(light_image=logo_pil_image, dark_image=logo_pil_image, size=(200, 200))
            ctk.CTkLabel(self, text="", image=logo).grid(columnspan=2, row=0, column=0, pady=(10, 10))
        except: pass

        ctk.CTkLabel(self, text="About WellCare Hospital", font=("Courier New", 40, "bold"), text_color="#1e3c72").grid(columnspan=2, row=1, column=0, pady=(20, 20))
        
        info_text = (
            "WellCare Hospital is a leading healthcare provider dedicated to offering\n"
            "comprehensive medical services with compassion and excellence.\n\n"
            "Our facility is equipped with state-of-the-art technology and staffed\n"
            "by highly trained professionals committed to the well-being of our community."
            "\n\nVersion: 1.0.0 | Clinic Management System"
        )
        ctk.CTkLabel(self, text=info_text, font=("Roboto", 18), justify="center").grid(columnspan=2, row=2, column=0, pady=20)
        ctk.CTkButton(self, text="Visit Website", command=lambda: webbrowser.open("https://github.com/"), font=("Roboto", 18, "bold"), fg_color="#1e85da", hover_color="#1565c0").grid(columnspan=2, row=3, column=0, pady=30)


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Clinic System Login", font=("", 28, "bold")).grid(pady=(50, 40), columnspan=2, column=0, row=0)
        ctk.CTkLabel(self, text="ID:", font=("Roboto", 20), text_color="#3D3D3D").grid(row=2, column=0, padx=10, pady=15, sticky="e")
        self.id_entry = ctk.CTkEntry(self, placeholder_text="Admin ('admin') or Staff ('staff')", width=250)
        self.id_entry.grid(row=2, column=1, padx=10, pady=15, sticky="w")

        ctk.CTkLabel(self, text="Password:", font=("Roboto", 20), text_color="#3D3D3D").grid(row=3, column=0, padx=10, pady=15, sticky="e")
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Enter Password ('123')", width=250, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=15, sticky="w")

        ctk.CTkButton(self, text="Login", command=self.login_check, font=("Roboto", 18, "bold"), fg_color="#374fb9", hover_color="#2a3c8e").grid(row=4, column=0, padx=30, pady=40, columnspan=2)

    def login_check(self):
        uid = self.id_entry.get().strip()
        pwd = self.password_entry.get().strip()
        
        if uid == "admin" and pwd == "123":
            self.controller.is_logged_in = True
            self.controller.current_user_role = "admin"
            self.controller.update_nav_buttons()
            messagebox.showinfo("Admin Login", "Welcome Administrator!\nFull system dashboard unlocked.")
            self.controller.show_frame(HomeFrame)
            
        elif uid == "staff" and pwd == "123":
            self.controller.is_logged_in = True
            self.controller.current_user_role = "staff"
            self.controller.update_nav_buttons()
            messagebox.showinfo("Staff Login", "Login Successful. Redirecting to Home.")
            self.controller.show_frame(HomeFrame)
            
        else:
            messagebox.showwarning("Warning", "Invalid User ID or Password!")


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.build_ui()

    def build_ui(self):
        if self.controller.current_user_role != "admin":
            ctk.CTkLabel(self, text="Unauthorized: Admins Only", text_color="red", font=("", 20)).pack()
            return

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(header_frame, text="Clinic Analytics Dashboard", font=("Courier New", 40, "bold"), text_color="#1e3c72").grid(row=0, column=1)

        self.chart_view_var = ctk.StringVar(value="Demographics View")
        view_menu = ctk.CTkOptionMenu(
            header_frame, 
            variable=self.chart_view_var, 
            values=["Demographics View", "Medical View", "Trend & History View"], 
            command=self.render_charts
        )
        view_menu.grid(row=0, column=2, sticky="e", padx=(20, 100))

        ctk.CTkButton(
            header_frame, 
            text="🔄 Refresh", 
            width=100,
            command=self.render_charts,
            fg_color="#388e3c",
            hover_color="#2e7d32"
        ).grid(row=0, column=2, sticky="e", padx=20)

        self.kpi_frame = ctk.CTkFrame(self, fg_color="#1e85da", corner_radius=10)
        self.kpi_frame.grid(row=1, column=0, columnspan=2, pady=10, ipady=10, ipadx=40)

        self.chart_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_container.grid(row=3, column=0, columnspan=2, pady=(10, 30), padx=20, sticky="nsew")

        ctk.CTkLabel(self, text="Graphical Representation", font=("Roboto", 24, "bold"), text_color="#1e3c72").grid(row=2, column=0, columnspan=2, pady=(30, 0))

        self.render_charts()
        self.auto_refresh()

    def render_charts(self, choice=None):
        for w in self.kpi_frame.winfo_children(): w.destroy()
        for w in self.chart_container.winfo_children(): w.destroy()

        stats = self.controller.db.get_dashboard_stats()

        # KPI Layout - Two Cards
        self.kpi_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Total Card
        total_card = ctk.CTkFrame(self.kpi_frame, fg_color="transparent")
        total_card.grid(row=0, column=0, padx=40, pady=10)
        ctk.CTkLabel(total_card, text="Total Patients", font=("Roboto", 18), text_color="white").pack()
        ctk.CTkLabel(total_card, text=str(stats["total"]), font=("Roboto", 45, "bold"), text_color="white").pack()
        
        # Today Card
        today_card = ctk.CTkFrame(self.kpi_frame, fg_color="transparent")
        today_card.grid(row=0, column=1, padx=40, pady=10)
        ctk.CTkLabel(today_card, text="New Patients (Today)", font=("Roboto", 18), text_color="white").pack()
        ctk.CTkLabel(today_card, text=str(stats["today"]), font=("Roboto", 45, "bold"), text_color="#ffd700").pack()

        if stats["total"] == 0:
            ctk.CTkLabel(self.chart_container, text="No patients in database yet.", font=("Roboto", 18)).pack(pady=100)
            return

        fig = None # Initialize to avoid NameError

        sns.set_theme(style="whitegrid")
        current_view = self.chart_view_var.get()
        
        # Determine background color based on current mode
        bg_col = "#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "#ebebeb"
        text_col = "white" if ctk.get_appearance_mode() == "Dark" else "black"
        plt.rcParams.update({'text.color': text_col, 'axes.labelcolor': text_col})

        if current_view == "Demographics View":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor=bg_col)
            fig.tight_layout(pad=3.0)

            # 1. Pie Chart
            valid_genders = [(g[0] if g[0] not in ["", "Select"] else "Unknown", g[1]) for g in stats["genders"]]
            labels1 = [item[0] for item in valid_genders]
            sizes1 = [item[1] for item in valid_genders]
            if sizes1:
                colors = sns.color_palette("pastel")[0:len(sizes1)]
                ax1.pie(sizes1, labels=labels1, autopct='%1.1f%%', startangle=90, colors=colors)
                ax1.set_title("Patient Demographics")
                ax1.axis('equal')

            # 2. Bar Chart (Age Groups)
            age_groups = {"0-18": 0, "19-35": 0, "36-50": 0, "51+": 0}
            for age_str in stats.get("ages", []):
                try:
                    a = int(age_str)
                    if a <= 18: age_groups["0-18"] += 1
                    elif a <= 35: age_groups["19-35"] += 1
                    elif a <= 50: age_groups["36-50"] += 1
                    else: age_groups["51+"] += 1
                except ValueError: pass
            if any(age_groups.values()):
                sns.barplot(x=list(age_groups.keys()), y=list(age_groups.values()), ax=ax2, palette="viridis")
                ax2.set_title("Age Categories")
                ax2.set_ylabel("Count")

        elif current_view == "Medical View":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor=bg_col)
            fig.tight_layout(pad=3.0)

            # 1. Bar Chart (Blood Groups)
            valid_bloods = [(b[0] if b[0] not in ["", "Select"] else "Unk", b[1]) for b in stats["blood_groups"]]
            labels2 = [item[0] for item in valid_bloods]
            values2 = [item[1] for item in valid_bloods]
            if values2:
                sns.barplot(x=labels2, y=values2, ax=ax1, palette="magma")
                ax1.set_title("Blood Group Distribution")
                ax1.set_ylabel("Count")

            # 2. Top Symptoms Chart
            symptom_words = []
            for s in stats.get("symptoms", []):
                for word in str(s).replace(',', ' ').split():
                    if len(word) > 3: symptom_words.append(word.lower())
            
            from collections import Counter
            top_symp = Counter(symptom_words).most_common(5)
            if top_symp:
                sns.barplot(x=[x[0].capitalize() for x in top_symp], y=[x[1] for x in top_symp], ax=ax2, palette="rocket")
                ax2.set_title("Top 5 Report Keywords")
                ax2.set_ylabel("Frequency")
            else:
                ax2.text(0.5, 0.5, 'No Symptom Data', ha='center', va='center', fontsize=12)
                ax2.set_axis_off()

        elif current_view == "Trend & History View":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor=bg_col)
            fig.tight_layout(pad=3.0)

            # 1. Line Chart (Registration Trends)
            if stats["trends"]:
                dates = [t[0] for t in reversed(stats["trends"])]
                counts = [t[1] for t in reversed(stats["trends"])]
                sns.lineplot(x=dates, y=counts, marker='o', ax=ax1, color="#1e85da")
                ax1.set_title("Registration Trends (Last 7 Days)")
                ax1.set_ylabel("New Patients")
                plt.setp(ax1.get_xticklabels(), rotation=30, horizontalalignment='right')
            else:
                ax1.text(0.5, 0.5, 'No Trend Data', ha='center', va='center')

            # 2. Text Summary (Recent Records)
            recent_text = "Recent Registrations:\n" + ("-"*30) + "\n"
            for r in stats["recent"]:
                recent_text += f"ID: {r[0]} | {r[1]} {r[2]} | {r[3]}\n"
            
            ax2.text(0.1, 0.9, recent_text, ha='left', va='top', fontname='Courier New', fontsize=10, transform=ax2.transAxes)
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

    def auto_refresh(self):
        if self.controller.current_frame == self:
            self.render_charts()
            self.after(10000, self.auto_refresh)


class PatientEntryFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Customer Details", font=("", 28, "bold")).grid(pady=(20, 25), columnspan=2, row=0)
        self.status_label = ctk.CTkLabel(self, text="", font=("Roboto", 16, "bold"))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        fields = [
            ("First Name", "first_name", ctk.CTkEntry), ("Last Name", "last_name", ctk.CTkEntry),
            ("Age", "age", ctk.CTkComboBox, [str(i) for i in range(1, 121)]), ("Gender", "gender", ctk.CTkComboBox, ['Male', 'Female', 'Other']),
            ("Blood Group", "blood", ctk.CTkComboBox, ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
            ("Weight (KG)", "weight", ctk.CTkEntry), ("Symptoms", "symptoms", ctk.CTkTextbox),
            ("Address", "address", ctk.CTkTextbox), ("Pincode", "pincode", ctk.CTkEntry),
            ("Email ID", "email", ctk.CTkEntry), ("Mobile No", "mobile", ctk.CTkEntry)
        ]

        self.inputs = {}
        row_idx = 2
        for field in fields:
            label_text, var_name, widget_type = field[0], field[1], field[2]
            ctk.CTkLabel(self, text=f"{label_text}   -", font=("Roboto", 20), text_color="#3D3D3D").grid(row=row_idx, column=0, padx=100, pady=10, sticky="e")

            if widget_type == ctk.CTkComboBox:
                widget = widget_type(self, values=field[3], border_color="#dddddd", width=250)
                widget.set("Select Age" if label_text == "Age" else "Select")
            elif widget_type == ctk.CTkTextbox:
                widget = widget_type(self, border_color="#b1acac", width=250, height=80, border_width=1)
            else:
                widget = widget_type(self, border_color="#dddddd", placeholder_text=f"Enter {label_text}", width=250, border_width=1)
            
            widget.grid(row=row_idx, column=1, padx=10, pady=10, sticky="w")
            self.inputs[var_name] = widget
            row_idx += 1

        ctk.CTkButton(self, text="Clear", command=self.clear_entries, text_color="#e9e9e9", fg_color="#fa4c4c", hover_color="#e63636").grid(row=row_idx, column=0, padx=30, pady=30, sticky="e")
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.grid(row=row_idx, column=1, padx=30, pady=30, sticky="w")
        ctk.CTkButton(btn_container, text="Save Only", command=self.save_action, text_color="#e9e9e9", fg_color="#52bb6c", hover_color="#447c3c").pack(side="left", padx=5)
        ctk.CTkButton(btn_container, text="Save & Print PDF", command=self.save_and_print_action, text_color="#e9e9e9", fg_color="#374fb9", hover_color="#2a3c8e").pack(side="left", padx=5)

    def display_status(self, message, color="red"):
        self.status_label.configure(text=message, text_color=color)
        self.after(4000, lambda: self.status_label.configure(text=""))

    def validate_inputs(self, mobile, email, weight, age):
        import re
        if not mobile.isdigit() or len(mobile) < 10: return "Mobile No must be at least 10 digits."
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email): return "Invalid Email format."
        if weight and not weight.replace('.', '', 1).isdigit(): return "Weight must be numeric."
        if age == "Select Age": return "Please select an Age."
        return None

    def get_val(self, key):
        widget = self.inputs[key]
        return widget.get("1.0", "end-1c").strip() if isinstance(widget, ctk.CTkTextbox) else widget.get().strip()

    def save_action(self):
        vals = {k: self.get_val(k) for k in self.inputs.keys()}
        if not vals["first_name"] or not vals["last_name"] or not vals["mobile"]: return self.display_status("First Name, Last Name, and Mobile are required.", "red")
        
        err = self.validate_inputs(vals["mobile"], vals["email"], vals["weight"], vals["age"])
        if err: return self.display_status(err, "red")

        if self.controller.db.conn:
            data = (vals["first_name"], vals["last_name"], vals["age"], vals["gender"], vals["blood"], vals["weight"], vals["mobile"], vals["email"], vals["address"], vals["pincode"], vals["symptoms"])
            success = self.controller.db.add_patient(data)
            if success:
                self.display_status("Patient Record Added Successfully!", "green")
                self.clear_entries()
                self.controller.refresh_dashboard_if_open()
            else: self.display_status("Failed to add record.", "red")
        else:
            self.display_status("Database is unavailable.", "red")

    def save_and_print_action(self):
        first, last, age, mobile = self.get_val("first_name"), self.get_val("last_name"), self.get_val("age"), self.get_val("mobile")
        if not first or not last or not mobile: return self.display_status("Required elements missing.", "red")
        self.save_action()
        if first: self.generate_pdf_prescription(first, last, age, mobile)

    def generate_pdf_prescription(self, first, last, age, mobile):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 24); pdf.set_text_color(30, 133, 218); pdf.cell(200, 15, txt="WellCare Hospital", ln=True, align='C')
        pdf.set_font("Arial", 'I', 12); pdf.set_text_color(100, 100, 100); pdf.cell(200, 10, txt="Your health, our priority.", ln=True, align='C'); pdf.ln(10)
        pdf.set_font("Arial", 'B', 14); pdf.set_text_color(0, 0, 0); pdf.cell(200, 10, txt="Patient Record Form", ln=True, align='L', border='B'); pdf.ln(5)
        pdf.set_font("Arial", '', 12); pdf.cell(100, 10, txt=f"Name: {first} {last}", ln=False); pdf.cell(100, 10, txt=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(100, 10, txt=f"Age: {age}", ln=False); pdf.cell(100, 10, txt=f"Mobile: {mobile}", ln=True); pdf.ln(10)
        pdf.set_font("Arial", 'B', 14); pdf.cell(200, 10, txt="Prescription / Doctor Notes:", ln=True, align='L'); pdf.set_font("Arial", '', 12); pdf.multi_cell(0, 80, txt="", border=1)
        pdf.ln(10); pdf.set_font("Arial", 'I', 10); pdf.cell(200, 10, txt="Doctor Signature: _______________________", ln=True, align='R')
        
        folder = "Patient_Prescriptions"
        if not os.path.exists(folder): os.makedirs(folder)
        filename = f"{folder}/{first}_{last}_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
        try:
            pdf.output(filename)
            self.display_status(f"Saved DB & Generated PDF ({filename})", "green")
        except Exception: self.display_status("Saved DB, but PDF failed.", "red")

    def clear_entries(self):
        for k, v in self.inputs.items():
            if isinstance(v, ctk.CTkComboBox): v.set("Select Age" if k == "age" else "Select")
            elif isinstance(v, ctk.CTkTextbox): v.delete("1.0", "end")
            else: v.delete(0, "end")


class SearchFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="Search Patient Record", font=("Courier New", 30, "bold")).grid(row=0, column=0, pady=30)
        
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter Name", width=300)
        self.search_entry.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Search", command=self.search_action, fg_color="#1e85da").pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Show All", command=lambda: self.search_action(show_all=True), fg_color="#388e3c", hover_color="#2e7d32").pack(side="left", padx=10)

        # Admin Features
        if self.controller.current_user_role == "admin":
            action_frame = ctk.CTkFrame(self, fg_color="transparent")
            action_frame.grid(row=2, column=0, pady=10)
            self.delete_id_entry = ctk.CTkEntry(action_frame, placeholder_text="Patient ID to Delete", width=150)
            self.delete_id_entry.pack(side="left", padx=10)
            ctk.CTkButton(action_frame, text="Delete Patient", fg_color="red", hover_color="#8b0000", command=self.delete_action).pack(side="left", padx=10)

        self.result_box = ctk.CTkTextbox(self, width=800, height=400, font=("Courier", 14))
        self.result_box.grid(row=3, column=0, pady=30)
        self.result_box.insert("1.0", "Search by entering the patient's first or last name.")
        self.result_box.configure(state="disabled")

    def search_action(self, show_all=False):
        name = self.search_entry.get().strip() if not show_all else ""
        if not name and not show_all: return messagebox.showwarning("Warning", "Please enter a name to search.")
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")

        if self.controller.db.conn:
            records = self.controller.db.search_patient(name)
            if records:
                self.result_box.insert("end", f"Found {len(records)} database records:\n" + ("="*50) + "\n\n")
                for r in records:
                    # Handle None values to avoid TypeError during formatting
                    rid = str(r[0]) if r[0] is not None else ""
                    fname = str(r[1]) if r[1] is not None else ""
                    lname = str(r[2]) if r[2] is not None else ""
                    age = str(r[3]) if r[3] is not None else ""
                    mobile = str(r[4]) if r[4] is not None else ""
                    symptoms = str(r[5]) if r[5] is not None else ""
                    
                    self.result_box.insert("end", f"ID: {rid:<4} | Name: {fname} {lname:<15} | Age: {age:<4} | Mobile: {mobile}\nSymptoms: {symptoms}\n{'-'*60}\n")
            else: self.result_box.insert("end", "No patient found.")
        self.result_box.configure(state="disabled")

    def delete_action(self):
        pid = self.delete_id_entry.get().strip()
        if not pid.isdigit():
            messagebox.showwarning("Error", "Please enter a valid numeric ID.")
            return
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to completely delete Patient ID {pid}?"):
            if self.controller.db.delete_patient(pid):
                messagebox.showinfo("Success", f"Patient ID {pid} deleted.")
                self.search_action()
                self.controller.refresh_dashboard_if_open()
            else:
                messagebox.showerror("Error", "Failed to delete patient. Ensure ID exists.")


# ================= MAIN CONTROLLER =================

class ClinicApp(ctk.CTk):
    """
    Main controller class for the application. 
    Implements the Controller-Frame pattern to manage navigation and global state.
    """
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title("WellCare Hospital Patient Management")
        self.geometry("1440x1024")
        self.minsize(900, 700)

        self.db = Database()
        if not self.db.conn: messagebox.showwarning("Database Error", "SQLite database connection failed.\nPlease ensure 'clinic.db' exists and is accessible.")
        
        self.is_logged_in = False
        self.current_user_role = None  # "admin" | "staff"
        
        # Build Wrapper UI
        self.upper_frame = ctk.CTkFrame(self, fg_color="#1e85da", height=120)
        self.upper_frame.pack(fill="x")
        
        try:
            img = Image.open("assets/wellcare.png")
            self.logo = ctk.CTkImage(dark_image=img, light_image=img, size=(200, 190))
            ctk.CTkLabel(self.upper_frame, text="", image=self.logo).place(anchor="nw", rely=-0.19, relx=0.02)
        except: pass

        ctk.CTkLabel(self.upper_frame, text="WellCare Hospital", font=("courier new", 55, "bold"), text_color="white").pack(pady=10)
        ctk.CTkLabel(self.upper_frame, text="Your health, our priority.", font=("Roboto", 15, "bold"), text_color="#e7dada").pack(pady=(0, 5))
        
        self.date_label = ctk.CTkLabel(self.upper_frame, font=("", 14), text_color="#e7dada")
        self.date_label.place(relx=0.98, rely=0.03, anchor="ne")
        
        self.mode_switch = ctk.CTkSwitch(self.upper_frame, text="Dark Mode", text_color="white", progress_color="#52bb6c", command=self.toggle_mode)
        self.mode_switch.place(relx=0.98, rely=0.3, anchor="ne")
        
        self.update_time()

        # Nav Buttons Array
        self.button_frame = ctk.CTkFrame(self.upper_frame, fg_color="transparent")
        self.button_frame.pack(pady=(5, 10))
        nav_args = {"fg_color": "transparent", "font": ("Roboto", 15, "bold"), "hover": True, "cursor": "hand2"}

        self.home_screen_button = ctk.CTkButton(self.button_frame, command=lambda: self.show_frame(HomeFrame), text="HOME", **nav_args)
        self.home_screen_button.grid(column=0, row=0, padx=15)
        
        self.about_button = ctk.CTkButton(self.button_frame, command=lambda: self.show_frame(AboutFrame), text="ABOUT", **nav_args)
        self.login_screen_button = ctk.CTkButton(self.button_frame, command=lambda: self.show_frame(LoginFrame), text="LOGIN", **nav_args)
        self.dashboard_button = ctk.CTkButton(self.button_frame, command=lambda: self.show_frame(DashboardFrame), text="DASHBOARD", **nav_args)
        self.new_patient_record_button = ctk.CTkButton(self.button_frame, command=lambda: self.show_frame(PatientEntryFrame), text="NEW PATIENT", **nav_args)
        self.search_button = ctk.CTkButton(self.button_frame, command=lambda: self.show_frame(SearchFrame), text="SEARCH", **nav_args)
        self.logout_button = ctk.CTkButton(self.button_frame, command=self.logout_action, text="LOGOUT", fg_color="#e25353", font=("Roboto", 15, "bold"), hover_color="#c44545", cursor="hand2")

        # Context Frame Container
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.current_frame = None
        self.update_nav_buttons()
        self.show_frame(HomeFrame)

    def update_time(self):
        self.date_label.configure(text=datetime.datetime.now().strftime("Date: %d/%m/%Y \nTime: %H:%M:%S"))
        self.after(1000, self.update_time)

    def refresh_dashboard_if_open(self):
        if isinstance(self.current_frame, DashboardFrame):
            self.current_frame.render_charts()

    def update_nav_buttons(self):
        if self.is_logged_in:
            self.login_screen_button.grid_forget()
            c_idx = 1
            if self.current_user_role == "admin":
                self.dashboard_button.grid(column=c_idx, row=0, padx=15)
                c_idx += 1
            else: self.dashboard_button.grid_forget()
            
            self.new_patient_record_button.grid(column=c_idx, row=0, padx=15)
            self.search_button.grid(column=c_idx+1, row=0, padx=15)
            self.about_button.grid(column=c_idx+2, row=0, padx=15)
            self.logout_button.grid(column=c_idx+3, row=0, padx=15)
        else:
            self.dashboard_button.grid_forget(); self.new_patient_record_button.grid_forget()
            self.search_button.grid_forget(); self.logout_button.grid_forget()
            self.about_button.grid(column=1, row=0, padx=15)
            self.login_screen_button.grid(column=2, row=0, padx=15)

    def toggle_mode(self):
        mode = "Dark" if self.mode_switch.get() else "Light"
        ctk.set_appearance_mode(mode)
        # Rerender if we are currently visualizing charts to update the canvas theme
        if hasattr(self, 'current_frame') and isinstance(self.current_frame, DashboardFrame):
            self.current_frame.render_charts()

    def show_frame(self, frame_class):
        # Authenticate routes implicitly based on frame classes
        if not self.is_logged_in and frame_class in [DashboardFrame, PatientEntryFrame, SearchFrame]:
            messagebox.showwarning("Access Denied", "Please login first.")
            return self.show_frame(LoginFrame)

        if self.current_frame: self.current_frame.destroy()
        
        # Instantiate Frame and link this controller
        self.current_frame = frame_class(master=self.main_frame, controller=self)
        self.current_frame.pack(fill="both", expand=True)

    def logout_action(self):
        self.is_logged_in = False
        self.current_user_role = None
        self.update_nav_buttons()
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        self.show_frame(HomeFrame)

if __name__ == "__main__":
    app = ClinicApp()
    app.mainloop()