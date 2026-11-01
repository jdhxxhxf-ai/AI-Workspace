"""File API routes."""

from fastapi import APIRouter, HTTPException

from engines.tools.file.manager import read_file

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/read")
def read(path: str):
    """Read a file by path."""
    try:
        return read_file(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except IsADirectoryError:
        raise HTTPException(status_code=400, detail="Path is a directory")
