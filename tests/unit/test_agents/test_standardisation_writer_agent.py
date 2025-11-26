"""Unit tests for src/agents/standardisation_writer_agent.py module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.agents.standardisation_writer_agent import StandardisationWriterAgent
from src.agents.base import AgentResult


class TestStandardisationWriterAgentInitialization:
    """Tests for StandardisationWriterAgent initialization."""

    def test_agent_initialization_with_default_prompt_path(self):
        """StandardisationWriterAgent should initialize with default prompt path."""
        with patch("src.agents.standardisation_writer_agent.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance

            agent = StandardisationWriterAgent()

        assert agent.agent is not None
        assert agent.agent.name == "Agent 5 – Standardisation Writer"

    def test_agent_initialization_with_custom_prompt_path(self, temp_prompt_file):
        """StandardisationWriterAgent should load prompt from custom path."""
        agent = StandardisationWriterAgent(prompt_path=str(temp_prompt_file))

        assert agent.agent is not None
        assert "test agent" in agent.agent.system_prompt.lower()

    def test_agent_uses_default_prompt_when_file_missing(self):
        """StandardisationWriterAgent should use default prompt when file doesn't exist."""
        agent = StandardisationWriterAgent(prompt_path="/nonexistent/path/prompt.md")

        assert agent.agent is not None
        assert "Standardisation Writer" in agent.agent.system_prompt

    def test_default_prompt_contains_required_sections(self):
        """Default prompt should contain all required sections."""
        agent = StandardisationWriterAgent(prompt_path="/nonexistent/path.md")

        prompt = agent.agent.system_prompt
        assert "standardize" in prompt.lower() or "standardise" in prompt.lower()
        assert "ROP" in prompt or "procedure" in prompt.lower()
        assert "JSA" in prompt or "safety" in prompt.lower()


class TestStandardisationWriterAgentGetDefaultPrompt:
    """Tests for StandardisationWriterAgent._get_default_prompt method."""

    def test_get_default_prompt_returns_string(self):
        """_get_default_prompt should return a string."""
        agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_get_default_prompt_is_markdown_formatted(self):
        """_get_default_prompt should return markdown-formatted text."""
        agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert "#" in prompt  # Contains headers

    def test_get_default_prompt_mentions_synthesis(self):
        """_get_default_prompt should mention synthesizing previous outputs."""
        agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert "synthesize" in prompt.lower() or "integrate" in prompt.lower()


class TestStandardisationWriterAgentRun:
    """Tests for StandardisationWriterAgent.run method."""

    def test_run_calls_underlying_agent(self, sample_documents, sample_previous_outputs, mock_openai_response):
        """run() should call the underlying LLMAgent."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, sample_previous_outputs, backend="openai")

        assert isinstance(result, AgentResult)
        mock_client.chat.completions.create.assert_called_once()

    def test_run_includes_all_previous_agent_outputs(self, sample_documents, sample_previous_outputs, mock_openai_response):
        """run() should include outputs from all 4 previous agents."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
            agent.run(sample_documents, sample_previous_outputs, backend="openai")

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        # Should include all agent outputs
        assert "Agent 1" in user_message
        assert "Agent 2" in user_message
        assert "Agent 3" in user_message
        assert "Agent 4" in user_message

    def test_run_truncates_agent_outputs(self, sample_documents, mock_openai_response):
        """run() should truncate long agent outputs."""
        long_output = "x" * 10000
        previous_outputs = {
            "agent1": long_output,
            "agent2": long_output,
            "agent3": long_output,
            "agent4": long_output,
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
            agent.run(sample_documents, previous_outputs, backend="openai")

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        # Should have truncation indicators
        assert "..." in user_message

    def test_run_handles_missing_previous_outputs(self, sample_documents, mock_openai_response):
        """run() should handle missing previous outputs gracefully."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base.openai_client", mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, {}, backend="openai")

        assert isinstance(result, AgentResult)

    def test_run_handles_partial_previous_outputs(self, sample_documents, mock_openai_response):
        """run() should handle partial previous outputs."""
        partial_outputs = {
            "agent1": "Agent 1 output",
            # Missing agent2, agent3, agent4
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base.openai_client", mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, partial_outputs, backend="openai")

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

            agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, sample_previous_outputs, backend="anthropic")

        assert isinstance(result, AgentResult)
        assert result.meta["backend"] == "anthropic"

    def test_run_returns_standardized_content(self, sample_documents, sample_previous_outputs, mock_openai_response):
        """run() should return AgentResult with content."""
        # Customize mock response to contain standardization content
        mock_openai_response.choices[0].message.content = """# Standardized BOP Installation Procedure

## Executive Summary
This document provides the standardized procedure...

## Standardized ROP
1. Pre-job preparation
2. BOP handling
3. Installation

## Standardized JSA
- Step 1: Pre-job meeting
- Step 2: BOP lifting
"""

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = StandardisationWriterAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, sample_previous_outputs, backend="openai")

        assert "Standardized" in result.content
        assert isinstance(result, AgentResult)
