"""LocalMind LLM provider abstraction layer."""

from localmind.llm.anthropic_provider import AnthropicProvider
from localmind.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMRole,
)
from localmind.llm.factory import create_provider, get_default_provider, get_initialized_provider
from localmind.llm.local_provider import LOCAL_MODELS, LocalProvider, get_models_directory
from localmind.llm.openai_provider import OpenAIProvider

__all__ = [
    # Base classes
    "BaseLLMProvider",
    "LLMMessage",
    "LLMResponse",
    "LLMConfig",
    "LLMRole",
    # Providers
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalProvider",
    # Factory
    "create_provider",
    "get_default_provider",
    "get_initialized_provider",
    # Utilities
    "LOCAL_MODELS",
    "get_models_directory",
]
