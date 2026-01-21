"""
Tests for LLM provider error handling.

Tests error scenarios for LLM providers including message formatting,
configuration, and response handling.
"""

from unittest.mock import MagicMock, patch

import pytest

from localmind.llm.base import LLMConfig, LLMMessage, LLMResponse, LLMRole


class TestLLMConfig:
    """Tests for LLMConfig."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = LLMConfig()

        assert config.temperature == 0.7
        assert config.max_tokens == 4096  # Actual default
        assert config.json_mode is False
        assert config.json_schema is None

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            temperature=0.3,
            max_tokens=1000,
            json_mode=True,
            json_schema={"type": "object"},
        )

        assert config.temperature == 0.3
        assert config.max_tokens == 1000
        assert config.json_mode is True
        assert config.json_schema == {"type": "object"}

    def test_config_temperature_boundaries(self):
        """Test temperature boundary values."""
        config_low = LLMConfig(temperature=0.0)
        config_high = LLMConfig(temperature=2.0)

        assert config_low.temperature == 0.0
        assert config_high.temperature == 2.0

    def test_config_max_tokens_large(self):
        """Test large max_tokens value."""
        config = LLMConfig(max_tokens=100000)
        assert config.max_tokens == 100000


class TestLLMRole:
    """Tests for LLMRole enum."""

    def test_role_values(self):
        """Test role enum values."""
        assert LLMRole.SYSTEM.value == "system"
        assert LLMRole.USER.value == "user"
        assert LLMRole.ASSISTANT.value == "assistant"


class TestLLMMessage:
    """Tests for LLMMessage."""

    def test_message_creation_with_enum(self):
        """Test message creation with enum role."""
        message = LLMMessage(role=LLMRole.USER, content="Hello")

        assert message.role == LLMRole.USER
        assert message.content == "Hello"

    def test_message_to_dict(self):
        """Test message to_dict conversion."""
        message = LLMMessage(role=LLMRole.ASSISTANT, content="Hi there")
        d = message.to_dict()

        assert d["role"] == "assistant"
        assert d["content"] == "Hi there"

    def test_message_system_role(self):
        """Test system role message."""
        message = LLMMessage(role=LLMRole.SYSTEM, content="You are a helpful assistant.")
        assert message.role == LLMRole.SYSTEM
        assert "helpful assistant" in message.content

    def test_message_empty_content(self):
        """Test message with empty content."""
        message = LLMMessage(role=LLMRole.USER, content="")
        assert message.content == ""

    def test_message_unicode_content(self):
        """Test message with Unicode content."""
        message = LLMMessage(role=LLMRole.USER, content="नमस्ते, मैं आपकी मदद कर सकता हूं")
        assert "नमस्ते" in message.content
        d = message.to_dict()
        assert "नमस्ते" in d["content"]


class TestLLMResponse:
    """Tests for LLMResponse."""

    def test_response_creation(self):
        """Test response creation."""
        response = LLMResponse(
            content="Response text",
            model="gpt-4",
            provider="openai",
            usage={"input_tokens": 10, "output_tokens": 20},
        )

        assert response.content == "Response text"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.usage["input_tokens"] == 10

    def test_response_default_usage(self):
        """Test response with default usage."""
        response = LLMResponse(
            content="Test",
            model="test",
            provider="test",
        )

        assert response.usage == {}

    def test_response_with_json_content(self):
        """Test response with JSON content."""
        json_content = '{"score": 8.5, "feedback": "Good performance"}'
        response = LLMResponse(
            content=json_content,
            model="gpt-4",
            provider="openai",
        )
        assert response.content == json_content

    def test_response_long_content(self):
        """Test response with long content."""
        long_content = "word " * 10000
        response = LLMResponse(
            content=long_content,
            model="gpt-4",
            provider="openai",
        )
        assert len(response.content) > 40000


class TestProviderJSONMode:
    """Tests for JSON mode configuration."""

    def test_json_schema_validation(self):
        """Test JSON schema structure."""
        schema = {
            "type": "object",
            "properties": {
                "score": {"type": "number"},
                "feedback": {"type": "string"},
            },
            "required": ["score", "feedback"],
        }

        config = LLMConfig(json_mode=True, json_schema=schema)

        assert config.json_mode is True
        assert config.json_schema["type"] == "object"
        assert "score" in config.json_schema["properties"]

    def test_json_mode_without_schema(self):
        """Test JSON mode without schema."""
        config = LLMConfig(json_mode=True)
        assert config.json_mode is True
        assert config.json_schema is None

    def test_complex_json_schema(self):
        """Test complex JSON schema."""
        schema = {
            "type": "object",
            "properties": {
                "parameter_scores": {
                    "type": "object",
                    "properties": {
                        "greeting": {
                            "type": "object",
                            "properties": {
                                "score": {"type": "number"},
                                "feedback": {"type": "string"},
                            },
                        }
                    },
                },
                "strengths": {"type": "array", "items": {"type": "string"}},
            },
        }

        config = LLMConfig(json_mode=True, json_schema=schema)
        assert "parameter_scores" in config.json_schema["properties"]


class TestCreateProvider:
    """Tests for create_provider function."""

    def test_create_provider_openai(self):
        """Test creating OpenAI provider."""
        with patch("localmind.llm.factory.get_settings") as mock_settings:
            mock_settings.return_value.llm.provider = "openai"
            mock_settings.return_value.llm.openai_api_key = "test-key"
            mock_settings.return_value.llm.openai_model = "gpt-4"

            from localmind.llm.factory import create_provider

            provider = create_provider()

            assert provider is not None
            assert provider.provider_name == "openai"

    def test_create_provider_anthropic(self):
        """Test creating Anthropic provider."""
        with patch("localmind.llm.factory.get_settings") as mock_settings:
            mock_settings.return_value.llm.provider = "anthropic"
            mock_settings.return_value.llm.anthropic_api_key = "test-key"
            mock_settings.return_value.llm.anthropic_model = "claude-3-opus"

            from localmind.llm.factory import create_provider

            provider = create_provider()

            assert provider is not None
            assert provider.provider_name == "anthropic"

    def test_create_provider_local(self):
        """Test creating Local provider."""
        with patch("localmind.llm.factory.get_settings") as mock_settings:
            mock_settings.return_value.llm.provider = "local"
            mock_settings.return_value.llm.local_model = "phi-3.5-mini"

            from localmind.llm.factory import create_provider

            provider = create_provider()

            assert provider is not None
            assert provider.provider_name == "local"


class TestLocalProvider:
    """Tests for Local LLM provider."""

    def test_local_provider_initialization(self):
        """Test local provider initialization."""
        from localmind.llm.local_provider import LocalProvider

        provider = LocalProvider(model="phi-3.5-mini")

        assert provider.provider_name == "local"

    def test_local_provider_message_creation(self):
        """Test local provider message creation."""
        from localmind.llm.local_provider import LocalProvider

        provider = LocalProvider(model="phi-3.5-mini")

        system_msg = provider.create_system_message("System prompt")
        user_msg = provider.create_user_message("User message")

        assert system_msg.role == LLMRole.SYSTEM
        assert user_msg.role == LLMRole.USER


class TestLLMMessageEdgeCases:
    """Tests for edge cases in LLM messages."""

    def test_message_with_special_characters(self):
        """Test message with special characters."""
        content = 'Test with "quotes" and \n newlines and \t tabs'
        message = LLMMessage(role=LLMRole.USER, content=content)
        assert message.content == content

    def test_message_with_json_string(self):
        """Test message containing JSON string."""
        content = '{"key": "value", "array": [1, 2, 3]}'
        message = LLMMessage(role=LLMRole.ASSISTANT, content=content)
        d = message.to_dict()
        assert d["content"] == content

    def test_multiple_messages(self):
        """Test creating multiple messages."""
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="You are helpful."),
            LLMMessage(role=LLMRole.USER, content="Hello"),
            LLMMessage(role=LLMRole.ASSISTANT, content="Hi there!"),
            LLMMessage(role=LLMRole.USER, content="How are you?"),
        ]
        assert len(messages) == 4
        assert messages[0].role == LLMRole.SYSTEM
        assert messages[-1].role == LLMRole.USER
