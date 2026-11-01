"""LLM request pipeline — orchestrates prompt building and provider calls."""

from engines.llm.config import LLMConfig
from engines.llm.ollama_provider import OllamaProvider
from engines.llm.openai_provider import OpenAIProvider
from engines.llm.prompt_builder import PromptBuilder
from engines.llm.provider import LLMProvider
from config.settings import settings
from shared.logger import get_logger

logger = get_logger("llm.pipeline")


class LLMPipeline:
    """Orchestrates LLM requests through the configured provider."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig(provider=settings.llm_provider)
        self._provider = self._create_provider()

    def _create_provider(self) -> LLMProvider:
        """Create the configured LLM provider."""
        providers: dict[str, type[LLMProvider]] = {
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
        }
        provider_cls = providers.get(self.config.provider, OllamaProvider)
        logger.info("Using LLM provider: %s", self.config.provider)
        return provider_cls(self.config)

    @property
    def provider(self) -> LLMProvider:
        """Get the active provider."""
        return self._provider

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a completion from a raw prompt."""
        return self._provider.generate(prompt, **kwargs)

    def generate_from_builder(self, builder: PromptBuilder, **kwargs) -> str:
        """Generate a completion from a PromptBuilder."""
        return self._provider.generate(builder.build(), **kwargs)

    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        return self._provider.is_available()
