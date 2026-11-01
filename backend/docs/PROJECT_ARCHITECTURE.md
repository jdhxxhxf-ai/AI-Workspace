# AI Workspace — Project Architecture

## Overview

AI Workspace Backend is a modular, engine-based architecture designed to evolve into a full AI coding assistant platform (similar to Cursor, Claude Code, OpenHands). Stage 1 establishes the production foundation that all future stages depend on.

## Architecture Pattern

The backend follows **Clean Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│                   API Layer                      │
│         (FastAPI routes, request/response)       │
├─────────────────────────────────────────────────┤
│                  Core Layer                      │
│         (App factory, startup validation)        │
├─────────────────────────────────────────────────┤
│                 Engines Layer                    │
│  agent │ workspace │ indexer │ rag │ llm │ memory   │
│                    tools                         │
├─────────────────────────────────────────────────┤
│              Shared + Config Layer               │
│   (exceptions, logging, responses, settings)   │
└─────────────────────────────────────────────────┘
```

## Engine Responsibilities

| Engine | Responsibility | Stage Status |
|--------|---------------|--------------|
| **Tools** | File, Terminal, Write tool execution | Fully implemented (Stage 1) |
| **Workspace** | Project discovery, scanning, configuration | Fully implemented (Stage 1) |
| **Indexer** | Python AST parsing, dependency analysis, persistent SQLite index | Fully implemented (Stage 2) |
| **RAG** | Vector embeddings, SQLite vector store, AST/heading chunking, hybrid search | Fully implemented (Stage 3) |
| **LLM** | Provider abstraction, Ollama integration | Infrastructure complete (Stage 1) |
| **Memory** | Conversation, workspace, session storage | Interfaces ready (Stage 1) |
| **Agent** | Rule-based planner and executor | Basic implementation (Stage 1) |

## Communication Flow

### Tool Execution Flow
```
Client → POST /tools/execute
  → API (tools/routes.py)
    → ToolRegistry.execute()
      → ToolValidator.validate_arguments()
        → BaseTool.execute()
          → Manager (file/terminal/write)
```

### Agent Execution Flow
```
Client → POST /executor/run
  → API (agent/routes.py)
    → Executor.execute(prompt)
      → Planner.create_plan(prompt)
        → ToolRegistry.execute() for each step
```

### Indexer Flow
```
Client → POST /indexer/scan
  → ProjectScanner.scan()
    → PythonParser.parse() per file
      → ImportAnalyzer, ClassAnalyzer, FunctionAnalyzer
        → DependencyAnalyzer → GraphBuilder.build()
          → IndexRepository.save()
```

## Dependency Graph

```
main.py
  └── core/app.py
        ├── api/router.py
        │     ├── api/workspace/routes → engines/workspace
        │     ├── api/files/routes     → engines/tools/file
        │     ├── api/tools/routes     → engines/tools/registry
        │     ├── api/agent/routes     → engines/agent
        │     └── api/indexer/routes   → engines/indexer
        ├── config/settings.py
        └── shared/logger.py

engines/tools/registry
  ├── engines/tools/loader
  ├── engines/tools/validator
  └── engines/tools/{file,terminal,write}/tool

engines/agent/executor
  ├── engines/agent/planner
  └── engines/tools/registry
```

## Design Decisions

1. **Engine-based modularity** — Each domain (tools, workspace, indexer) is an independent engine that can evolve without affecting others.

2. **Registry pattern for tools** — Tools self-register via `ToolLoader`, enabling future dynamic discovery.

3. **In-memory storage for Stage 1** — Index repository and memory stores use in-memory dicts. Persistent storage deferred to later stages.

4. **Ollama as default LLM** — Local-first approach; OpenAI provider stubbed for future integration.

5. **Startup validation** — Application validates imports, tool registration, and routes on startup for early failure detection.

6. **Structured logging** — All engines log through a centralized logger with file and console output.

7. **Preserved API compatibility** — All original endpoints maintained with identical behavior.
