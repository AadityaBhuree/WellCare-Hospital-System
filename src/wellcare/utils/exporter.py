"""Data export utilities for exporting patient records to CSV and JSON formats."""

import csv
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from src.wellcare.logger import logger
from src.wellcare.models import Patient


def export_patients_to_csv(patients: Sequence[Patient], output_path: str | Path) -> bool:
    """Export a list of Patient objects to a CSV file.

    Args:
        patients: Sequence of Patient dataclass instances.
        output_path: Path where the CSV file should be saved.

    Returns:
        bool: True if export succeeded, False otherwise.
    """
    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "id",
            "first_name",
            "last_name",
            "age",
            "gender",
            "blood_group",
            "weight",
            "mobile",
            "email",
            "address",
            "pincode",
            "symptoms",
            "created_at",
        ]
        with open(path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for p in patients:
                writer.writerow(p.to_dict())
        logger.info("Successfully exported %d patients to CSV: %s", len(patients), path)
        return True
    except Exception as exc:
        logger.error("Failed to export patients to CSV (%s): %s", path, exc)
        return False


def export_patients_to_json(patients: Sequence[Patient], output_path: str | Path) -> bool:
    """Export a list of Patient objects to a JSON file.

    Args:
        patients: Sequence of Patient dataclass instances.
        output_path: Path where the JSON file should be saved.

    Returns:
        bool: True if export succeeded, False otherwise.
    """
    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data: list[dict[str, Any]] = [p.to_dict() for p in patients]
        with open(path, mode="w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        logger.info("Successfully exported %d patients to JSON: %s", len(patients), path)
        return True
    except Exception as exc:
        logger.error("Failed to export patients to JSON (%s): %s", path, exc)
        return False
