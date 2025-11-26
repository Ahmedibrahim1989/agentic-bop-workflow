"""Unit tests for src/agents/equipment_validator_agent.py module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.agents.equipment_validator_agent import EquipmentValidatorAgent
from src.agents.base import AgentResult


class TestEquipmentValidatorAgentInitialization:
    """Tests for EquipmentValidatorAgent initialization."""

    def test_agent_initialization_with_default_prompt_path(self):
        """EquipmentValidatorAgent should initialize with default prompt path."""
        with patch("src.agents.equipment_validator_agent.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance

            agent = EquipmentValidatorAgent()

        assert agent.agent is not None
        assert agent.agent.name == "Agent 4 – Equipment Validator"

    def test_agent_initialization_with_custom_prompt_path(self, temp_prompt_file):
        """EquipmentValidatorAgent should load prompt from custom path."""
        agent = EquipmentValidatorAgent(prompt_path=str(temp_prompt_file))

        assert agent.agent is not None
        assert "test agent" in agent.agent.system_prompt.lower()

    def test_agent_uses_default_prompt_when_file_missing(self):
        """EquipmentValidatorAgent should use default prompt when file doesn't exist."""
        agent = EquipmentValidatorAgent(prompt_path="/nonexistent/path/prompt.md")

        assert agent.agent is not None
        assert "Equipment Validator" in agent.agent.system_prompt

    def test_default_prompt_contains_required_sections(self):
        """Default prompt should contain all required sections."""
        agent = EquipmentValidatorAgent(prompt_path="/nonexistent/path.md")

        prompt = agent.agent.system_prompt
        assert "equipment" in prompt.lower()
        assert "standardization" in prompt.lower() or "standard" in prompt.lower()
        assert "constraint" in prompt.lower() or "limitation" in prompt.lower()


class TestEquipmentValidatorAgentGetDefaultPrompt:
    """Tests for EquipmentValidatorAgent._get_default_prompt method."""

    def test_get_default_prompt_returns_string(self):
        """_get_default_prompt should return a string."""
        agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_get_default_prompt_is_markdown_formatted(self):
        """_get_default_prompt should return markdown-formatted text."""
        agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert "#" in prompt  # Contains headers


class TestEquipmentValidatorAgentRun:
    """Tests for EquipmentValidatorAgent.run method."""

    def test_run_calls_underlying_agent(self, sample_documents, sample_previous_outputs, mock_openai_response):
        """run() should call the underlying LLMAgent."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, sample_previous_outputs, backend="openai")

        assert isinstance(result, AgentResult)
        mock_client.chat.completions.create.assert_called_once()

    def test_run_includes_documents_and_agent1_output(self, sample_documents, sample_previous_outputs, mock_openai_response):
        """run() should include documents and Agent 1 output in the user prompt."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
            agent.run(sample_documents, sample_previous_outputs, backend="openai")

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        # Should include documents
        for doc_name in sample_documents.keys():
            assert doc_name in user_message

        # Should include Agent 1 output reference
        assert "Agent 1" in user_message

    def test_run_truncates_documents(self, sample_previous_outputs, mock_openai_response):
        """run() should truncate long documents."""
        long_doc = "x" * 10000
        documents = {"Long Equipment Doc": long_doc}

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
            agent.run(documents, sample_previous_outputs, backend="openai")

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        # Should have truncation indicators
        assert "..." in user_message

    def test_run_handles_missing_agent1_output(self, sample_documents, mock_openai_response):
        """run() should handle missing agent1 output gracefully."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base.openai_client", mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, {}, backend="openai")

        assert isinstance(result, AgentResult)

    def test_run_with_anthropic_backend(self, sample_documents, sample_previous_outputs, mock_anthropic_response):
        """run() should work with Anthropic backend."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_response

        with patch("src.agents.base.anthropic_client", mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_anthropic = "claude-3-5-sonnet-20241022"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, sample_previous_outputs, backend="anthropic")

        assert isinstance(result, AgentResult)
        assert result.meta["backend"] == "anthropic"

    def test_run_with_empty_documents(self, sample_previous_outputs, mock_openai_response):
        """run() should handle empty documents dictionary."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base.openai_client", mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = EquipmentValidatorAgent(prompt_path="/nonexistent.md")
            result = agent.run({}, sample_previous_outputs, backend="openai")

        assert isinstance(result, AgentResult)
