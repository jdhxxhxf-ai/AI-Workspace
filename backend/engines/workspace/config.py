"""Workspace configuration management."""

from engines.workspace.models import WorkspaceConfig


class WorkspaceConfiguration:
    """Manages workspace configuration settings."""

    def __init__(self) -> None:
        self._configs: dict[str, WorkspaceConfig] = {}

    def register(self, config: WorkspaceConfig) -> None:
        """Register a workspace configuration."""
        self._configs[config.root_path] = config

    def get(self, root_path: str) -> WorkspaceConfig | None:
        """Get configuration for a workspace."""
        return self._configs.get(root_path)

    def list_all(self) -> list[WorkspaceConfig]:
        """List all registered workspace configurations."""
        return list(self._configs.values())
