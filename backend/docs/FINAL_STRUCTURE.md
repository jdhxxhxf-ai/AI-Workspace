# Final Structure (Stage 3 — RAG & Knowledge Engine)

## Directory Layout

```
backend/
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment configuration template
├── api/                             # API Layer
│   ├── __init__.py
│   ├── router.py                    # Central route aggregator
│   ├── health.py                    # Health check endpoint
│   ├── workspace/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── files/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── agent/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── indexer/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── rag/                         # Stage 3 RAG API
│       ├── __init__.py
│       ├── routes.py
│       └── schemas.py
├── core/                            # Application Core
│   ├── __init__.py
│   ├── app.py                       # FastAPI app factory
│   └── startup.py                   # Startup validation
├── config/                          # Configuration
│   ├── __init__.py
│   └── settings.py                  # Centralized settings
├── shared/                          # Shared Layer
│   ├── __init__.py
│   ├── base.py                      # BaseEngine, BaseManager
│   ├── constants.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── responses.py
│   ├── utils.py
│   └── validators.py
├── engines/                         # Engine Layer
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── planner.py
│   │   ├── executor.py
│   │   └── models.py
│   ├── workspace/
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   ├── scanner.py
│   │   ├── config.py
│   │   └── models.py
│   ├── indexer/
│   │   ├── __init__.py
│   │   ├── scanner.py
│   │   ├── parser.py
│   │   ├── import_analyzer.py
│   │   ├── class_analyzer.py
│   │   ├── function_analyzer.py
│   │   ├── dependency_analyzer.py
│   │   ├── graph_builder.py
│   │   ├── models.py
│   │   └── database/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       └── repository.py
│   ├── rag/                         # Stage 3 RAG Engine
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── config.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   └── extractor.py
│   │   ├── chunking/
│   │   │   ├── __init__.py
│   │   │   ├── python_chunker.py
│   │   │   ├── markdown_chunker.py
│   │   │   └── generic_chunker.py
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   ├── provider.py
│   │   │   ├── ollama_provider.py
│   │   │   └── mock_provider.py
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   └── vector_store.py
│   │   ├── retrieval/
│   │   │   ├── __init__.py
│   │   │   └── hybrid_retriever.py
│   │   ├── indexing/
│   │   │   ├── __init__.py
│   │   │   └── manager.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── context_builder.py
│   │       └── retrieval_service.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── provider.py
│   │   ├── ollama_provider.py
│   │   ├── openai_provider.py
│   │   ├── config.py
│   │   ├── prompt_builder.py
│   │   └── pipeline.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   ├── conversation.py
│   │   ├── workspace.py
│   │   ├── cache.py
│   │   └── session.py
│   └── tools/
│       ├── __init__.py
│       ├── base.py
│       ├── metadata.py
│       ├── registry.py
│       ├── loader.py
│       ├── validator.py
│       ├── discovery.py
│       ├── file/
│       │   ├── __init__.py
│       │   ├── tool.py
│       │   ├── manager.py
│       │   └── models.py
│       ├── terminal/
│       │   ├── __init__.py
│       │   ├── tool.py
│       │   └── manager.py
│       └── write/
│           ├── __init__.py
│           ├── tool.py
│           └── manager.py
├── database/                        # Persistent SQLite databases
│   ├── __init__.py
│   ├── project_intelligence.db
│   └── vector_knowledge.db
├── storage/                         # File storage utilities
│   └── __init__.py
├── logs/                            # Application logs
│   └── app.log
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_startup.py
│   ├── test_tools.py
│   ├── test_indexer_scanner.py
│   ├── test_indexer_parser.py
│   ├── test_indexer_database.py
│   ├── test_indexer_service.py
│   ├── test_indexer_api.py
│   └── rag/
│       ├── __init__.py
│       ├── test_extractor.py
│       ├── test_chunker.py
│       ├── test_embeddings.py
│       ├── test_vector_store.py
│       ├── test_retrieval.py
│       ├── test_incremental.py
│       └── test_api.py
└── docs/                            # Stage & Architecture Reports
    └── (all .md files)
```

## Metrics Summary

- **Total Python packages**: 32 (all with `__init__.py`)
- **Total Python modules**: ~75
- **Total API endpoints**: 27 (Health: 2, Workspace: 1, Files: 1, Tools: 2, Agent: 2, Indexer: 11, RAG: 7, Delete: 1)
- **Registered tools**: 3 (file, terminal, write)
- **Test cases**: 41 (100% passing)

