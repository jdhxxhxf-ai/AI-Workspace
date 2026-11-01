"""Standard API response models."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""

    success: bool = True
    data: T | None = None
    message: str = "OK"


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str
    code: str = "INTERNAL_ERROR"
    detail: Any | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = Field(default="0.1.0")
    engines: dict[str, str] = Field(default_factory=dict)
