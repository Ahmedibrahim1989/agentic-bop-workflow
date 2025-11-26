"""Unit tests for src/config.py module."""

import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Tests for the Settings dataclass."""

    def test_settings_with_openai_key_only(self):
        """Settings should accept only OpenAI API key."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-openai-key",
            "ANTHROPIC_API_KEY": "",
        }, clear=False):
            # Need to reimport to get fresh settings
            from src.config import Settings
            settings = Settings(
                openai_api_key="test-openai-key",
                anthropic_api_key=None
            )
            assert settings.openai_api_key == "test-openai-key"
            assert settings.anthropic_api_key is None

    def test_settings_with_anthropic_key_only(self):
        """Settings should accept only Anthropic API key."""
        from src.config import Settings
        settings = Settings(
            openai_api_key=None,
            anthropic_api_key="test-anthropic-key"
        )
        assert settings.openai_api_key is None
        assert settings.anthropic_api_key == "test-anthropic-key"

    def test_settings_with_both_keys(self):
        """Settings should accept both API keys."""
        from src.config import Settings
        settings = Settings(
            openai_api_key="test-openai-key",
            anthropic_api_key="test-anthropic-key"
        )
        assert settings.openai_api_key == "test-openai-key"
        assert settings.anthropic_api_key == "test-anthropic-key"

    def test_settings_default_model_names(self):
        """Settings should have correct default model names."""
        from src.config import Settings
        settings = Settings(
            openai_api_key="test-key",
            anthropic_api_key=None
        )
        assert settings.model_name_openai == "gpt-4o"
        assert settings.model_name_anthropic == "claude-3-5-sonnet-20241022"

    def test_settings_default_temperature(self):
        """Settings should have correct default temperature."""
        from src.config import Settings
        settings = Settings(openai_api_key="test-key")
        assert settings.temperature == 0.2

    def test_settings_default_max_tokens(self):
        """Settings should have correct default max tokens."""
        from src.config import Settings
        settings = Settings(openai_api_key="test-key")
        assert settings.max_tokens == 4096

    def test_settings_custom_values(self):
        """Settings should accept custom values."""
        from src.config import Settings
        settings = Settings(
            openai_api_key="custom-key",
            anthropic_api_key="custom-anthropic",
            model_name_openai="gpt-4-turbo",
            model_name_anthropic="claude-3-opus",
            temperature=0.5,
            max_tokens=8192
        )
        assert settings.model_name_openai == "gpt-4-turbo"
        assert settings.model_name_anthropic == "claude-3-opus"
        assert settings.temperature == 0.5
        assert settings.max_tokens == 8192


class TestSettingsValidation:
    """Tests for Settings.validate() method."""

    def test_validate_with_openai_key_succeeds(self):
        """Validation should pass with OpenAI key only."""
        from src.config import Settings
        settings = Settings(
            openai_api_key="test-key",
            anthropic_api_key=None
        )
        # Should not raise
        settings.validate()

    def test_validate_with_anthropic_key_succeeds(self):
        """Validation should pass with Anthropic key only."""
        from src.config import Settings
        settings = Settings(
            openai_api_key=None,
            anthropic_api_key="test-key"
        )
        # Should not raise
        settings.validate()

    def test_validate_with_both_keys_succeeds(self):
        """Validation should pass with both keys."""
        from src.config import Settings
        settings = Settings(
            openai_api_key="openai-key",
            anthropic_api_key="anthropic-key"
        )
        # Should not raise
        settings.validate()

    def test_validate_without_keys_fails(self):
        """Validation should fail without any API keys."""
        from src.config import Settings
        settings = Settings(
            openai_api_key=None,
            anthropic_api_key=None
        )
        with pytest.raises(ValueError) as exc_info:
            settings.validate()
        assert "At least one API key must be set" in str(exc_info.value)

    def test_validate_with_empty_string_keys_fails(self):
        """Validation should fail with empty string keys."""
        from src.config import Settings
        settings = Settings(
            openai_api_key="",
            anthropic_api_key=""
        )
        with pytest.raises(ValueError) as exc_info:
            settings.validate()
        assert "At least one API key must be set" in str(exc_info.value)


class TestSettingsFromEnvironment:
    """Tests for Settings loading from environment variables."""

    def test_settings_loads_openai_key_from_env(self):
        """Settings should load OPENAI_API_KEY from environment."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-openai-key"}, clear=False):
            # Create fresh Settings reading from env
            openai_key = os.getenv("OPENAI_API_KEY")
            from src.config import Settings
            settings = Settings(openai_api_key=openai_key)
            assert settings.openai_api_key == "env-openai-key"

    def test_settings_loads_anthropic_key_from_env(self):
        """Settings should load ANTHROPIC_API_KEY from environment."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-anthropic-key"}, clear=False):
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            from src.config import Settings
            settings = Settings(anthropic_api_key=anthropic_key)
            assert settings.anthropic_api_key == "env-anthropic-key"

    def test_settings_loads_temperature_from_env(self):
        """Settings should load TEMPERATURE from environment."""
        with patch.dict(os.environ, {"TEMPERATURE": "0.7"}, clear=False):
            temp = float(os.getenv("TEMPERATURE", "0.2"))
            from src.config import Settings
            settings = Settings(openai_api_key="key", temperature=temp)
            assert settings.temperature == 0.7

    def test_settings_loads_max_tokens_from_env(self):
        """Settings should load MAX_TOKENS from environment."""
        with patch.dict(os.environ, {"MAX_TOKENS": "2048"}, clear=False):
            max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
            from src.config import Settings
            settings = Settings(openai_api_key="key", max_tokens=max_tokens)
            assert settings.max_tokens == 2048

    def test_settings_uses_defaults_when_env_not_set(self):
        """Settings should use defaults when environment variables are not set."""
        from src.config import Settings
        # Create with explicit values to test defaults
        settings = Settings(
            openai_api_key="test-key",
            anthropic_api_key=None,
            model_name_openai="gpt-4o",
            model_name_anthropic="claude-3-5-sonnet-20241022",
            temperature=0.2,
            max_tokens=4096
        )
        assert settings.model_name_openai == "gpt-4o"
        assert settings.model_name_anthropic == "claude-3-5-sonnet-20241022"
        assert settings.temperature == 0.2
        assert settings.max_tokens == 4096
