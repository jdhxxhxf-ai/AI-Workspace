# Roadmap

## Stage 1 — Foundation (COMPLETE)

Build the production-ready backend foundation.

- [x] Enterprise architecture with engine-based modularity
- [x] Tool Engine (registry, loader, validator, discovery)
- [x] Workspace Engine (manager, scanner, config)
- [x] Indexer Engine (scanner, parser, analyzers, graph builder, database)
- [x] LLM Engine (provider interface, Ollama, pipeline)
- [x] Memory Engine (interfaces, conversation, workspace, cache, session)
- [x] Agent Engine (planner, executor)
- [x] Shared layer (exceptions, logging, responses, validators)
- [x] API layer (organized routes, consistent responses)
- [x] Configuration (environment variables, settings)
- [x] Import and package refactoring
- [x] Documentation
- [x] Validation

---

## Stage 2 — Project Intelligence Engine (COMPLETE)

Build deterministic static project understanding and persistent index.

- [x] Persistent SQLite index storage (`database/project_intelligence.db`)
- [x] Project Discovery (manifests, entry points, language stats)
- [x] Professional Project Scanner with configurable exclusions, file size limits, and SHA-256 hashing
- [x] Extension-based Language Detection
- [x] Deep Python AST static analysis (modules, classes, methods, functions, decorators, docstrings, symbols)
- [x] Module, Class, Function, Method, Variable, and Constant symbol extraction (`constant` vs `variable`)
- [x] Internal Python module import resolution (`internal`, `stdlib`, `third_party`, `unresolved`)
- [x] Direct and reverse dependency query capabilities
- [x] Structural relationship graph (`IMPORTS`, `INHERITS_FROM`)
- [x] Incremental reindexing (`POST /indexer/refresh`) with SHA-256 content hashes
- [x] High-level `ProjectIntelligenceService` and `ProjectContextBuilder`
- [x] 11 REST API endpoints for Project Intelligence
- [x] Complete automated test suite (29 tests, 100% passing)

---

## Stage 3 — RAG & Knowledge Engine (COMPLETE)

Build 100% local, code-aware Retrieval-Augmented Generation (RAG) and Knowledge Engine.

- [x] Document extraction pipeline with Stage 2 AST integration
- [x] Python AST code-aware chunker (preserves functions, classes, methods, line ranges)
- [x] Markdown heading hierarchy structure-aware chunker
- [x] Generic text sliding-window chunker
- [x] Abstract `EmbeddingProvider` interface with `OllamaEmbeddingProvider` and `MockEmbeddingProvider`
- [x] Zero-network offline testing enforcement with `MockEmbeddingProvider`
- [x] Local persistent SQLite vector database (`backend/database/vector_knowledge.db`)
- [x] Cosine similarity search and metadata filtering
- [x] Project workspace isolation in vector store and queries
- [x] Hybrid semantic and lexical retrieval (`0.6 * vector + 0.4 * lexical` with symbol match boosting)
- [x] Deterministic score sorting and result deduplication
- [x] Incremental RAG indexing (skip unchanged, re-embed changed, purge deleted files)
- [x] Structured context builder (`KnowledgeContextBuilder`) for AI Agent prompts
- [x] 7 REST API endpoints (`/rag/index`, `/rag/refresh`, `/rag/status`, `/rag/stats`, `/rag/search`, `/rag/context`, `/rag/project`)
- [x] Complete automated test suite (41 tests total, 100% passing)

---

## Stage 4 — Coding Agent & Chat Interface


Build the autonomous coding agent.

- [ ] Multi-step task execution
- [ ] Code editing tool (AST-aware patches)
- [ ] Diff generation and application
- [ ] Test runner integration
- [ ] Error recovery and retry logic
- [ ] Task planning with LLM
- [ ] Progress tracking and reporting
- [ ] Sandbox execution environment

---

## Stage 5 — Multi-Agent

Build multi-agent orchestration.

- [ ] Agent roles (planner, coder, reviewer, tester)
- [ ] Inter-agent communication protocol
- [ ] Task delegation and coordination
- [ ] Git integration (branch, commit, PR)
- [ ] Code review agent
- [ ] Parallel agent execution
- [ ] Agent memory sharing

---

## Stage 6 — Automation

Build automation and external tool integration.

- [ ] Docker integration (container management)
- [ ] Browser automation (Playwright)
- [ ] CI/CD pipeline integration
- [ ] Scheduled task runner
- [ ] Webhook and event system
- [ ] Plugin architecture for custom tools
- [ ] Long-running task management

---

## Stage 7 — Production

Production hardening and deployment.

- [ ] Authentication and authorization
- [ ] Rate limiting and throttling
- [ ] Database migrations
- [ ] Monitoring and metrics (Prometheus)
- [ ] Error tracking (Sentry)
- [ ] Docker deployment
- [ ] Kubernetes manifests
- [ ] Load testing and optimization
- [ ] API versioning
- [ ] Comprehensive test suite (>80% coverage)
