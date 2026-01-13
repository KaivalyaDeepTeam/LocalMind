"""LocalMind LLM provider abstraction layer."""

from localmind.llm.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    LLMConfig,
    LLMRole,
)
from localmind.llm.openai_provider import OpenAIProvider
from localmind.llm.anthropic_provider import AnthropicProvider
from localmind.llm.local_provider import LocalProvider, LOCAL_MODELS, get_models_directory
from localmind.llm.factory import create_provider, get_default_provider, get_initialized_provider

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
