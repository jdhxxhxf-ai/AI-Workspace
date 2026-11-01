"""Centralized application configuration."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "AI Workspace API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Paths
    backend_root: Path = Path(__file__).resolve().parent.parent
    logs_dir: Path = backend_root / "logs"
    storage_dir: Path = backend_root / "storage"
    database_dir: Path = backend_root / "database"

    # LLM
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Workspace
    default_workspace_path: str = ""

    # Indexer
    indexer_ignore_dirs: set[str] = {
        ".git", ".venv", "__pycache__", "node_modules",
        "dist", "build", ".idea", ".vscode",
    }
    indexer_db_path: Path = database_dir / "project_intelligence.db"
    indexer_max_file_size: int = 2 * 1024 * 1024
    indexer_search_limit: int = 50

    # RAG & Knowledge Engine
    rag_enabled: bool = True
    rag_embedding_provider: str = "ollama"
    rag_embedding_model: str = "nomic-embed-text"
    rag_vector_db_path: Path = database_dir / "vector_knowledge.db"
    rag_top_k: int = 10
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 64
    rag_batch_size: int = 32

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


settings = Settings()
