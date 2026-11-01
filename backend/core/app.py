"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.router import api_router
from config.settings import settings
from core.startup import run_startup_validation
from shared.logger import get_logger, setup_logging

logger = get_logger("core.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    setup_logging()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    run_startup_validation(app)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.include_router(api_router)

    @app.get("/")
    def root():
        return {
            "status": "running",
            "message": "AI Workspace Backend is running",
            "version": settings.app_version,
        }

    return app
