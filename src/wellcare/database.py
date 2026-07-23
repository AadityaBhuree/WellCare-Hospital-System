"""Database operations for the WellCare Hospital Management System.

Uses SQLite for efficient, lightweight local data storage with caching and audit logging.
"""

import sqlite3
from collections import Counter
from typing import Any, cast


from src.wellcare.cache import TTLCache
from src.wellcare.config import DATABASE_PATH
from src.wellcare.logger import logger
from src.wellcare.models import Patient


class Database:
    """Handles all persistent data operations with connection management and caching."""

    def __init__(self) -> None:
        self.conn: sqlite3.Connection | None = None
        self.cur: sqlite3.Cursor | None = None
        self._cache = TTLCache(ttl_seconds=3.0)
        try:
            self.conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
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
        stats["total"] = self.cur.fetchone()[0]

        self.cur.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
        stats["genders"] = self.cur.fetchall()

        self.cur.execute("SELECT blood_group, COUNT(*) FROM patients GROUP BY blood_group")
        stats["blood_groups"] = self.cur.fetchall()

        self.cur.execute("SELECT age FROM patients")
        stats["ages"] = [row[0] for row in self.cur.fetchall()]

        self.cur.execute("SELECT COUNT(*) FROM patients WHERE date(created_at) = date('now')")
        stats["today"] = self.cur.fetchone()[0]

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
