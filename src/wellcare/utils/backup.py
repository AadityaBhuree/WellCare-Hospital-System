"""Database backup utilities for WellCare Hospital System."""

import datetime
import shutil
from pathlib import Path

from src.wellcare.config import DATABASE_PATH, PROJECT_ROOT
from src.wellcare.logger import logger

BACKUPS_DIR = PROJECT_ROOT / "backups"


def backup_database(destination_dir: str | Path | None = None) -> Path | None:
    """Create a timestamped backup of the local SQLite database.

    Args:
        destination_dir: Optional custom directory to save backup.

    Returns:
        Path to created backup file, or None if backup failed.
    """
    if not DATABASE_PATH.exists():
        logger.warning("Cannot backup database: %s does not exist", DATABASE_PATH)
        return None

    target_dir = Path(destination_dir) if destination_dir else BACKUPS_DIR
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = target_dir / f"clinic_backup_{timestamp}.db"
        shutil.copy2(DATABASE_PATH, backup_filename)
        logger.info("Successfully created database backup: %s", backup_filename)
        return backup_filename
    except Exception as exc:
        logger.error("Failed to create database backup: %s", exc)
        return None
