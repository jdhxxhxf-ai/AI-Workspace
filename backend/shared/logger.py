"""Structured logging configuration."""

import logging
import sys
from pathlib import Path

from config.settings import settings
from shared.utils import ensure_directory


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    ensure_directory(settings.logs_dir)

    log_file = settings.logs_dir / "app.log"

    formatter = logging.Formatter(settings.log_format)

    root_logger = logging.getLogger("ai_workspace")
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not root_logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named child logger."""
    return logging.getLogger(f"ai_workspace.{name}")
