"""File write tool."""

from typing import Any

from engines.tools.base import BaseTool
from engines.tools.write.manager import write_file


class WriteTool(BaseTool):
    """Tool for writing text to files."""

    name = "write"
    description = "Write text to a file."

    def execute(self, **kwargs: Any) -> Any:
        path = kwargs.get("path")
        content = kwargs.get("content")
        if not path:
            raise ValueError("Missing required argument: path")
        if content is None:
            raise ValueError("Missing required argument: content")
        return write_file(path, content)
