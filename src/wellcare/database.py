"""
Database operations for the WellCare Hospital Management System.

Uses SQLite for efficient, lightweight local data storage.
"""

import sqlite3
from collections import Counter
from typing import Any

from src.wellcare.config import DATABASE_PATH
from src.wellcare.logger import logger


class Database:
    """Handles all persistent data operations."""

    def __init__(self) -> None:
        self.conn: sqlite3.Connection | None = None
        self.cur: sqlite3.Cursor | None = None
        try:
            self.conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
            self.cur = self.conn.cursor()
            self._create_table()
        except Exception as err:
            logger.error("Database Connection Error: %s", err)

    def _create_table(self) -> None:
        if self.cur is None:
            return
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
        if self.conn:
            self.conn.commit()

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
            return True
        except Exception as e:
            logger.error("Failed to add patient: %s", e)
            return False

    def search_patient(self, keyword: str) -> list[tuple[Any, ...]]:
        if self.cur is None:
            return []
        # Escape special LIKE pattern characters
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
            return self.cur.rowcount > 0
        except Exception as e:
            logger.error("Failed to delete patient %s: %s", patient_id, e)
            return False

    def get_dashboard_stats(self) -> dict[str, Any]:
        """Return aggregated statistics for the dashboard."""
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
