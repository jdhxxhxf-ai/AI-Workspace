"""File write operations."""

from pathlib import Path

from shared.constants import DEFAULT_ENCODING


def write_file(path: str, content: str) -> dict[str, str | int]:
    """Write content to a file, creating parent directories if needed."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding=DEFAULT_ENCODING)

    return {
        "path": str(file_path),
        "size": file_path.stat().st_size,
        "message": "File written successfully.",
    }
