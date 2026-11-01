"""Ollama local embedding provider."""

import math
import httpx

from config.settings import settings
from engines.rag.config import RAGConfig
from engines.rag.embeddings.provider import EmbeddingProvider
from shared.logger import get_logger

logger = get_logger("rag.embeddings.ollama")


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama embedding provider connecting to local server."""

    name = "ollama"

    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig()
        self.model = self.config.embedding_model or settings.ollama_model
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.dimension = 384

    def embed_text(self, text: str) -> list[float]:
        vecs = self.embed_documents([text])
        return vecs[0] if vecs else [0.0] * self.dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        # Try /api/embed first (Ollama v0.1.26+ batch endpoint), fallback to /api/embeddings per item
        try:
            with httpx.Client(timeout=30) as client:
                res = client.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.model, "input": texts},
                )
                if res.status_code == 200:
                    data = res.json()
                    embeddings = data.get("embeddings", [])
                    if embeddings:
                        self.dimension = len(embeddings[0])
                        return [self._normalize(v) for v in embeddings]
        except httpx.HTTPError:
            pass

        # Fallback per text item using /api/embeddings
        results: list[list[float]] = []
        try:
            with httpx.Client(timeout=30) as client:
                for text in texts:
                    res = client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": self.model, "prompt": text},
                    )
                    res.raise_for_status()
                    vec = res.json().get("embedding", [])
                    if vec:
                        self.dimension = len(vec)
                        results.append(self._normalize(vec))
                    else:
                        results.append([0.0] * self.dimension)
            return results
        except httpx.HTTPError as e:
            logger.error("Ollama embedding generation failed: %s", e)
            raise RuntimeError(f"Ollama embedding failed: {e}") from e

    def is_available(self) -> bool:
        """Check if Ollama server is running and the embedding model is available."""
        try:
            with httpx.Client(timeout=5) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code != 200:
                    return False
                models = [m.get("name", "") for m in res.json().get("models", [])]
                return any(self.model in m or m.startswith(self.model) for m in models)
        except httpx.HTTPError:
            return False

    @staticmethod
    def _normalize(vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]
