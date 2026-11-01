"""Abstract EmbeddingProvider interface and factory."""

from abc import ABC, abstractmethod

from engines.rag.config import RAGConfig
from shared.logger import get_logger

logger = get_logger("rag.embeddings")


class EmbeddingProvider(ABC):
    """Abstract interface for text embedding models."""

    name: str = "base"
    dimension: int = 384

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string into a vector."""
        pass

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of text strings into vectors."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the embedding provider/model is available."""
        pass


def get_embedding_provider(config: RAGConfig | None = None) -> EmbeddingProvider:
    """Factory function to get configured embedding provider."""
    from engines.rag.embeddings.mock_provider import MockEmbeddingProvider
    from engines.rag.embeddings.ollama_provider import OllamaEmbeddingProvider

    cfg = config or RAGConfig()
    provider_type = cfg.embedding_provider.lower()

    if provider_type == "ollama":
        provider = OllamaEmbeddingProvider(cfg)
        if provider.is_available():
            return provider
        logger.warning(
            "Ollama embedding provider requested but model '%s' unavailable. Falling back to MockEmbeddingProvider.",
            cfg.embedding_model,
        )
        return MockEmbeddingProvider()

    if provider_type == "mock" or provider_type == "fake":
        return MockEmbeddingProvider()

    logger.warning("Unknown embedding provider '%s'. Falling back to MockEmbeddingProvider.", provider_type)
    return MockEmbeddingProvider()
