# API Reference

Base URL: `http://localhost:8000`

## Health

### GET `/`
Root status check.

**Response**:
```json
{
  "status": "running",
  "message": "AI Workspace Backend is running",
  "version": "0.1.0"
}
```

### GET `/health`
Detailed health check with engine status.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "engines": {
    "tools": "ready",
    "workspace": "ready",
    "indexer": "ready",
    "llm": "ready",
    "memory": "ready",
    "agent": "ready"
  }
}
```

---

## Workspace

### GET `/workspace/scan?path={path}`
Scan a workspace directory.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | Directory path to scan |

**Response**:
```json
{
  "root": "/path/to/workspace",
  "total_files": 42,
  "total_directories": 8,
  "items": [
    {"name": "main.py", "path": "/path/to/workspace/main.py", "is_dir": false}
  ]
}
```

**Errors**: 404 if path not found

---

## Files

### GET `/files/read?path={path}`
Read a file by path.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | Yes | File path |

**Response**:
```json
{
  "path": "/path/to/file.py",
  "content": "file contents",
  "size": 1234
}
```

**Errors**: 404 (not found), 400 (is directory)

---

## Tools

### POST `/tools/execute`
Execute a registered tool.

**Request Body**:
```json
{
  "tool": "terminal",
  "arguments": {
    "command": "echo hello"
  }
}
```

**Response**: Tool-specific result object

**Errors**: 400 (tool not found, validation error)

### GET `/tools/list`
List all registered tools.

**Response**:
```json
{
  "tools": [
    {"name": "file", "description": "Read project files", "version": "1.0.0"},
    {"name": "terminal", "description": "Execute terminal commands.", "version": "1.0.0"},
    {"name": "write", "description": "Write text to a file.", "version": "1.0.0"}
  ]
}
```

---

## Agent

### POST `/planner/plan`
Create an execution plan from a natural language prompt.

**Request Body**:
```json
{
  "prompt": "read main.py"
}
```

**Response**:
```json
{
  "steps": [
    {"tool": "file", "arguments": {"path": "main.py"}}
  ]
}
```

**Errors**: 400 (no suitable tool found)

### POST `/executor/run`
Create and execute a plan from a prompt.

**Request Body**:
```json
{
  "prompt": "terminal echo hello"
}
```

**Response**:
```json
{
  "plan": {
    "steps": [{"tool": "terminal", "arguments": {"command": "echo hello"}}]
  },
  "results": [
    {"tool": "terminal", "result": {"command": "echo hello", "return_code": 0, "stdout": "hello\n", "stderr": ""}}
  ]
}
```

---

## Indexer (Project Intelligence Engine)

### POST `/indexer/scan?project_path={path}`
Perform full scan and index of a project directory.

### POST `/indexer/refresh?project_path={path}`
Perform incremental refresh using SHA-256 content hashes.

### GET `/indexer/indexes`
List all stored project indexes in SQLite.

### GET `/indexer/project?project_path={path}`
Return project summary (languages, file counts, symbol counts, entry points).

### GET `/indexer/files?project_path={path}&language={lang}&limit={limit}`
List indexed project files.

### GET `/indexer/file?project_path={path}&path={relative_path}`
Return structural AST intelligence for a single file (symbols, imports, docstring).

### GET `/indexer/symbols/search?project_path={path}&q={query}&symbol_type={type}&limit={limit}`
Search symbols by name (functions, classes, methods, variables, constants).

### GET `/indexer/dependencies?project_path={path}&path={relative_path}`
Return direct dependencies for a file/module.

### GET `/indexer/dependents?project_path={path}&path={relative_path}`
Return reverse dependencies (files that depend on this file/module).

### GET `/indexer/graph?project_path={path}`
Return structural dependency graph (nodes and edges).

### GET `/indexer/context?project_path={path}&focus_path={focus_path}`
Return compact structural project context payload for downstream engines.

---

## RAG & Knowledge Engine

### POST `/rag/index`
Perform full RAG indexing run over a project workspace.

**Request Body**:
```json
{
  "project_path": "/path/to/project"
}
```

### POST `/rag/refresh`
Perform incremental RAG indexing based on Stage 2 content hashes.

**Request Body**:
```json
{
  "project_path": "/path/to/project"
}
```

### GET `/rag/status`
Return status of RAG engine, embedding provider, and vector store.

### GET `/rag/stats?project_path={path}`
Return total chunk counts and metadata for a project in RAG vector store.

### POST `/rag/search`
Perform hybrid semantic and lexical search over indexed project knowledge.

**Request Body**:
```json
{
  "project_path": "/path/to/project",
  "query": "function_name",
  "limit": 10
}
```

### POST `/rag/context`
Retrieve and format structured context payload for AI Agents.

**Request Body**:
```json
{
  "project_path": "/path/to/project",
  "query": "how is authentication handled?",
  "limit": 10
}
```

### DELETE `/rag/project?project_path={path}`
Delete all indexed RAG vectors and file hash tracking for a project.

---

## Error Format

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

## Prompt Patterns

| Pattern | Example | Tool Used |
|---------|---------|-----------|
| `read {path}` | `read main.py` | file |
| `terminal {cmd}` | `terminal ls -la` | terminal |
| `write \| {path} \| {content}` | `write \| out.txt \| hello` | write |

