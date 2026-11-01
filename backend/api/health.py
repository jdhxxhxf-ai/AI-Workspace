"""Health check endpoints."""

from fastapi import APIRouter

from config.settings import settings
from shared.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        engines={
            "tools": "ready",
            "workspace": "ready",
            "indexer": "ready",
            "llm": "ready",
            "memory": "ready",
            "agent": "ready",
        },
    )
