# Engines Reference

## Tool Engine

**Location**: `engines/tools/`

Professional tool execution framework with registration, validation, loading, and discovery.

### Components

| Component | Class | Description |
|-----------|-------|-------------|
| Base Class | `BaseTool` | Abstract tool with `name`, `description`, `execute()` |
| Metadata | `ToolMetadata` | Tool name, description, version, parameters |
| Registry | `ToolRegistry` | Central registry for tool lookup and execution |
| Loader | `ToolLoader` | Loads and validates default tools |
| Validator | `ToolValidator` | Validates tool instances and arguments |
| Discovery | `ToolDiscovery` | Scans packages for BaseTool subclasses |

### Registered Tools

| Tool | Name | Arguments | Manager |
|------|------|-----------|---------|
| FileTool | `file` | `path: str` | `read_file()` |
| TerminalTool | `terminal` | `command: str` | `run_command()` |
| WriteTool | `write` | `path: str, content: str` | `write_file()` |

### Usage

```python
from engines.tools.registry import registry

result = registry.execute("terminal", command="echo hello")
tools = registry.list_tools()
```

---

## Workspace Engine

**Location**: `engines/workspace/`

Manages workspace discovery, configuration, and scanning.

### Components

| Component | Class | Description |
|-----------|-------|-------------|
| Manager | `WorkspaceManager` | Active workspace, discovery, config |
| Scanner | `scan_workspace()` | Directory structure scanning |
| Config | `WorkspaceConfiguration` | Multi-workspace config storage |
| Models | `WorkspaceInfo`, `FileNode` | Data models |

### Future Capabilities (Stage 2+)
- File watcher integration
- Multiple project support
- Workspace-level settings persistence

---

## Indexer Engine

**Location**: `engines/indexer/`

Full Project Intelligence Engine with AST analysis, persistent SQLite repository, internal module dependency graphs, incremental indexing, symbol searching, and structural context building.

### Components

| Component | Class | Description |
|-----------|-------|-------------|
| Discovery | `ProjectDiscovery` | Manifest files, entry points, and framework detection |
| Scanner | `ProjectScanner` | Safe recursive file discovery with exclusions, file size limits, and SHA-256 hashing |
| Language | `detect_language` | Extension-based language detector |
| Parser | `PythonParser` | AST parser for modules, classes, methods, functions, and symbols |
| Import Analyzer | `ImportAnalyzer` | AST import statement analyzer |
| Class Analyzer | `ClassAnalyzer` | Class definition analyzer |
| Function Analyzer | `FunctionAnalyzer` | Function and method definition analyzer |
| Dependency Analyzer | `DependencyAnalyzer` | Internal module and standard library import resolver |
| Graph Builder | `GraphBuilder` | Builds relationship edges (`IMPORTS`, `INHERITS_FROM`) |
| Database Repository | `IndexRepository` | SQLite storage (`database/project_intelligence.db`) |
| Intelligence Service | `ProjectIntelligenceService` | High-level orchestrator for full/incremental indexing and queries |
| Context Builder | `ProjectContextBuilder` | Constructs compact structural context for downstream consumers |

### Data Flow

```
ProjectScanner → [PythonParser → Analyzers] → GraphBuilder → IndexRepository (SQLite) ↔ ProjectIntelligenceService ↔ API Layer
```

---

## LLM Engine

**Location**: `engines/llm/`

Provider-abstracted LLM infrastructure. Default provider: Ollama.

### Components

| Component | Class | Description |
|-----------|-------|-------------|
| Interface | `LLMProvider` | Abstract provider with generate/is_available/list_models |
| Ollama | `OllamaProvider` | Local Ollama integration via HTTP |
| OpenAI | `OpenAIProvider` | Stub for future implementation |
| Pipeline | `LLMPipeline` | Request orchestration |
| Prompt Builder | `PromptBuilder` | Structured prompt construction |

### Configuration

Environment variables:
- `LLM_PROVIDER` — Provider name (default: `ollama`)
- `OLLAMA_BASE_URL` — Ollama server URL
- `OLLAMA_MODEL` — Default model name

---

## Memory Engine

**Location**: `engines/memory/`

Interface-only memory storage for Stage 1.

### Components

| Component | Class | Description |
|-----------|-------|-------------|
| Interface | `MemoryStore` | Abstract get/set/delete/clear |
| Conversation | `ConversationMemory` | Message history per session |
| Workspace | `WorkspaceMemory` | Workspace-level context |
| Cache | `TemporaryCache` | In-memory key-value cache |
| Session | `SessionStorage` | UUID-based session management |

---

## Agent Engine

**Location**: `engines/agent/`

Rule-based planner and executor for tool orchestration.

### Components

| Component | Class | Description |
|-----------|-------|-------------|
| Planner | `Planner` | Creates ExecutionPlan from prompts |
| Executor | `Executor` | Executes plans via tool registry |

### Supported Prompt Patterns

| Pattern | Tool | Example |
|---------|------|---------|
| `read {path}` | file | `read main.py` |
| `terminal {command}` | terminal | `terminal echo hello` |
| `write \| {path} \| {content}` | write | `write \| test.txt \| hello` |

---

## RAG & Knowledge Engine

**Location**: `engines/rag/`

Production-quality local, code-aware Retrieval-Augmented Generation (RAG) and Knowledge Engine.

### Components

| Component | Class / Function | Description |
|-----------|------------------|-------------|
| Domain Models | `KnowledgeDocument`, `KnowledgeChunk`, `ChunkMetadata`, `RetrievalResult`, `ContextPayload`, `RAGStats` | Domain data transfer objects |
| Document Extractor | `DocumentExtractor` | Filesystem reader integrating Stage 2 AST metadata |
| Python Chunker | `PythonCodeChunker` | Code-aware AST boundary chunker preserving symbol context |
| Markdown Chunker | `MarkdownChunker` | Heading hierarchy section chunker |
| Generic Chunker | `GenericChunker` | Bounded sliding window chunker |
| Embedding Interface | `EmbeddingProvider` | Abstract provider interface |
| Ollama Provider | `OllamaEmbeddingProvider` | Local HTTP integration via `/api/embed` / `/api/embeddings` |
| Mock Provider | `MockEmbeddingProvider` | Deterministic SHA-256 derived pseudo-vectors for testing |
| Vector Store | `SQLiteVectorStore` | Local persistent SQLite vector database (`database/vector_knowledge.db`) |
| Hybrid Retriever | `HybridRetriever` | Combines cosine similarity with symbol, path, and token matching |
| Index Manager | `RAGIndexManager` | Full and incremental RAG indexing orchestrator |
| Context Builder | `KnowledgeContextBuilder` | Formats retrieved chunks into Markdown context blocks |
| Domain Service | `KnowledgeRetrievalService` | High-level facade for API routes and downstream engines |

### Data Flow

```
Filesystem + Stage 2 AST → DocumentExtractor → Python/Markdown/Generic Chunker → EmbeddingProvider → SQLiteVectorStore ↔ HybridRetriever ↔ KnowledgeContextBuilder
```

