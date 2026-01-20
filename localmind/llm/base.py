"""
LocalMind LLM Base Provider

Abstract base class for LLM providers with unified interface.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LLMRole(Enum):
    """Message roles for chat completion."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class LLMMessage:
    """A message in a conversation."""

    role: LLMRole
    content: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary format."""
        return {"role": self.role.value, "content": self.content}


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str
    provider: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str | None = None
    raw_response: Any | None = None

    @property
    def input_tokens(self) -> int:
        """Get input token count."""
        return self.usage.get("input_tokens", 0)

    @property
    def output_tokens(self) -> int:
        """Get output token count."""
        return self.usage.get("output_tokens", 0)

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        return self.input_tokens + self.output_tokens


@dataclass
class LLMConfig:
    """Configuration for LLM generation."""

    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    stop_sequences: list[str] | None = None
    json_mode: bool = False
    json_schema: dict[str, Any] | None = None  # JSON schema for constrained generation


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model: str):
        """Initialize provider with model name."""
        self._model = model
        self._is_initialized = False

    @property
    def model(self) -> str:
        """Get the model name."""
        return self._model

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name."""
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._is_initialized

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider (load models, validate API keys, etc.)."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            messages: List of conversation messages.
            config: Generation configuration.

        Returns:
            LLMResponse with generated content.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM.

        Args:
            messages: List of conversation messages.
            config: Generation configuration.

        Yields:
            String chunks of the response.
        """
        pass

    async def generate_json(
        self,
        messages: list[LLMMessage],
        config: LLMConfig | None = None,
    ) -> dict[str, Any]:
        """Generate a JSON response from the LLM.

        Args:
            messages: List of conversation messages.
            config: Generation configuration.

        Returns:
            Parsed JSON response.
        """
        import json

        if config is None:
            config = LLMConfig()
        config.json_mode = True

        response = await self.generate(messages, config)

        # Try to parse JSON from response
        content = response.content.strip()

        # Handle markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # Try to parse JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Better error message showing what the LLM actually returned
            preview = content[:200] if content else "(empty response)"
            raise ValueError(
                f"LLM did not return valid JSON. Error: {e}\n"
                f"Response preview: {preview}\n"
                f"Make sure the model supports JSON mode and the prompt is clear."
            )

    def create_system_message(self, content: str) -> LLMMessage:
        """Create a system message."""
        return LLMMessage(role=LLMRole.SYSTEM, content=content)

    def create_user_message(self, content: str) -> LLMMessage:
        """Create a user message."""
        return LLMMessage(role=LLMRole.USER, content=content)

    def create_assistant_message(self, content: str) -> LLMMessage:
        """Create an assistant message."""
        return LLMMessage(role=LLMRole.ASSISTANT, content=content)

    @abstractmethod
    async def close(self) -> None:
        """Clean up provider resources."""
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
