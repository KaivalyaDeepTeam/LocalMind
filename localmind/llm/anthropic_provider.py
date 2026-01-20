"""
LocalMind Anthropic Provider

Anthropic API implementation of the LLM provider.
"""

from collections.abc import AsyncGenerator
from typing import Any

from localmind.llm.base import (
    BaseLLMProvider,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMRole,
)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic API provider implementation."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """Initialize Anthropic provider.

        Args:
            model: Model name (e.g., claude-sonnet-4-20250514).
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var).
            base_url: Optional custom base URL for API.
        """
        super().__init__(model)
        self._api_key = api_key
        self._base_url = base_url
        self._client = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "anthropic"

    async def initialize(self) -> None:
        """Initialize the Anthropic client."""
        if self._is_initialized:
            return

        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

        kwargs: dict[str, Any] = {}
        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._base_url:
            kwargs["base_url"] = self._base_url

        self._client = AsyncAnthropic(**kwargs)
        self._is_initialized = True

    async def generate(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        """Generate a response using Anthropic API."""
        if not self._is_initialized:
            await self.initialize()

        if config is None:
            config = LLMConfig()

        # Separate system message from conversation
        system_content = None
        conversation_messages = []

        for msg in messages:
            if msg.role == LLMRole.SYSTEM:
                system_content = msg.content
            else:
                conversation_messages.append(msg.to_dict())

        # Build request parameters
        params: dict[str, Any] = {
            "model": self._model,
            "messages": conversation_messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }

        if system_content:
            params["system"] = system_content

        if config.stop_sequences:
            params["stop_sequences"] = config.stop_sequences

        # Make API call
        response = await self._client.messages.create(**params)

        # Extract response data
        content = ""
        if response.content:
            content = response.content[0].text

        return LLMResponse(
            content=content,
            model=response.model,
            provider=self.provider_name,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
            raw_response=response,
        )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response using Anthropic API."""
        if not self._is_initialized:
            await self.initialize()

        if config is None:
            config = LLMConfig()

        # Separate system message from conversation
        system_content = None
        conversation_messages = []

        for msg in messages:
            if msg.role == LLMRole.SYSTEM:
                system_content = msg.content
            else:
                conversation_messages.append(msg.to_dict())

        # Build request parameters
        params: dict[str, Any] = {
            "model": self._model,
            "messages": conversation_messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
        }

        if system_content:
            params["system"] = system_content

        if config.stop_sequences:
            params["stop_sequences"] = config.stop_sequences

        # Make streaming API call
        async with self._client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text

    async def close(self) -> None:
        """Clean up Anthropic client resources."""
        if self._client:
            await self._client.close()
            self._client = None
            self._is_initialized = False
