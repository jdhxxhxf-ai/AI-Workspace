"""Shared validation utilities."""

from pathlib import Path


def validate_path_exists(path: str) -> Path:
    """Validate that a path exists and return it as Path."""
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(path)
    return resolved


def validate_file_path(path: str) -> Path:
    """Validate that a path exists and is a file."""
    resolved = validate_path_exists(path)
    if resolved.is_dir():
        raise IsADirectoryError(path)
    return resolved


def validate_directory_path(path: str) -> Path:
    """Validate that a path exists and is a directory."""
    resolved = validate_path_exists(path)
    if not resolved.is_dir():
        raise NotADirectoryError(path)
    return resolved
