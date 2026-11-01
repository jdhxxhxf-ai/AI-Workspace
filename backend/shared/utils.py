"""Shared utility functions."""

from pathlib import Path
from typing import Any


def ensure_directory(path: Path) -> Path:
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_dict_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    return data.get(key, default)
