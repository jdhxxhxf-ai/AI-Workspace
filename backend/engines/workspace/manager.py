"""Workspace manager — central workspace operations."""

from typing import Any

from engines.workspace.config import WorkspaceConfiguration
from engines.workspace.models import WorkspaceConfig, WorkspaceInfo
from engines.workspace.scanner import scan_workspace
from shared.base import BaseManager
from shared.logger import get_logger

logger = get_logger("workspace.manager")


class WorkspaceManager(BaseManager):
    """Manages workspace discovery, configuration, and scanning."""

    def __init__(self) -> None:
        self._config = WorkspaceConfiguration()
        self._active_workspace: str | None = None

    def set_active(self, path: str) -> None:
        """Set the active workspace path."""
        self._active_workspace = path
        logger.info("Active workspace set: %s", path)

    def get_active(self) -> str | None:
        """Get the active workspace path."""
        return self._active_workspace

    def discover(self, path: str) -> WorkspaceInfo:
        """Discover and scan a workspace."""
        info = scan_workspace(path)
        config = WorkspaceConfig(root_path=path, name=path.split("/")[-1] or path.split("\\")[-1])
        self._config.register(config)
        logger.info("Discovered workspace: %s", path)
        return info

    def register_config(self, config: WorkspaceConfig) -> None:
        """Register a workspace configuration."""
        self._config.register(config)

    def get_config(self, path: str) -> WorkspaceConfig | None:
        """Get workspace configuration."""
        return self._config.get(path)

    def get_status(self) -> dict[str, Any]:
        """Return manager status."""
        return {
            "active_workspace": self._active_workspace,
            "registered_workspaces": len(self._config.list_all()),
        }


workspace_manager = WorkspaceManager()
