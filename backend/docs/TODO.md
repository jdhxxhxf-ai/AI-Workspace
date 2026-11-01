# TODO

## Stage 1 — Completed

- [x] Analyze entire backend codebase
- [x] Design enterprise architecture
- [x] Create shared layer (config, logging, exceptions, responses)
- [x] Build Tool Engine with registry, loader, validator, discovery
- [x] Build Workspace Engine with manager and config
- [x] Build Indexer Engine with analyzers and graph builder
- [x] Build LLM Engine with Ollama provider
- [x] Build Memory Engine interfaces
- [x] Build Agent Engine (planner + executor)
- [x] Create API layer with organized routes
- [x] Create core app factory with startup validation
- [x] Fix all broken imports
- [x] Add all missing `__init__.py` files
- [x] Remove legacy directory structure
- [x] Validate server startup
- [x] Validate all endpoints
- [x] Validate tool registration and execution
- [x] Generate documentation
- [x] Fix route validation for FastAPI `_IncludedRouter`
- [x] Add pytest to requirements and validate test suite

## Stage 2 — Completed

- [x] Persistent SQLite index storage (`database/project_intelligence.db`)
- [x] Project Discovery (manifests, entry points, language stats)
- [x] Professional Project Scanner with exclusions & SHA-256 content hashes
- [x] Python AST static parser (modules, classes, methods, functions, constants, docstrings)
- [x] Module import resolution (`internal`, `stdlib`, `third_party`, `unresolved`)
- [x] Incremental reindexing (`POST /indexer/refresh`)
- [x] Structural context builder and REST API

## Stage 3 — Completed (RAG & Knowledge Engine)

- [x] Document extraction pipeline with Stage 2 AST metadata integration
- [x] Code-aware Python AST chunker (symbol boundaries)
- [x] Structure-aware Markdown heading chunker
- [x] Generic sliding window line-aligned chunker
- [x] Abstract `EmbeddingProvider` interface with `OllamaEmbeddingProvider` and `MockEmbeddingProvider`
- [x] Persistent SQLite local vector storage (`database/vector_knowledge.db`)
- [x] Project workspace isolation in vector store & queries
- [x] Hybrid retrieval (vector cosine similarity + symbol/path lexical boosting)
- [x] Deterministic score ranking and chunk deduplication
- [x] Incremental RAG indexing (skip unchanged, re-embed changed, purge deleted)
- [x] Structured `KnowledgeContextBuilder` payload assembly
- [x] REST API endpoints (`/rag/index`, `/rag/refresh`, `/rag/status`, `/rag/stats`, `/rag/search`, `/rag/context`, `/rag/project`)
- [x] 41/41 automated pytest suite passing

## Stage 4 — Next Up (Coding Agent / Chat Interface)

- [ ] WebSocket streaming
- [ ] LLM-powered planner
- [ ] OpenAI provider implementation
- [ ] Chat session persistence
- [ ] Autonomous task execution & AST code patches

## Technical Debt

- [x] Add pytest to requirements and CI
- [x] Add `.env.example` file
- [ ] Add pre-commit hooks for linting
- [x] Increase test coverage (41 tests passing)
- [ ] Add API rate limiting middleware

