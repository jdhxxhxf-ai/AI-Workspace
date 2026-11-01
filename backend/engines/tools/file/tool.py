"""File read tool."""

from typing import Any

from engines.tools.base import BaseTool
from engines.tools.file.manager import read_file


class FileTool(BaseTool):
    """Tool for reading project files."""

    name = "file"
    description = "Read project files"

    def execute(self, **kwargs: Any) -> Any:
        path = kwargs.get("path")
        if not path:
            raise ValueError("Missing required argument: path")
        return read_file(path)
