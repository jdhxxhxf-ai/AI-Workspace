# Import Map

Complete mapping of all import changes from pre-migration to Stage 1.

## Main Entry Point

| Old | New |
|-----|-----|
| `from workspace_engine.workspace.routes import router` | `from api.router import api_router` (via core/app.py) |
| `from tool_engine.file.file_manager.routes import router` | Included in `api_router` |
| `from tool_engine.tools.routes import router` | Included in `api_router` |
| `from agent_engine.planner.routes import router` | Included in `api_router` |
| `from agent_engine.executor.routes import router` | Included in `api_router` |
| `from project_indexer_engine.routes import router` | Included in `api_router` |

## Tool Engine

| Old | New |
|-----|-----|
| `from tool_engine.tools.base import BaseTool` | `from engines.tools.base import BaseTool` |
| `from tool_engine.tools.registry import registry` | `from engines.tools.registry import registry` |
| `from tool_engine.tools.models import ToolRequest` | Defined inline in `api/tools/routes.py` |
| `from tool_engine.tools.file_tool import FileTool` | `from engines.tools.file.tool import FileTool` |
| `from tool_engine.tools.terminal_tool import TerminalTool` | `from engines.tools.terminal.tool import TerminalTool` |
| `from tool_engine.tools.write_tool import WriteTool` | `from engines.tools.write.tool import WriteTool` |
| `from tool_engine.file.file_manager.manager import read_file` | `from engines.tools.file.manager import read_file` |
| `from tool_engine.file.file_manager.models import ReadFileResponse` | `from engines.tools.file.models import ReadFileResponse` |
| `from tool_engine.terminal.terminal_manager.manager import run_command` | `from engines.tools.terminal.manager import run_command` |
| `from tool_engine.write.write_manager.manager import write_file` | `from engines.tools.write.manager import write_file` |

## Workspace Engine

| Old | New |
|-----|-----|
| `from workspace_engine.workspace.scanner import scan_workspace` | `from engines.workspace.scanner import scan_workspace` |
| `from workspace_engine.workspace.models import FileNode, WorkspaceInfo` | `from engines.workspace.models import FileNode, WorkspaceInfo` |
| `from workspace_engine.workspace.routes import router` | `from api.workspace.routes import router` |

## Project Indexer

| Old | New |
|-----|-----|
| `from project_indexer_engine.scanner import ProjectScanner` | `from engines.indexer.scanner import ProjectScanner` |
| `from project_indexer_engine.parser import PythonParser` | `from engines.indexer.parser import PythonParser` |
| `from project_indexer_engine.models import *` | `from engines.indexer.models import *` |
| `from project_indexer_engine.routes import router` | `from api.indexer.routes import router` |

## Agent Engine

| Old | New |
|-----|-----|
| `from agent_engine.planner import planner` | `from engines.agent.planner import planner` |
| `from agent_engine.executor import executor` | `from engines.agent.executor import executor` |
| `from agent_engine.models import *` | `from engines.agent.models import *` |
| `from planner.planner import planner` (broken) | `from engines.agent.planner import planner` |
| `from tools.registry import registry` (broken) | `from engines.tools.registry import registry` |

## New Imports (Stage 1 Additions)

| Module | Import |
|--------|--------|
| Config | `from config.settings import settings` |
| Logging | `from shared.logger import get_logger, setup_logging` |
| Exceptions | `from shared.exceptions import AIWorkspaceError, ToolNotFoundError, ...` |
| Responses | `from shared.responses import APIResponse, HealthResponse` |
| LLM | `from engines.llm.pipeline import LLMPipeline` |
| Memory | `from engines.memory.conversation import ConversationMemory` |
| Tool Loader | `from engines.tools.loader import ToolLoader` |
| Tool Validator | `from engines.tools.validator import ToolValidator` |
| Tool Discovery | `from engines.tools.discovery import ToolDiscovery` |
| Index Analyzers | `from engines.indexer.import_analyzer import ImportAnalyzer` |
| Graph Builder | `from engines.indexer.graph_builder import GraphBuilder` |
| Index Repository | `from engines.indexer.database.repository import index_repository` |
