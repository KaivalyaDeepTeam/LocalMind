"""
LLM Provider Abstraction Layer for CallScore Desktop

Supports multiple LLM backends:
- OpenAI (GPT-4o, o1)
- Anthropic (Claude)
- Local (Phi-3.5-mini, Mistral-7B via llama-cpp)

Usage:
    from desktop.llm import get_provider
    from desktop.config.user_settings import get_settings

    provider = get_provider(get_settings())
    result = provider.merge_transcripts(v3_text, h2h_text, duration)
"""

from typing import TYPE_CHECKING

from desktop.llm.base_provider import (
    BaseLLMProvider,
    MergeResult,
    AuditResult,
    QualityParameter,
)
from desktop.llm.openai_provider import OpenAIProvider
from desktop.llm.anthropic_provider import AnthropicProvider
from desktop.llm.local_provider import LocalLLMProvider, download_local_model

if TYPE_CHECKING:
    from desktop.config.user_settings import UserSettings

__all__ = [
    # Base classes
    "BaseLLMProvider",
    "MergeResult",
    "AuditResult",
    "QualityParameter",
    # Providers
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalLLMProvider",
    # Factory
    "get_provider",
    # Utilities
    "download_local_model",
]


def get_provider(settings: "UserSettings") -> BaseLLMProvider:
    """
    Get the appropriate LLM provider based on user settings.

    Args:
        settings: User settings containing LLM configuration

    Returns:
        Configured LLM provider instance
    """
    from desktop.config.user_settings import LLMProviderType

    provider_type = settings.llm.provider

    if provider_type == LLMProviderType.OPENAI:
        return OpenAIProvider(
            api_key=settings.llm.openai_api_key,
            model=settings.llm.openai_model,
        )
    elif provider_type == LLMProviderType.ANTHROPIC:
        return AnthropicProvider(
            api_key=settings.llm.anthropic_api_key,
            model=settings.llm.anthropic_model,
        )
    else:
        return LocalLLMProvider(
            model=settings.llm.local_model,
        )


def get_provider_by_name(name: str, api_key: str = "", model: str = "") -> BaseLLMProvider:
    """
    Get a provider by name.

    Args:
        name: Provider name ("openai", "anthropic", "local")
        api_key: API key (for cloud providers)
        model: Model identifier

    Returns:
        Provider instance
    """
    name = name.lower()

    if name == "openai":
        return OpenAIProvider(api_key=api_key, model=model)
    elif name == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model)
    else:
        return LocalLLMProvider(model=model)
