"""File tool models."""

from pydantic import BaseModel


class ReadFileResponse(BaseModel):
    """Response from reading a file."""

    path: str
    content: str
    size: int
