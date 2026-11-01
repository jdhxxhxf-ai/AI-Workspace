# Modules Reference

## API Layer (`api/`)

| Module | Purpose |
|--------|---------|
| `router.py` | Aggregates all route modules into a single router |
| `health.py` | Health check endpoint with engine status |
| `workspace/routes.py` | Workspace scan endpoint |
| `files/routes.py` | File read endpoint |
| `tools/routes.py` | Tool execution and listing endpoints |
| `agent/routes.py` | Planner and executor endpoints |
| `indexer/routes.py` | Project indexing endpoints |
| `rag/routes.py` | RAG indexing, retrieval, search, context, and status endpoints |
| `rag/schemas.py` | RAG API request and response Pydantic models |

## Core Layer (`core/`)

| Module | Purpose |
|--------|---------|
| `app.py` | FastAPI application factory with lifespan management |
| `startup.py` | Import, tool, and route validation on startup |

## Config Layer (`config/`)

| Module | Purpose |
|--------|---------|
| `settings.py` | Pydantic Settings with environment variable support |

## Shared Layer (`shared/`)

| Module | Purpose |
|--------|---------|
| `base.py` | BaseEngine and BaseManager abstract classes |
| `constants.py` | Application-wide constants |
| `exceptions.py` | Custom exception hierarchy |
| `logger.py` | Structured logging setup |
| `responses.py` | Standard API response models |
| `utils.py` | Utility functions |
| `validators.py` | Path validation utilities |

## Engine: Agent (`engines/agent/`)

| Module | Purpose |
|--------|---------|
| `planner.py` | Rule-based plan creation from prompts |
| `executor.py` | Plan execution via tool registry |
| `models.py` | PlannerRequest, ExecutorRequest, ExecutionPlan, PlanStep |

## Engine: Workspace (`engines/workspace/`)

| Module | Purpose |
|--------|---------|
| `manager.py` | WorkspaceManager — discovery, config, active workspace |
| `scanner.py` | Directory scanning logic |
| `config.py` | WorkspaceConfiguration management |
| `models.py` | FileNode, WorkspaceInfo, WorkspaceConfig |

## Engine: Indexer (`engines/indexer/`)

| Module | Purpose |
|--------|---------|
| `scanner.py` | ProjectScanner — recursive Python file discovery |
| `parser.py` | PythonParser — orchestrates analyzers |
| `import_analyzer.py` | AST import statement extraction |
| `class_analyzer.py` | AST class definition extraction |
| `function_analyzer.py` | AST function definition extraction |
| `dependency_analyzer.py` | Import dependency edge building |
| `graph_builder.py` | ProjectIndex with dependency graph |
| `models.py` | All indexer data models |
| `database/models.py` | IndexRecord, IndexMetadata |
| `database/repository.py` | In-memory index storage |

## Engine: LLM (`engines/llm/`)

| Module | Purpose |
|--------|---------|
| `provider.py` | LLMProvider abstract interface |
| `ollama_provider.py` | Ollama local LLM implementation |
| `openai_provider.py` | OpenAI stub for future stages |
| `config.py` | LLMConfig model |
| `prompt_builder.py` | Structured prompt construction |
| `pipeline.py` | LLM request orchestration |

## Engine: Memory (`engines/memory/`)

| Module | Purpose |
|--------|---------|
| `interfaces.py` | MemoryStore abstract interface |
| `conversation.py` | ConversationMemory — message history |
| `workspace.py` | WorkspaceMemory — workspace context |
| `cache.py` | TemporaryCache — in-memory cache |
| `session.py` | SessionStorage — session management |

## Engine: Tools (`engines/tools/`)

| Module | Purpose |
|--------|---------|
| `base.py` | BaseTool abstract class |
| `metadata.py` | ToolMetadata dataclass |
| `registry.py` | ToolRegistry — registration and execution |
| `loader.py` | ToolLoader — default tool loading |
| `validator.py` | ToolValidator — input validation |
| `discovery.py` | ToolDiscovery — package scanning |
| `file/tool.py` | FileTool implementation |
| `file/manager.py` | read_file() function |
| `terminal/tool.py` | TerminalTool implementation |
| `terminal/manager.py` | run_command() function |
| `write/tool.py` | WriteTool implementation |
| `write/manager.py` | write_file() function |

## Engine: RAG (`engines/rag/`)

| Module | Purpose |
|--------|---------|
| `models.py` | KnowledgeDocument, KnowledgeChunk, ChunkMetadata, RetrievalResult, RAGStats, ContextPayload |
| `config.py` | RAGConfig model and settings mapping |
| `domain/extractor.py` | DocumentExtractor — filesystem reader with Stage 2 AST integration |
| `chunking/python_chunker.py` | PythonCodeChunker — AST code symbol boundary chunker |
| `chunking/markdown_chunker.py` | MarkdownChunker — heading structure section chunker |
| `chunking/generic_chunker.py` | GenericChunker — bounded line-aligned sliding window chunker |
| `embeddings/provider.py` | EmbeddingProvider abstract class and get_embedding_provider factory |
| `embeddings/ollama_provider.py` | OllamaEmbeddingProvider — local HTTP vector embedding client |
| `embeddings/mock_provider.py` | MockEmbeddingProvider — deterministic offline test provider |
| `storage/vector_store.py` | VectorStore abstract class and SQLiteVectorStore database backend |
| `retrieval/hybrid_retriever.py` | HybridRetriever — vector similarity + symbol lexical match engine |
| `indexing/manager.py` | RAGIndexManager — full and incremental RAG index manager |
| `services/context_builder.py` | KnowledgeContextBuilder — structured prompt context assembly |
| `services/retrieval_service.py` | KnowledgeRetrievalService — high-level domain orchestrator facade |

