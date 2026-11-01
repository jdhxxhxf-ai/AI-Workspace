"""Terminal execution tool."""

from typing import Any

from engines.tools.base import BaseTool
from engines.tools.terminal.manager import run_command


class TerminalTool(BaseTool):
    """Tool for executing terminal commands."""

    name = "terminal"
    description = "Execute terminal commands."

    def execute(self, **kwargs: Any) -> Any:
        command = kwargs.get("command")
        if not command:
            raise ValueError("Missing required argument: command")
        return run_command(command)
