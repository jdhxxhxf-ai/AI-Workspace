"""Tool input validation."""

from typing import Any

from engines.tools.base import BaseTool
from shared.exceptions import ToolValidationError


class ToolValidator:
    """Validates tool instances and execution arguments."""

    @staticmethod
    def validate_tool(tool: BaseTool) -> None:
        """Validate that a tool has required attributes."""
        if not tool.name:
            raise ToolValidationError("Tool must have a name")
        if not tool.description:
            raise ToolValidationError(f"Tool '{tool.name}' must have a description")

    @staticmethod
    def validate_arguments(tool: BaseTool, arguments: dict[str, Any]) -> None:
        """Validate arguments before tool execution."""
        if tool.name == "file" and "path" not in arguments:
            raise ToolValidationError("File tool requires 'path' argument")
        if tool.name == "terminal" and "command" not in arguments:
            raise ToolValidationError("Terminal tool requires 'command' argument")
        if tool.name == "write":
            if "path" not in arguments:
                raise ToolValidationError("Write tool requires 'path' argument")
            if "content" not in arguments:
                raise ToolValidationError("Write tool requires 'content' argument")
