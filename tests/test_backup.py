"""Tests for database backup utility."""

from pathlib import Path
from unittest.mock import patch

from src.wellcare.utils.backup import backup_database


class TestDatabaseBackup:
    """Tests for backup_database function."""

    def test_backup_database_success(self, tmp_path: Path) -> None:
        source_db = tmp_path / "clinic.db"
        source_db.write_text("dummy db content")

        backup_dir = tmp_path / "backups"

        with patch("src.wellcare.utils.backup.DATABASE_PATH", source_db):
            result = backup_database(destination_dir=backup_dir)
            assert result is not None
            assert result.exists()
            assert result.read_text() == "dummy db content"

    def test_backup_database_file_not_found(self, tmp_path: Path) -> None:
        missing_db = tmp_path / "non_existent.db"

        with patch("src.wellcare.utils.backup.DATABASE_PATH", missing_db):
            result = backup_database(destination_dir=tmp_path)
            assert result is None
