"""Workspace memory — interface for Stage 1."""

from typing import Any


class WorkspaceMemory:
    """Stores workspace-level context and metadata."""

    def __init__(self) -> None:
        self._context: dict[str, Any] = {}

    def set_context(self, key: str, value: Any) -> None:
        """Store workspace context."""
        self._context[key] = value

    def get_context(self, key: str) -> Any | None:
        """Retrieve workspace context."""
        return self._context.get(key)

    def get_all(self) -> dict[str, Any]:
        """Get all workspace context."""
        return dict(self._context)

    def clear(self) -> None:
        """Clear workspace memory."""
        self._context.clear()
