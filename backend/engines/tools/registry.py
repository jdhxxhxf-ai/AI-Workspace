"""Central tool registry."""

from typing import Any

from engines.tools.base import BaseTool
from engines.tools.loader import ToolLoader
from engines.tools.metadata import ToolMetadata
from engines.tools.validator import ToolValidator
from shared.exceptions import ToolNotFoundError
from shared.logger import get_logger

logger = get_logger("tools.registry")


class ToolRegistry:
    """Registry for tool registration, lookup, and execution."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        ToolValidator.validate_tool(tool)
        self._tools[tool.name] = tool
        logger.info("Registered tool: %s", tool.name)

    def get(self, tool_name: str) -> BaseTool | None:
        """Get a tool by name."""
        return self._tools.get(tool_name)

    def list_tools(self) -> list[ToolMetadata]:
        """List metadata for all registered tools."""
        return [tool.get_metadata() for tool in self._tools.values()]

    def execute(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a tool by name with arguments."""
        tool = self._tools.get(tool_name)
        if tool is None:
            raise ToolNotFoundError(tool_name)

        ToolValidator.validate_arguments(tool, kwargs)
        logger.info("Executing tool: %s", tool_name)
        return tool.execute(**kwargs)

    def initialize(self) -> None:
        """Load and register all default tools."""
        for tool in ToolLoader.load_defaults():
            self.register(tool)


registry = ToolRegistry()
registry.initialize()
