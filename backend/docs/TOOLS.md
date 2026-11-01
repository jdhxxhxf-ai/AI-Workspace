# Tools Reference

## Overview

The Tool Engine provides a professional framework for registering, validating, and executing tools. All tools inherit from `BaseTool` and are managed through the central `ToolRegistry`.

## Architecture

```
ToolLoader.load_defaults()
  → ToolValidator.validate_tool()
    → ToolRegistry.register()
      → ToolRegistry.execute()
        → ToolValidator.validate_arguments()
          → BaseTool.execute()
            → Manager function
```

## File Tool

**Name**: `file`
**Description**: Read project files

### Arguments
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Absolute or relative file path |

### Returns
```json
{
  "path": "/path/to/file.py",
  "content": "file contents...",
  "size": 1234
}
```

### Errors
- `FileNotFoundError` — File does not exist
- `IsADirectoryError` — Path is a directory

---

## Terminal Tool

**Name**: `terminal`
**Description**: Execute terminal commands

### Arguments
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | Yes | Shell command to execute |

### Returns
```json
{
  "command": "echo hello",
  "return_code": 0,
  "stdout": "hello\n",
  "stderr": ""
}
```

---

## Write Tool

**Name**: `write`
**Description**: Write text to a file

### Arguments
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Target file path |
| `content` | string | Yes | Content to write |

### Returns
```json
{
  "path": "/path/to/file.txt",
  "size": 13,
  "message": "File written successfully."
}
```

### Behavior
- Creates parent directories if they do not exist
- Overwrites existing files
- Uses UTF-8 encoding

---

## Tool Registry API

### Register a Custom Tool

```python
from engines.tools.base import BaseTool
from engines.tools.registry import registry

class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something"

    def execute(self, **kwargs):
        return {"result": "done"}

registry.register(MyTool())
```

### List Registered Tools

```python
tools = registry.list_tools()
# Returns list of ToolMetadata
```

### Execute a Tool

```python
result = registry.execute("file", path="main.py")
```

## Tool Discovery

Future tools can be auto-discovered from packages:

```python
from engines.tools.discovery import ToolDiscovery

tool_classes = ToolDiscovery.discover_tools("engines.tools")
```

## Validation

The `ToolValidator` ensures:
1. Every tool has a `name` and `description`
2. Required arguments are present before execution
3. Tool-specific argument schemas are satisfied
