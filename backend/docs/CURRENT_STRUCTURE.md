# Current Structure (Pre-Migration)

This documents the backend structure before Stage 1 refactoring.

## Directory Layout

```
backend/
├── main.py                          # Entry point (broken imports)
├── agent_engine/
│   ├── planner.py                   # Rule-based planner
│   ├── executor.py                  # Plan executor (broken imports)
│   ├── models.py                    # Pydantic models
│   └── routes.py                    # Planner routes only
├── tool_engine/
│   ├── tools/
│   │   ├── base.py                  # BaseTool ABC
│   │   ├── file_tool.py
│   │   ├── terminal_tool.py
│   │   ├── write_tool.py
│   │   ├── registry.py            # ToolRegistry
│   │   ├── models.py
│   │   └── routes.py
│   ├── file/file_manager/
│   │   ├── manager.py               # read_file()
│   │   ├── models.py
│   │   └── routes.py
│   ├── terminal/terminal_manager/
│   │   └── manager.py               # run_command()
│   └── write/write_manager/
│       └── manager.py               # write_file()
├── workspace_engine/
│   └── workspace/
│       ├── scanner.py
│       ├── models.py
│       └── routes.py
└── project_indexer_engine/
    ├── scanner.py                   # ProjectScanner
    ├── parser.py                    # PythonParser (monolithic)
    ├── models.py
    └── routes.py
```

## Known Issues

1. **No `__init__.py` files** — Invalid Python packages throughout
2. **Broken imports in main.py** — References non-existent `planner.routes` and `executor.routes`
3. **Broken imports in executor.py** — Uses `planner.planner` and `tools.registry`
4. **Duplicate nesting** — `file/file_manager/`, `terminal/terminal_manager/`, `write/write_manager/`
5. **No centralized config** — Hardcoded values scattered
6. **No logging infrastructure** — No structured logging
7. **No shared layer** — No exceptions, response models, or validators
8. **Monolithic parser** — All AST analysis in one file
9. **Missing executor route** — Only planner route existed
10. **No LLM or Memory engines** — Not present

## Working Endpoints (when imports fixed)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root status |
| GET | `/health` | Health check |
| GET | `/workspace/scan` | Scan workspace |
| GET | `/files/read` | Read file |
| POST | `/tools/execute` | Execute tool |
| POST | `/planner/plan` | Create plan |

## Dependencies

- fastapi
- uvicorn
- pydantic
