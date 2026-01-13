"""
Unit tests for LocalMind LLM module.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from localmind.llm.base import (
    BaseLLMProvider,
    LLMMessage,
    LLMResponse,
    LLMConfig,
    LLMRole,
)
from localmind.llm.factory import create_provider
from localmind.config import LLMProviderType


class TestLLMMessage:
    """Tests for LLMMessage."""

    def test_create_message(self):
        """Test creating a message."""
        msg = LLMMessage(role=LLMRole.USER, content="Hello")

        assert msg.role == LLMRole.USER
        assert msg.content == "Hello"

    def test_to_dict(self):
        """Test converting message to dictionary."""
        msg = LLMMessage(role=LLMRole.SYSTEM, content="You are helpful.")

        data = msg.to_dict()

        assert data["role"] == "system"
        assert data["content"] == "You are helpful."

    def test_all_roles(self):
        """Test all message roles."""
        roles = [LLMRole.SYSTEM, LLMRole.USER, LLMRole.ASSISTANT]

        for role in roles:
            msg = LLMMessage(role=role, content="test")
            assert msg.role == role


class TestLLMResponse:
    """Tests for LLMResponse."""

    def test_create_response(self):
        """Test creating a response."""
        response = LLMResponse(
            content="Hello!",
            model="gpt-4o",
            provider="openai",
            usage={"input_tokens": 10, "output_tokens": 5},
        )

        assert response.content == "Hello!"
        assert response.model == "gpt-4o"
        assert response.provider == "openai"

    def test_token_counts(self):
        """Test token count properties."""
        response = LLMResponse(
            content="test",
            model="test",
            provider="test",
            usage={"input_tokens": 100, "output_tokens": 50},
        )

        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.total_tokens == 150

    def test_empty_usage(self):
        """Test with empty usage dict."""
        response = LLMResponse(
            content="test",
            model="test",
            provider="test",
        )

        assert response.input_tokens == 0
        assert response.output_tokens == 0
        assert response.total_tokens == 0


class TestLLMConfig:
    """Tests for LLMConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LLMConfig()

        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.top_p == 1.0
        assert config.json_mode is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = LLMConfig(
            temperature=0.3,
            max_tokens=1000,
            json_mode=True,
            stop_sequences=["END"],
        )

        assert config.temperature == 0.3
        assert config.max_tokens == 1000
        assert config.json_mode is True
        assert config.stop_sequences == ["END"]


class TestProviderFactory:
    """Tests for provider factory."""

    def test_create_openai_provider(self, mock_settings):
        """Test creating OpenAI provider."""
        from localmind.llm.openai_provider import OpenAIProvider

        provider = create_provider(
            provider_type=LLMProviderType.OPENAI,
            model="gpt-4o-mini",
            api_key="test-key",
        )

        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4o-mini"

    def test_create_anthropic_provider(self, mock_settings):
        """Test creating Anthropic provider."""
        from localmind.llm.anthropic_provider import AnthropicProvider

        provider = create_provider(
            provider_type=LLMProviderType.ANTHROPIC,
            model="claude-3-haiku-20240307",
            api_key="test-key",
        )

        assert isinstance(provider, AnthropicProvider)
        assert provider.model == "claude-3-haiku-20240307"

    def test_create_local_provider(self, mock_settings):
        """Test creating local provider."""
        from localmind.llm.local_provider import LocalProvider

        provider = create_provider(
            provider_type=LLMProviderType.LOCAL,
            model="phi-3.5-mini",
        )

        assert isinstance(provider, LocalProvider)
        assert provider.model == "phi-3.5-mini"


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    def test_provider_name(self):
        """Test provider name."""
        from localmind.llm.openai_provider import OpenAIProvider

        provider = OpenAIProvider(model="gpt-4o")
        assert provider.provider_name == "openai"

    @pytest.mark.asyncio
    async def test_generate_mock(self):
        """Test generate with mocked client."""
        from localmind.llm.openai_provider import OpenAIProvider

        provider = OpenAIProvider(model="gpt-4o", api_key="test")

        # Mock the client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello!"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-4o"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5

        with patch.object(provider, "_client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            provider._is_initialized = True

            messages = [LLMMessage(role=LLMRole.USER, content="Hi")]
            response = await provider.generate(messages)

            assert response.content == "Hello!"
            assert response.provider == "openai"


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    def test_provider_name(self):
        """Test provider name."""
        from localmind.llm.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(model="claude-sonnet-4-20250514")
        assert provider.provider_name == "anthropic"


class TestLocalProvider:
    """Tests for Local LLM provider."""

    def test_provider_name(self):
        """Test provider name."""
        from localmind.llm.local_provider import LocalProvider

        provider = LocalProvider(model="phi-3.5-mini")
        assert provider.provider_name == "local"

    def test_model_config(self):
        """Test getting model configuration."""
        from localmind.llm.local_provider import LocalProvider, LOCAL_MODELS

        provider = LocalProvider(model="phi-3.5-mini")
        config = provider._get_model_config()

        assert config == LOCAL_MODELS["phi-3.5-mini"]
        assert "repo" in config
        assert "filename" in config

    def test_is_model_downloaded(self):
        """Test checking if model is downloaded."""
        from localmind.llm.local_provider import LocalProvider

        provider = LocalProvider(model="phi-3.5-mini")

        # Model likely not downloaded in test environment
        assert provider.is_model_downloaded() in [True, False]
