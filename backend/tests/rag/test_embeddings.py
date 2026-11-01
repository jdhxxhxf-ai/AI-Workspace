"""Unit tests for embedding providers and mocks."""

import pytest

from engines.rag.config import RAGConfig
from engines.rag.embeddings.mock_provider import MockEmbeddingProvider
from engines.rag.embeddings.ollama_provider import OllamaEmbeddingProvider
from engines.rag.embeddings.provider import get_embedding_provider


def test_mock_embedding_provider():
    provider = MockEmbeddingProvider()
    assert provider.is_available() is True
    assert provider.dimension == 384

    v1 = provider.embed_text("Hello world")
    v2 = provider.embed_text("Hello world")
    v3 = provider.embed_text("Different text")

    assert len(v1) == 384
    assert v1 == v2  # Deterministic
    assert v1 != v3


def test_factory_fallback_to_mock():
    config = RAGConfig(embedding_provider="invalid_provider")
    provider = get_embedding_provider(config)
    assert provider.name == "mock"


@pytest.mark.ollama
def test_live_ollama_provider():
    provider = OllamaEmbeddingProvider()
    if provider.is_available():
        vec = provider.embed_text("Test embedding generation")
        assert len(vec) > 0
