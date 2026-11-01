"""OpenAI LLM provider — infrastructure stub for future stages."""

from typing import Any

from config.settings import settings
from engines.llm.config import LLMConfig
from engines.llm.provider import LLMProvider
from shared.exceptions import LLMProviderError
from shared.logger import get_logger

logger = get_logger("llm.openai")


class OpenAIProvider(LLMProvider):
    """OpenAI provider stub — to be implemented in future stages."""

    name = "openai"

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig(
            provider="openai",
            model=settings.openai_model,
        )

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using OpenAI — not yet implemented."""
        raise LLMProviderError(
            "OpenAI provider is not implemented yet. Use Ollama for Stage 1."
        )

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(settings.openai_api_key)

    def list_models(self) -> list[str]:
        """List available OpenAI models."""
        return [settings.openai_model]
