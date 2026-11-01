"""Tool loading and registration."""

from engines.tools.base import BaseTool
from engines.tools.file.tool import FileTool
from engines.tools.terminal.tool import TerminalTool
from engines.tools.validator import ToolValidator
from engines.tools.write.tool import WriteTool
from shared.logger import get_logger

logger = get_logger("tools.loader")


class ToolLoader:
    """Loads and validates tools into the registry."""

    DEFAULT_TOOLS: list[type[BaseTool]] = [
        FileTool,
        TerminalTool,
        WriteTool,
    ]

    @classmethod
    def load_defaults(cls) -> list[BaseTool]:
        """Instantiate all default tools."""
        tools: list[BaseTool] = []
        for tool_cls in cls.DEFAULT_TOOLS:
            tool = tool_cls()
            ToolValidator.validate_tool(tool)
            tools.append(tool)
            logger.info("Loaded tool: %s", tool.name)
        return tools

    @staticmethod
    def load_tool(tool_cls: type[BaseTool]) -> BaseTool:
        """Load and validate a single tool class."""
        tool = tool_cls()
        ToolValidator.validate_tool(tool)
        return tool
