"""Logging configuration for the application with console and rotating file handlers."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGS_DIR = Path("logs")


def setup_logger(name: str = "wellcare") -> logging.Logger:
    """Configure and return a logger instance with console and rotating file handlers."""
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(logging.INFO)

    if not logger_instance.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger_instance.addHandler(console_handler)

        # Rotating file handler
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            log_file = LOGS_DIR / "wellcare.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger_instance.addHandler(file_handler)
        except Exception as exc:
            logger_instance.warning("Could not set up file logger: %s", exc)

    return logger_instance


logger = setup_logger()
