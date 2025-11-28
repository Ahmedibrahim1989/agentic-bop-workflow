"""Unit tests for src/agents/integrated_compliance_agent.py module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.agents.integrated_compliance_agent import IntegratedComplianceAgent
from src.agents.base import AgentResult


class TestIntegratedComplianceAgentInitialization:
    """Tests for IntegratedComplianceAgent initialization."""

    def test_agent_initialization_with_default_prompt_path(self):
        """IntegratedComplianceAgent should initialize with default prompt path."""
        with patch("src.agents.integrated_compliance_agent.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = False
            mock_path.return_value = mock_path_instance

            agent = IntegratedComplianceAgent()

        assert agent.agent is not None
        assert agent.agent.name == "Integrated Compliance Agent"

    def test_agent_initialization_with_custom_prompt_path(self, temp_prompt_file):
        """IntegratedComplianceAgent should load prompt from custom path."""
        agent = IntegratedComplianceAgent(prompt_path=str(temp_prompt_file))

        assert agent.agent is not None
        assert "test agent" in agent.agent.system_prompt.lower()

    def test_agent_uses_default_prompt_when_file_missing(self):
        """IntegratedComplianceAgent should use default prompt when file doesn't exist."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent/path/prompt.md")

        assert agent.agent is not None
        assert "Integrated Compliance Agent" in agent.agent.system_prompt

    def test_default_prompt_contains_required_sections(self):
        """Default prompt should contain all required sections."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent/path.md")

        prompt = agent.agent.system_prompt
        assert "Technical Writing" in prompt or "procedure" in prompt.lower()
        assert "Gap" in prompt
        assert "Human Performance" in prompt or "HP" in prompt
        assert "Equipment" in prompt
        assert "standard" in prompt.lower()


class TestIntegratedComplianceAgentGetDefaultPrompt:
    """Tests for IntegratedComplianceAgent._get_default_prompt method."""

    def test_get_default_prompt_returns_string(self):
        """_get_default_prompt should return a string."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_get_default_prompt_is_markdown_formatted(self):
        """_get_default_prompt should return markdown-formatted text."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert "#" in prompt  # Contains headers

    def test_get_default_prompt_mentions_all_agent_functions(self):
        """_get_default_prompt should mention all five agent functions."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        # Check for references to all agent capabilities
        assert "Technical" in prompt or "Writer" in prompt
        assert "Gap" in prompt
        assert "HP" in prompt or "Human Performance" in prompt
        assert "Equipment" in prompt
        assert "standard" in prompt.lower()

    def test_get_default_prompt_mentions_adnoc(self):
        """_get_default_prompt should mention ADNOC."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        prompt = agent._get_default_prompt()

        assert "ADNOC" in prompt


class TestIntegratedComplianceAgentBuildUserPrompt:
    """Tests for IntegratedComplianceAgent._build_user_prompt method."""

    def test_build_user_prompt_includes_documents(self, sample_documents):
        """_build_user_prompt should include all provided documents."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        prompt = agent._build_user_prompt(sample_documents, {})

        for doc_name in sample_documents.keys():
            assert doc_name in prompt

    def test_build_user_prompt_includes_context(self, sample_documents):
        """_build_user_prompt should include context information."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        context = {
            "rig_name": "Dana",
            "operation_type": "BOP Installation",
            "constraints": "Limited crane capacity",
        }
        prompt = agent._build_user_prompt(sample_documents, context)

        assert "Dana" in prompt
        assert "BOP Installation" in prompt
        assert "Limited crane capacity" in prompt

    def test_build_user_prompt_includes_adnoc_cps(self, sample_documents):
        """_build_user_prompt should include ADNOC CPs when provided."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        context = {
            "adnoc_cps": ["HSE-PSW-CP01", "HSE-PSW-CP04", "HSE-PSW-CP09"]
        }
        prompt = agent._build_user_prompt(sample_documents, context)

        assert "HSE-PSW-CP01" in prompt
        assert "HSE-PSW-CP04" in prompt
        assert "HSE-PSW-CP09" in prompt

    def test_build_user_prompt_truncates_large_documents(self):
        """_build_user_prompt should truncate very large documents."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        large_doc = {"Large Document": "x" * 15000}
        prompt = agent._build_user_prompt(large_doc, {})

        assert "truncated" in prompt.lower()

    def test_build_user_prompt_handles_empty_context(self, sample_documents):
        """_build_user_prompt should handle empty context gracefully."""
        agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
        prompt = agent._build_user_prompt(sample_documents, {})

        assert "Not specified" in prompt
        assert isinstance(prompt, str)


class TestIntegratedComplianceAgentRun:
    """Tests for IntegratedComplianceAgent.run method."""

    def test_run_calls_underlying_agent(self, sample_documents, mock_openai_response):
        """run() should call the underlying LLMAgent."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, backend="openai")

        assert isinstance(result, AgentResult)
        mock_client.chat.completions.create.assert_called_once()

    def test_run_with_context(self, sample_documents, mock_openai_response):
        """run() should include context in the request."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        context = {
            "rig_name": "Dana",
            "operation_type": "BOP Installation",
        }

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            agent.run(sample_documents, context=context, backend="openai")

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        assert "Dana" in user_message
        assert "BOP Installation" in user_message

    def test_run_with_anthropic_backend(self, sample_documents, mock_anthropic_response):
        """run() should work with Anthropic backend."""
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_response

        with patch("src.agents.base._get_anthropic_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_anthropic = "claude-3-5-sonnet-20241022"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, backend="anthropic")

        assert isinstance(result, AgentResult)
        assert result.meta["backend"] == "anthropic"

    def test_run_returns_agent_result(self, sample_documents, mock_openai_response):
        """run() should return AgentResult with content and metadata."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, backend="openai")

        assert hasattr(result, "content")
        assert hasattr(result, "meta")
        assert "agent" in result.meta


class TestIntegratedComplianceAgentRunWithPreviousOutputs:
    """Tests for IntegratedComplianceAgent.run_with_previous_outputs method."""

    def test_run_with_previous_outputs_includes_all_agents(
        self, sample_documents, sample_previous_outputs, mock_openai_response
    ):
        """run_with_previous_outputs() should include all previous agent outputs."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            agent.run_with_previous_outputs(
                sample_documents, sample_previous_outputs, backend="openai"
            )

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        # Should reference all previous agents
        assert "Agent 1" in user_message or "Comparison" in user_message
        assert "Agent 2" in user_message or "Gap" in user_message
        assert "Agent 3" in user_message or "HP" in user_message
        assert "Agent 4" in user_message or "Equipment" in user_message

    def test_run_with_previous_outputs_truncates_long_outputs(
        self, sample_documents, mock_openai_response
    ):
        """run_with_previous_outputs() should truncate long previous outputs."""
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

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            agent.run_with_previous_outputs(
                sample_documents, previous_outputs, backend="openai"
            )

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        assert "truncated" in user_message.lower()

    def test_run_with_previous_outputs_handles_empty_previous(
        self, sample_documents, mock_openai_response
    ):
        """run_with_previous_outputs() should handle empty previous outputs."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            result = agent.run_with_previous_outputs(
                sample_documents, {}, backend="openai"
            )

        assert isinstance(result, AgentResult)

    def test_run_with_previous_outputs_handles_partial_previous(
        self, sample_documents, mock_openai_response
    ):
        """run_with_previous_outputs() should handle partial previous outputs."""
        partial_outputs = {
            "agent1": "Agent 1 output only",
            # Missing other agents
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            result = agent.run_with_previous_outputs(
                sample_documents, partial_outputs, backend="openai"
            )

        assert isinstance(result, AgentResult)

    def test_run_with_previous_outputs_includes_agent5(
        self, sample_documents, mock_openai_response
    ):
        """run_with_previous_outputs() should include agent5 output if provided."""
        previous_outputs = {
            "agent1": "Agent 1 output",
            "agent2": "Agent 2 output",
            "agent3": "Agent 3 output",
            "agent4": "Agent 4 output",
            "agent5": "Agent 5 standardisation output",
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            agent.run_with_previous_outputs(
                sample_documents, previous_outputs, backend="openai"
            )

        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        assert "Standardisation" in user_message or "Agent 5" in user_message


class TestIntegratedComplianceAgentOutputFormat:
    """Tests for output format requirements."""

    def test_run_returns_structured_content(self, sample_documents, mock_openai_response):
        """run() should return properly structured content."""
        # Customize mock response
        mock_openai_response.choices[0].message.content = """# Integrated ROP Package

## Part 1: Rig Operating Procedure
### 1. General Information
Document number: ROP-001

### 2. Work Description
BOP Installation procedure...

## Part 2: Gap Analysis Report
No critical gaps identified.

## Part 3: Human Performance Assessment
All steps reviewed for HP risks.

## Part 4: Equipment Validation Matrix
| Equipment | Status |
|-----------|--------|
| Crane | Compliant |

## Part 5: Document Control
Revision: 1.0
"""

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent = IntegratedComplianceAgent(prompt_path="/nonexistent.md")
            result = agent.run(sample_documents, backend="openai")

        # Verify structure elements are present
        assert "Part 1" in result.content or "ROP" in result.content
        assert "Gap" in result.content
        assert "Human Performance" in result.content or "HP" in result.content
        assert "Equipment" in result.content
