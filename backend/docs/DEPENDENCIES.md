# Dependencies

## Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.110.0 | Web framework |
| uvicorn | >=0.27.0 | ASGI server |
| pydantic | >=2.0.0 | Data validation and settings |
| pydantic-settings | >=2.0.0 | Environment-based configuration |
| httpx | >=0.27.0 | HTTP client for Ollama provider |
| python-dotenv | >=1.0.0 | .env file loading |

## Installation

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Running

```bash
python -m uvicorn main:app --reload
```

## Internal Dependencies

### Engine Dependency Graph

```
api → engines → shared → config

engines/agent → engines/tools
engines/indexer → config (settings)
engines/llm → config (settings)
engines/tools → shared
engines/workspace → shared
core → api, config, shared
```

### No Circular Dependencies

All imports flow in one direction:
- `api` imports from `engines` and `shared`
- `engines` imports from `shared` and `config`
- `shared` imports from `config`
- `config` has no internal imports
- `core` imports from `api`, `config`, `shared`

## Future Dependencies (Later Stages)

| Package | Stage | Purpose |
|---------|-------|---------|
| openai | Stage 3 | OpenAI API integration |
| chromadb / qdrant | Stage 2 | Vector database for RAG |
| sentence-transformers | Stage 2 | Embeddings |
| websockets | Stage 3 | Streaming chat |
| sqlalchemy | Stage 2 | Persistent database |
| watchdog | Stage 2 | File watcher |
| gitpython | Stage 5 | Git integration |
| docker | Stage 6 | Docker integration |
| playwright | Stage 6 | Browser automation |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| APP_NAME | AI Workspace API | Application name |
| APP_VERSION | 0.1.0 | Application version |
| DEBUG | false | Debug mode |
| LLM_PROVIDER | ollama | LLM provider name |
| OLLAMA_BASE_URL | http://localhost:11434 | Ollama server URL |
| OLLAMA_MODEL | llama3 | Default Ollama model |
| OPENAI_API_KEY | (empty) | OpenAI API key |
| OPENAI_MODEL | gpt-4 | OpenAI model name |
| LOG_LEVEL | INFO | Logging level |
| DEFAULT_WORKSPACE_PATH | (empty) | Default workspace path |
| RAG_ENABLED | true | Enable RAG Engine |
| RAG_EMBEDDING_PROVIDER | ollama | Embedding provider (ollama / mock) |
| RAG_EMBEDDING_MODEL | nomic-embed-text | Embedding model name |
| RAG_VECTOR_DB_PATH | database/vector_knowledge.db | SQLite vector database file path |
| RAG_TOP_K | 10 | Default top-k search limit |
| RAG_CHUNK_SIZE | 512 | Target chunk token/char length |
| RAG_CHUNK_OVERLAP | 64 | Chunk overlap size |

Create a `.env` file in the `backend/` directory to override defaults.

