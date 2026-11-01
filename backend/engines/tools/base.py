"""Tool base class."""

from abc import ABC, abstractmethod
from typing import Any

from engines.tools.metadata import ToolMetadata


class BaseTool(ABC):
    """Abstract base class for all tools."""

    name: str
    description: str
    version: str = "1.0.0"

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given arguments."""

    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name=self.name,
            description=self.description,
            version=self.version,
        )
