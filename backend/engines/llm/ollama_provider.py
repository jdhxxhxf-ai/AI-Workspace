"""Ollama LLM provider."""

from typing import Any

import httpx

from config.settings import settings
from engines.llm.config import LLMConfig
from engines.llm.provider import LLMProvider
from shared.exceptions import LLMProviderError
from shared.logger import get_logger

logger = get_logger("llm.ollama")


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    name = "ollama"

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig(
            provider="ollama",
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        )

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using Ollama."""
        model = kwargs.get("model", self.config.model)
        url = f"{self.config.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.HTTPError as e:
            logger.error("Ollama request failed: %s", e)
            raise LLMProviderError(f"Ollama request failed: {e}") from e

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.config.base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.config.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except httpx.HTTPError:
            return []
