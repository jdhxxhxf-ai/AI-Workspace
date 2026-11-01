"""Deterministic mock embedding provider for unit testing and fallback."""

import hashlib
import math
from engines.rag.embeddings.provider import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    """Generates deterministic pseudo-embedding vectors for offline testing."""

    name = "mock"
    dimension = 384

    def embed_text(self, text: str) -> list[float]:
        return self._generate_vector(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._generate_vector(t) for t in texts]

    def is_available(self) -> bool:
        return True

    def _generate_vector(self, text: str) -> list[float]:
        # Generate 384 float values deterministically from text SHA-256 hash seed
        vector = []
        base_seed = hashlib.sha256(text.encode("utf-8")).digest()

        for i in range(self.dimension):
            # Mix index with base seed
            idx_bytes = i.to_bytes(4, byteorder="big")
            h = hashlib.sha256(base_seed + idx_bytes).digest()
            val = (int.from_bytes(h[:4], "big") / (2**32 - 1)) * 2.0 - 1.0
            vector.append(val)

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]
