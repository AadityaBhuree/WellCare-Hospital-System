"""Database operations for the WellCare Hospital Management System.

Uses SQLite for efficient, lightweight local data storage with caching and audit logging.
"""

import sqlite3
from collections import Counter
from typing import Any, cast

from src.wellcare.cache import TTLCache
from src.wellcare.config import DATABASE_PATH
from src.wellcare.logger import logger
from src.wellcare.models import Appointment, Bill, Patient


class Database:
    """Handles all persistent data operations with connection management and caching."""

    def __init__(self) -> None:
        self.conn: sqlite3.Connection | None = None
        self.cur: sqlite3.Cursor | None = None
        self._cache = TTLCache(ttl_seconds=3.0)
        try:
            self.conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.cur = self.conn.cursor()
            self._create_table()
        except Exception as err:
            logger.error("Database Connection Error: %s", err)

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close SQLite cursor and connection."""
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            logger.error("Error closing database connection: %s", e)
        finally:
            self.cur = None
            self.conn = None

    def _create_table(self) -> None:
        if self.cur is None:
            return

        # Patients table
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

        # Appointments table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_name TEXT,
                department TEXT,
                date TEXT,
                time_slot TEXT,
                status TEXT DEFAULT 'Scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            );
        """)

        # Doctors table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                specialization TEXT,
                phone TEXT,
                email TEXT,
                available_days TEXT,
                is_active INTEGER DEFAULT 1
            );
        """)

        # Billing table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                appointment_id INTEGER,
                amount REAL,
                description TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            );
        """)

        # Medical records table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_name TEXT,
                diagnosis TEXT,
                treatment TEXT,
                notes TEXT,
                visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            );
        """)

        # Audit log table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Performance Indexes
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_patients_mobile ON patients(mobile);")
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_patients_last_name ON patients(last_name);"
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);"
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);"
        )
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id);"
        )

        if self.conn:
            self.conn.commit()

    def log_action(self, user_id: str, action: str, details: str = "") -> None:
        """Log audit trail event."""
        if self.cur is None or self.conn is None:
            return
        try:
            self.cur.execute(
                "INSERT INTO audit_log(user_id, action, details) VALUES (?, ?, ?)",
                (user_id, action, details),
            )
            self.conn.commit()
        except Exception as e:
            logger.error("Failed to log audit action: %s", e)

    def add_patient(self, data: tuple[str, ...]) -> bool:
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute(
                """
                INSERT INTO patients(
                    first_name, last_name, age, gender, blood_group, weight,
                    mobile, email, address, pincode, symptoms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                data,
            )
            self.conn.commit()
            self._cache.invalidate()
            return True
        except Exception as e:
            logger.error("Failed to add patient: %s", e)
            return False

    def get_patient_by_id(self, patient_id: int | str) -> Patient | None:
        """Fetch full patient object by ID."""
        if self.cur is None:
            return None
        self.cur.execute(
            """
            SELECT id, first_name, last_name, age, gender, blood_group,
                   weight, mobile, email, address, pincode, symptoms, created_at
            FROM patients WHERE id = ?
        """,
            (patient_id,),
        )
        row = self.cur.fetchone()
        if not row:
            return None
        return Patient(
            id=row[0],
            first_name=row[1] or "",
            last_name=row[2] or "",
            age=int(row[3]) if row[3] and str(row[3]).isdigit() else 0,
            gender=row[4] or "",
            blood_group=row[5] or "",
            weight=float(row[6]) if row[6] and str(row[6]).replace(".", "", 1).isdigit() else 0.0,
            mobile=row[7] or "",
            email=row[8] or "",
            address=row[9] or "",
            pincode=row[10] or "",
            symptoms=row[11] or "",
        )

    def get_all_patients(self) -> list[Patient]:
        """Fetch all patient objects ordered by ID."""
        if self.cur is None:
            return []
        self.cur.execute(
            """
            SELECT id, first_name, last_name, age, gender, blood_group,
                   weight, mobile, email, address, pincode, symptoms, created_at
            FROM patients ORDER BY id ASC
        """
        )
        rows = self.cur.fetchall()
        patients = []
        for r in rows:
            patients.append(
                Patient(
                    id=r[0],
                    first_name=r[1] or "",
                    last_name=r[2] or "",
                    age=int(r[3]) if r[3] and str(r[3]).isdigit() else 0,
                    gender=r[4] or "",
                    blood_group=r[5] or "",
                    weight=float(r[6]) if r[6] and str(r[6]).replace(".", "", 1).isdigit() else 0.0,
                    mobile=r[7] or "",
                    email=r[8] or "",
                    address=r[9] or "",
                    pincode=r[10] or "",
                    symptoms=r[11] or "",
                )
            )
        return patients

    def update_patient(self, patient_id: int | str, data: tuple[str, ...]) -> bool:
        """Update existing patient record fields."""
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute(
                """
                UPDATE patients
                SET first_name=?, last_name=?, age=?, gender=?, blood_group=?,
                    weight=?, mobile=?, email=?, address=?, pincode=?, symptoms=?
                WHERE id=?
            """,
                (*data, patient_id),
            )
            self.conn.commit()
            self._cache.invalidate()
            return self.cur.rowcount > 0
        except Exception as e:
            logger.error("Failed to update patient %s: %s", patient_id, e)
            return False

    def search_patient(self, keyword: str) -> list[tuple[Any, ...]]:
        if self.cur is None:
            return []
        safe_keyword = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        self.cur.execute(
            """
            SELECT id, first_name, last_name, age, mobile, symptoms
            FROM patients
            WHERE first_name LIKE ? ESCAPE '\\' OR last_name LIKE ? ESCAPE '\\'
        """,
            (f"%{safe_keyword}%", f"%{safe_keyword}%"),
        )
        return self.cur.fetchall()

    def delete_patient(self, patient_id: int | str) -> bool:
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
            self.cur.execute("DELETE FROM billing WHERE patient_id = ?", (patient_id,))
            self.cur.execute("DELETE FROM medical_records WHERE patient_id = ?", (patient_id,))
            self.cur.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
            self.conn.commit()
            self._cache.invalidate()
            return self.cur.rowcount > 0
        except Exception as e:
            logger.error("Failed to delete patient %s: %s", patient_id, e)
            return False

    def get_dashboard_stats(self) -> dict[str, Any]:
        """Return aggregated statistics for the dashboard with caching."""
        cached_stats = self._cache.get("dashboard_stats")
        if cached_stats is not None:
            return cast(dict[str, Any], cached_stats)

        stats: dict[str, Any] = {
            "total": 0,
            "today": 0,
            "genders": [],
            "blood_groups": [],
            "ages": [],
            "symptoms": [],
            "trends": [],
            "recent": [],
        }

        if self.cur is None:
            return stats

        self.cur.execute("SELECT COUNT(*) FROM patients")
        row = self.cur.fetchone()
        stats["total"] = row[0] if row else 0

        self.cur.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
        stats["genders"] = self.cur.fetchall()

        self.cur.execute("SELECT blood_group, COUNT(*) FROM patients GROUP BY blood_group")
        stats["blood_groups"] = self.cur.fetchall()

        self.cur.execute("SELECT age FROM patients")
        stats["ages"] = [row[0] for row in self.cur.fetchall()]

        self.cur.execute("SELECT COUNT(*) FROM patients WHERE date(created_at) = date('now')")
        row_today = self.cur.fetchone()
        stats["today"] = row_today[0] if row_today else 0

        self.cur.execute("""
            SELECT date(created_at) as d, COUNT(*)
            FROM patients
            WHERE created_at >= date('now', '-6 days')
            GROUP BY d
            ORDER BY d ASC
        """)
        stats["trends"] = self.cur.fetchall()

        self.cur.execute(
            "SELECT id, first_name, last_name, mobile FROM patients ORDER BY id DESC LIMIT 5"
        )
        stats["recent"] = self.cur.fetchall()

        self.cur.execute("SELECT symptoms FROM patients")
        stats["symptoms"] = [row[0] for row in self.cur.fetchall() if row[0]]

        self._cache.set("dashboard_stats", stats)
        return stats

    def get_symptom_frequencies(self, top_n: int = 5) -> list[tuple[str, int]]:
        """Get the most common symptom keywords."""
        if self.cur is None:
            return []
        self.cur.execute("SELECT symptoms FROM patients")
        symptom_words: list[str] = []
        for row in self.cur.fetchall():
            if row[0]:
                for word in str(row[0]).replace(",", " ").split():
                    if len(word) > 3:
                        symptom_words.append(word.lower())
        return Counter(symptom_words).most_common(top_n)

    def add_appointment(self, appt: Appointment) -> bool:
        """Add a new appointment record."""
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute(
                """
                INSERT INTO appointments(
                    patient_id, doctor_name, department, date, time_slot, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    appt.patient_id,
                    appt.doctor_name,
                    appt.department,
                    appt.date,
                    appt.time_slot,
                    appt.status,
                    appt.notes,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error("Failed to add appointment: %s", e)
            return False

    def get_appointments(self, date_filter: str = "") -> list[tuple[Any, ...]]:
        """Get appointments list, optionally filtered by date."""
        if self.cur is None:
            return []
        if date_filter:
            self.cur.execute(
                """
                SELECT a.id, p.first_name || ' ' || p.last_name, a.doctor_name,
                       a.department, a.date, a.time_slot, a.status, a.notes
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                WHERE a.date = ?
                ORDER BY a.time_slot ASC
            """,
                (date_filter,),
            )
        else:
            self.cur.execute("""
                SELECT a.id, p.first_name || ' ' || p.last_name, a.doctor_name,
                       a.department, a.date, a.time_slot, a.status, a.notes
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                ORDER BY a.id DESC LIMIT 50
            """)
        return self.cur.fetchall()

    def update_appointment_status(self, appt_id: int | str, status: str) -> bool:
        """Update appointment status."""
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute(
                "UPDATE appointments SET status = ? WHERE id = ?",
                (status, appt_id),
            )
            self.conn.commit()
            return self.cur.rowcount > 0
        except Exception as e:
            logger.error("Failed to update appointment %s status: %s", appt_id, e)
            return False

    def add_doctor(
        self,
        name: str,
        specialization: str,
        phone: str = "",
        email: str = "",
        available_days: str = "Mon,Tue,Wed,Thu,Fri",
    ) -> bool:
        """Add a new doctor to the database."""
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute(
                """
                INSERT INTO doctors (name, specialization, phone, email, available_days, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (name, specialization, phone, email, available_days),
            )
            self.conn.commit()
            logger.info("Doctor added successfully: %s (%s)", name, specialization)
            return True
        except Exception as err:
            logger.error("Error adding doctor %s: %s", name, err)
            return False

    def get_all_doctors(self, active_only: bool = True) -> list[tuple[Any, ...]]:
        """Retrieve list of doctors from database."""
        if self.cur is None:
            return []
        query = (
            "SELECT id, name, specialization, phone, email, available_days, is_active FROM doctors"
        )
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name ASC"
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_doctors_by_specialization(self, spec: str) -> list[tuple[Any, ...]]:
        """Filter active doctors by medical specialization."""
        if self.cur is None:
            return []
        self.cur.execute(
            """
            SELECT id, name, specialization, phone, email, available_days, is_active
            FROM doctors
            WHERE is_active = 1 AND LOWER(specialization) LIKE ?
            ORDER BY name ASC
            """,
            (f"%{spec.lower()}%",),
        )
        return self.cur.fetchall()

    def toggle_doctor_status(self, doctor_id: int, is_active: bool) -> bool:
        """Enable or disable a doctor's active status."""
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute(
                "UPDATE doctors SET is_active = ? WHERE id = ?",
                (1 if is_active else 0, doctor_id),
            )
            self.conn.commit()
            return self.cur.rowcount > 0
        except Exception as err:
            logger.error("Error toggling status for doctor %d: %s", doctor_id, err)
            return False

    # ── Billing Operations ──────────────────────────────────────────────

    def add_bill(self, bill: Bill) -> int | None:
        """Create a new billing record and return inserted bill ID."""
        if self.cur is None or self.conn is None:
            return None
        try:
            self.cur.execute(
                """
                INSERT INTO billing (patient_id, appointment_id, amount, description, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    bill.patient_id,
                    bill.appointment_id,
                    bill.amount,
                    bill.description,
                    bill.status,
                ),
            )
            self.conn.commit()
            bill_id = self.cur.lastrowid
            logger.info("Created bill #%s for patient ID %s", bill_id, bill.patient_id)
            return bill_id
        except Exception as err:
            logger.error("Error creating bill for patient %s: %s", bill.patient_id, err)
            return None

    def get_bills(self, patient_id: int | None = None) -> list[tuple[Any, ...]]:
        """Retrieve list of billing records joined with patient names."""
        if self.cur is None:
            return []
        query = """
            SELECT b.id, b.patient_id, (p.first_name || ' ' || p.last_name) as patient_name,
                   b.appointment_id, b.amount, b.description, b.status, b.created_at
            FROM billing b
            LEFT JOIN patients p ON b.patient_id = p.id
        """
        params: list[Any] = []
        if patient_id is not None:
            query += " WHERE b.patient_id = ?"
            params.append(patient_id)
        query += " ORDER BY b.id DESC"
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def update_bill_status(self, bill_id: int, status: str) -> bool:
        """Update payment status of a bill."""
        if self.cur is None or self.conn is None:
            return False
        try:
            self.cur.execute(
                "UPDATE billing SET status = ? WHERE id = ?",
                (status, bill_id),
            )
            self.conn.commit()
            return self.cur.rowcount > 0
        except Exception as err:
            logger.error("Error updating bill #%d status: %s", bill_id, err)
            return False

    def get_billing_stats(self) -> dict[str, float | int]:
        """Compute summary statistics for hospital financial billing."""
        if self.cur is None:
            return {
                "total_revenue": 0.0,
                "pending_amount": 0.0,
                "paid_count": 0,
                "pending_count": 0,
            }
        self.cur.execute("SELECT status, amount FROM billing")
        rows = self.cur.fetchall()
        total_rev = 0.0
        pending_amt = 0.0
        paid_cnt = 0
        pending_cnt = 0

        for status, amt in rows:
            amount = float(amt or 0.0)
            if status == "Paid":
                total_rev += amount
                paid_cnt += 1
            elif status in ("Pending", "Partial"):
                pending_amt += amount
                pending_cnt += 1

        return {
            "total_revenue": total_rev,
            "pending_amount": pending_amt,
            "paid_count": paid_cnt,
            "pending_count": pending_cnt,
        }

    # ── Medical Records Operations ──────────────────────────────────────

    def add_medical_record(
        self,
        patient_id: int,
        doctor_name: str,
        diagnosis: str,
        treatment: str,
        notes: str = "",
    ) -> int | None:
        """Create a new medical history record for a patient."""
        if self.cur is None or self.conn is None:
            return None
        try:
            self.cur.execute(
                """
                INSERT INTO medical_records (patient_id, doctor_name, diagnosis, treatment, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (patient_id, doctor_name, diagnosis, treatment, notes),
            )
            self.conn.commit()
            record_id = self.cur.lastrowid
            logger.info("Added medical record #%s for patient #%s", record_id, patient_id)
            return record_id
        except Exception as err:
            logger.error("Error adding medical record for patient %s: %s", patient_id, err)
            return None

    def get_patient_medical_history(
        self, patient_id: int | None = None
    ) -> list[tuple[Any, ...]]:
        """Retrieve diagnostic medical timeline history for a patient or all patients."""
        if self.cur is None:
            return []
        query = """
            SELECT m.id, m.patient_id, (p.first_name || ' ' || p.last_name) as patient_name,
                   m.doctor_name, m.diagnosis, m.treatment, m.notes, m.visit_date
            FROM medical_records m
            LEFT JOIN patients p ON m.patient_id = p.id
        """
        params: list[Any] = []
        if patient_id is not None:
            query += " WHERE m.patient_id = ?"
            params.append(patient_id)
        query += " ORDER BY m.id DESC"
        self.cur.execute(query, params)
        return self.cur.fetchall()
