"""Tool engine tests."""

from engines.tools.file.tool import FileTool
from engines.tools.registry import registry
from engines.tools.terminal.tool import TerminalTool
from engines.tools.write.tool import WriteTool


def test_file_tool_metadata():
    tool = FileTool()
    meta = tool.get_metadata()
    assert meta.name == "file"


def test_terminal_tool_metadata():
    tool = TerminalTool()
    meta = tool.get_metadata()
    assert meta.name == "terminal"


def test_write_tool_metadata():
    tool = WriteTool()
    meta = tool.get_metadata()
    assert meta.name == "write"


def test_registry_execute_terminal():
    result = registry.execute("terminal", command="echo hello")
    assert result["return_code"] == 0
    assert "hello" in result["stdout"]
