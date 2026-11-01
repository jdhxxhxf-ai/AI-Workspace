"""LLM engine configuration."""

from pydantic import BaseModel


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    provider: str = "ollama"
    model: str = "llama3"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 120
