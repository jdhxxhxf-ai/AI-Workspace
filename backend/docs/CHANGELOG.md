## [0.3.0] — 2026-08-10 — Stage 3 RAG & Knowledge Engine

### Added

- Code-aware, structure-preserving Retrieval-Augmented Generation (RAG) and Knowledge Engine (`backend/engines/rag/`).
- Document extraction pipeline (`DocumentExtractor`) integrating Stage 2 AST metadata (`ast_symbols`, `ast_imports`) for source code, documentation, configuration, and test files.
- AST symbol boundary Python code chunker (`PythonCodeChunker`) isolating functions, classes, methods, constants, and line ranges.
- Heading structure Markdown chunker (`MarkdownChunker`) preserving `#`, `##`, `###` sections and line range bounds.
- Bounded sliding window line-aligned text chunker (`GenericChunker`).
- Provider-agnostic embedding interface (`EmbeddingProvider`) with factory `get_embedding_provider()`.
- HTTP-based Ollama embedding provider (`OllamaEmbeddingProvider`) using `/api/embed` and `/api/embeddings` with L2 norm normalization.
- Deterministic 384-dim mock embedding provider (`MockEmbeddingProvider`) for zero-network, reproducible offline testing.
- Local persistent SQLite vector store (`SQLiteVectorStore` in `backend/database/vector_knowledge.db`) storing float blobs, chunk metadata, and SHA-256 file hashes.
- Incremental RAG indexing manager (`RAGIndexManager`) leveraging SHA-256 content hashes to skip unchanged files, re-embed modified files, insert new files, and delete removed file vectors.
- Hybrid retrieval engine (`HybridRetriever`) combining cosine vector similarity ($0.6$) with exact symbol, qualified name, relative path, and content token lexical matches ($0.4$).
- Structured knowledge context builder (`KnowledgeContextBuilder`) formatting Markdown prompt context blocks and metadata sources (`ContextPayload`).
- High-level domain service facade (`KnowledgeRetrievalService`) exposed via 7 REST API endpoints (`POST /rag/index`, `POST /rag/refresh`, `GET /rag/status`, `GET /rag/stats`, `POST /rag/search`, `POST /rag/context`, `DELETE /rag/project`).
- Comprehensive RAG test suite (`backend/tests/rag/`) with 12 new tests bringing total backend coverage to 41 passing tests (100%).
- Complete Stage 3 specification and engineering documentation (`docs/STAGE_3_REPORT.md` and `backend/docs/STAGE_3_REPORT.md`).

## [0.2.0] — 2026-08-09 — Stage 2 Project Intelligence Engine

### Added

- Persistent SQLite project index storage (`backend/database/project_intelligence.db`) with schema initialization, index creation, foreign key CASCADE constraints, and transactional execution.
- Deterministic project discovery (`ProjectDiscovery`): detects project root, languages, configuration files, manifests (`requirements.txt`, `pyproject.toml`, `package.json`), entry points (`main.py`, `app.py`), and framework indicators.
- Professional project scanner (`ProjectScanner`) with configurable exclusions (`.venv`, `node_modules`, `.git`, `.idea`, etc.), file size limits, symlink safety, and SHA-256 content hashing per file.
- Extended Python AST static parser (`PythonParser`): symbol extraction for modules, classes, sync/async methods, functions, parameters, return annotations, decorators, docstrings, and class/module constants & variables (`constant` vs `variable`).
- Graceful malformed Python handling logging `parse_error` per file without aborting project scan.
- Internal module import resolution (`DependencyAnalyzer`) classifying imports as `internal`, `stdlib`, `third_party`, or `unresolved`.
- Reverse dependency lookups (`get_dependents`) and class inheritance graph mapping (`INHERITS_FROM`).
- Incremental reindexing (`POST /indexer/refresh`) using SHA-256 content hashes to skip unchanged files and reparse only modified/new files.
- High-level domain service (`ProjectIntelligenceService`) and structural context payload builder (`ProjectContextBuilder`).
- 9 new Project Intelligence REST endpoints (`/indexer/refresh`, `/indexer/project`, `/indexer/files`, `/indexer/file`, `/indexer/symbols/search`, `/indexer/dependencies`, `/indexer/dependents`, `/indexer/graph`, `/indexer/context`).
- Comprehensive automated test suite (`test_indexer_database.py`, `test_indexer_service.py`, `test_indexer_api.py`) bringing test count to 29 tests (100% passing).
- Detailed engineering report `STAGE_2_REPORT.md`.

## [0.1.0] — 2026-08-01 — Stage 1 Foundation

### Added

- Enterprise architecture with engine-based modularity
- **API Layer**: Organized routes in `api/` with central router
- **Core Layer**: FastAPI app factory with lifespan and startup validation
- **Config Layer**: Pydantic Settings with environment variable support
- **Shared Layer**: Exceptions, logging, responses, validators, base classes
- **Tool Engine**: Registry, loader, validator, discovery, metadata
- **Workspace Engine**: Manager, scanner, configuration
- **Indexer Engine**: Scanner, parser, 4 analyzers, graph builder, database repository
- **LLM Engine**: Provider interface, Ollama provider, OpenAI stub, prompt builder, pipeline
- **Memory Engine**: Conversation, workspace, cache, session interfaces
- **Agent Engine**: Rule-based planner and executor
- New endpoint: `GET /tools/list`
- New endpoint: `POST /executor/run`
- New endpoint: `GET /indexer/indexes`
- Enhanced `/health` with engine status
- Dependency graph in indexer output
- Structured logging to `logs/app.log`
- Startup validation (imports, tools, routes)
- Test suite with startup and tool tests
- Complete documentation (13 documents)

### Changed

- Restructured from fragmented `*_engine/` layout to unified `engines/` architecture
- Moved routes from engine internals to dedicated `api/` layer
- Split monolithic parser into specialized analyzers
- Flattened duplicate nesting (`file_manager/`, `terminal_manager/`, `write_manager/`)
- All imports updated to new package paths

### Fixed

- Broken imports in `main.py` (planner.routes, executor.routes)
- Broken imports in `executor.py` (planner.planner, tools.registry)
- Missing `__init__.py` in all packages
- Missing executor API route
- Invalid Python package structure
- Route validation failing with FastAPI `_IncludedRouter` (now uses OpenAPI schema)
- Test suite route assertion incompatible with FastAPI route objects

### Removed

- `tool_engine/` directory (migrated)
- `workspace_engine/` directory (migrated)
- `project_indexer_engine/` directory (migrated)
- `agent_engine/` directory (migrated)

### Dependencies Added

- pydantic-settings >= 2.0.0
- httpx >= 0.27.0
- pytest >= 8.0.0
