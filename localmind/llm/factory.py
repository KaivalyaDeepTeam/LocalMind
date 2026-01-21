"""
LocalMind LLM Provider Factory

Factory for creating LLM providers based on configuration.
"""

from localmind.config import (
    LLMProviderType,
    get_anthropic_api_key,
    get_openai_api_key,
    get_settings,
)
from localmind.llm.anthropic_provider import AnthropicProvider
from localmind.llm.base import BaseLLMProvider
from localmind.llm.local_provider import LocalProvider
from localmind.llm.openai_provider import OpenAIProvider


def create_provider(
    provider_type: LLMProviderType | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> BaseLLMProvider:
    """Create an LLM provider based on configuration.

    Args:
        provider_type: Type of provider (uses settings if not specified).
        model: Model name (uses settings if not specified).
        api_key: API key (uses settings if not specified).

    Returns:
        Configured LLM provider instance.
    """
    settings = get_settings()

    if provider_type is None:
        provider_type = settings.llm.provider

    if provider_type == LLMProviderType.OPENAI:
        return OpenAIProvider(
            model=model or settings.llm.openai_model,
            api_key=api_key or get_openai_api_key(),  # Get from secure storage
        )
    elif provider_type == LLMProviderType.ANTHROPIC:
        return AnthropicProvider(
            model=model or settings.llm.anthropic_model,
            api_key=api_key or get_anthropic_api_key(),  # Get from secure storage
        )
    elif provider_type == LLMProviderType.LOCAL:
        return LocalProvider(
            model=model or settings.llm.local_model,
        )
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def get_default_provider() -> BaseLLMProvider:
    """Get the default LLM provider based on user settings.

    Returns:
        Configured LLM provider instance.
    """
    return create_provider()


async def get_initialized_provider(
    provider_type: LLMProviderType | None = None,
) -> BaseLLMProvider:
    """Get an initialized LLM provider.

    Args:
        provider_type: Type of provider (uses settings if not specified).

    Returns:
        Initialized LLM provider instance.
    """
    provider = create_provider(provider_type)
    await provider.initialize()
    return provider
