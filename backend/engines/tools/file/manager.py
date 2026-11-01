"""File read/write operations."""

from pathlib import Path

from engines.tools.file.models import ReadFileResponse
from shared.constants import DEFAULT_ENCODING


def read_file(path: str) -> ReadFileResponse:
    """Read a file and return its contents."""
    file = Path(path)

    if not file.exists():
        raise FileNotFoundError(path)

    if file.is_dir():
        raise IsADirectoryError(path)

    text = file.read_text(encoding=DEFAULT_ENCODING)

    return ReadFileResponse(
        path=str(file),
        content=text,
        size=file.stat().st_size,
    )
