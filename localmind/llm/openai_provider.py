"""
LocalMind OpenAI Provider

OpenAI API implementation of the LLM provider.
"""

from typing import Optional, List, Dict, Any, AsyncGenerator

from localmind.llm.base import (
    BaseLLMProvider, LLMMessage, LLMResponse, LLMConfig,
)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize OpenAI provider.

        Args:
            model: Model name (e.g., gpt-4o, gpt-4o-mini).
            api_key: OpenAI API key (or uses OPENAI_API_KEY env var).
            base_url: Optional custom base URL for API.
        """
        super().__init__(model)
        self._api_key = api_key
        self._base_url = base_url
        self._client = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    async def initialize(self) -> None:
        """Initialize the OpenAI client."""
        if self._is_initialized:
            return

        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

        self._client = AsyncOpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
        )
        self._is_initialized = True

    async def generate(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
    ) -> LLMResponse:
        """Generate a response using OpenAI API."""
        if not self._is_initialized:
            await self.initialize()

        if config is None:
            config = LLMConfig()

        # Build request parameters
        params: Dict[str, Any] = {
            "model": self._model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }

        if config.stop_sequences:
            params["stop"] = config.stop_sequences

        if config.json_mode:
            params["response_format"] = {"type": "json_object"}

        # Make API call
        response = await self._client.chat.completions.create(**params)

        # Extract response data
        choice = response.choices[0]
        content = choice.message.content or ""

        return LLMResponse(
            content=content,
            model=response.model,
            provider=self.provider_name,
            usage={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            },
            finish_reason=choice.finish_reason,
            raw_response=response,
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response using OpenAI API."""
        if not self._is_initialized:
            await self.initialize()

        if config is None:
            config = LLMConfig()

        # Build request parameters
        params: Dict[str, Any] = {
            "model": self._model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "stream": True,
        }

        if config.stop_sequences:
            params["stop"] = config.stop_sequences

        # Make streaming API call
        stream = await self._client.chat.completions.create(**params)

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def close(self) -> None:
        """Clean up OpenAI client resources."""
        if self._client:
            await self._client.close()
            self._client = None
            self._is_initialized = False
