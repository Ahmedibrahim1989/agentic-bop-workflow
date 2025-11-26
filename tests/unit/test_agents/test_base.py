"""Unit tests for src/agents/base.py module."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import time

from src.agents.base import AgentResult, LLMAgent


class TestAgentResult:
    """Tests for the AgentResult dataclass."""

    def test_agent_result_creation(self):
        """AgentResult should store content and metadata."""
        result = AgentResult(
            content="Test output content",
            meta={"key": "value"}
        )
        assert result.content == "Test output content"
        assert result.meta == {"key": "value"}

    def test_agent_result_with_full_metadata(self):
        """AgentResult should store complete metadata."""
        meta = {
            "agent": "Test Agent",
            "backend": "openai",
            "total_duration_seconds": 1.5,
            "model": "gpt-4o",
            "tokens_prompt": 100,
            "tokens_completion": 50,
            "tokens_total": 150,
        }
        result = AgentResult(content="Content", meta=meta)

        assert result.meta["agent"] == "Test Agent"
        assert result.meta["backend"] == "openai"
        assert result.meta["tokens_total"] == 150

    def test_agent_result_empty_content(self):
        """AgentResult should accept empty content."""
        result = AgentResult(content="", meta={})
        assert result.content == ""

    def test_agent_result_markdown_content(self):
        """AgentResult should preserve markdown formatting."""
        markdown = """# Header

## Section 1
- Item 1
- Item 2

```python
code_block()
```
"""
        result = AgentResult(content=markdown, meta={})
        assert "# Header" in result.content
        assert "```python" in result.content


class TestLLMAgentInitialization:
    """Tests for LLMAgent initialization."""

    def test_agent_initialization(self):
        """LLMAgent should initialize with name and system prompt."""
        agent = LLMAgent("Test Agent", "You are a test agent.")

        assert agent.name == "Test Agent"
        assert agent.system_prompt == "You are a test agent."

    def test_agent_with_long_system_prompt(self):
        """LLMAgent should accept long system prompts."""
        long_prompt = "Instructions\n" * 1000
        agent = LLMAgent("Long Prompt Agent", long_prompt)

        assert agent.system_prompt == long_prompt


class TestLLMAgentOpenAI:
    """Tests for LLMAgent OpenAI backend."""

    def test_call_openai_without_client(self):
        """_call_openai should return stub when client is None."""
        agent = LLMAgent("Test Agent", "System prompt")

        with patch("src.agents.base._get_openai_client", return_value=None):
            content, meta = agent._call_openai("Test prompt")

        assert "OPENAI_API_KEY not set" in content
        assert "stub output" in content
        assert meta.get("error") == "No OpenAI client available"

    def test_call_openai_success(self, mock_openai_response):
        """_call_openai should return content and metadata on success."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            content, meta = agent._call_openai("Test prompt")

        assert content == "This is a mock OpenAI response for testing."
        assert meta["model"] == "gpt-4o"
        assert meta["tokens_prompt"] == 100
        assert meta["tokens_completion"] == 50
        assert meta["tokens_total"] == 150
        assert "duration_seconds" in meta

    def test_call_openai_passes_correct_parameters(self, mock_openai_response):
        """_call_openai should pass correct parameters to API."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent._call_openai("User prompt text")

        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]

        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["max_tokens"] == 4096
        assert call_kwargs["temperature"] == 0.2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][0]["content"] == "System prompt"
        assert call_kwargs["messages"][1]["role"] == "user"
        assert call_kwargs["messages"][1]["content"] == "User prompt text"

    def test_call_openai_handles_exception(self):
        """_call_openai should handle API exceptions gracefully."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            content, meta = agent._call_openai("Test prompt")

        assert "Error calling OpenAI" in content
        assert "API Error" in content
        assert meta["error"] == "API Error"
        assert "duration_seconds" in meta

    def test_call_openai_handles_empty_response(self):
        """_call_openai should handle empty response content."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 0
        mock_response.usage.total_tokens = 100

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            content, meta = agent._call_openai("Test prompt")

        assert content == ""


class TestLLMAgentAnthropic:
    """Tests for LLMAgent Anthropic backend."""

    def test_call_anthropic_without_client(self):
        """_call_anthropic should return stub when client is None."""
        agent = LLMAgent("Test Agent", "System prompt")

        with patch("src.agents.base._get_anthropic_client", return_value=None):
            content, meta = agent._call_anthropic("Test prompt")

        assert "ANTHROPIC_API_KEY not set" in content
        assert "stub output" in content
        assert meta.get("error") == "No Anthropic client available"

    def test_call_anthropic_success(self, mock_anthropic_response):
        """_call_anthropic should return content and metadata on success."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_response

        with patch("src.agents.base._get_anthropic_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_anthropic = "claude-3-5-sonnet-20241022"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            content, meta = agent._call_anthropic("Test prompt")

        assert content == "This is a mock Anthropic response for testing."
        assert meta["model"] == "claude-3-5-sonnet-20241022"
        assert meta["tokens_prompt"] == 100
        assert meta["tokens_completion"] == 50
        assert meta["tokens_total"] == 150
        assert "duration_seconds" in meta

    def test_call_anthropic_passes_correct_parameters(self, mock_anthropic_response):
        """_call_anthropic should pass correct parameters to API."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_response

        with patch("src.agents.base._get_anthropic_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_anthropic = "claude-3-5-sonnet-20241022"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            agent._call_anthropic("User prompt text")

        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]

        assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
        assert call_kwargs["max_tokens"] == 4096
        assert call_kwargs["temperature"] == 0.2
        assert call_kwargs["system"] == "System prompt"
        assert call_kwargs["messages"][0]["role"] == "user"
        assert call_kwargs["messages"][0]["content"] == "User prompt text"

    def test_call_anthropic_handles_exception(self):
        """_call_anthropic should handle API exceptions gracefully."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("Anthropic Error")

        with patch("src.agents.base._get_anthropic_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_anthropic = "claude-3-5-sonnet-20241022"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            content, meta = agent._call_anthropic("Test prompt")

        assert "Error calling Anthropic" in content
        assert "Anthropic Error" in content
        assert meta["error"] == "Anthropic Error"
        assert "duration_seconds" in meta

    def test_call_anthropic_handles_multiple_content_blocks(self):
        """_call_anthropic should join multiple text blocks."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_block1 = MagicMock()
        mock_block1.type = "text"
        mock_block1.text = "First block."
        mock_block2 = MagicMock()
        mock_block2.type = "text"
        mock_block2.text = "Second block."

        mock_response = MagicMock()
        mock_response.content = [mock_block1, mock_block2]
        mock_response.usage = MagicMock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        with patch("src.agents.base._get_anthropic_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_anthropic = "claude-3-5-sonnet-20241022"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            content, meta = agent._call_anthropic("Test prompt")

        assert "First block." in content
        assert "Second block." in content


class TestLLMAgentRun:
    """Tests for LLMAgent.run() method."""

    def test_run_with_openai_backend(self, mock_openai_response):
        """run() should use OpenAI backend by default."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            result = agent.run("Test prompt", backend="openai")

        assert isinstance(result, AgentResult)
        assert result.meta["backend"] == "openai"
        assert result.meta["agent"] == "Test Agent"

    def test_run_with_anthropic_backend(self, mock_anthropic_response):
        """run() should use Anthropic backend when specified."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_anthropic_response

        with patch("src.agents.base._get_anthropic_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_anthropic = "claude-3-5-sonnet-20241022"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            result = agent.run("Test prompt", backend="anthropic")

        assert isinstance(result, AgentResult)
        assert result.meta["backend"] == "anthropic"

    def test_run_returns_agent_result(self, mock_openai_response):
        """run() should return AgentResult with content and metadata."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            result = agent.run("Test prompt")

        assert result.content == "This is a mock OpenAI response for testing."
        assert "total_duration_seconds" in result.meta
        assert result.meta["agent"] == "Test Agent"

    def test_run_tracks_total_duration(self, mock_openai_response):
        """run() should track total duration including overhead."""
        agent = LLMAgent("Test Agent", "System prompt")

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_openai_response

        with patch("src.agents.base._get_openai_client", return_value=mock_client), \
             patch("src.agents.base.settings") as mock_settings:
            mock_settings.model_name_openai = "gpt-4o"
            mock_settings.max_tokens = 4096
            mock_settings.temperature = 0.2

            result = agent.run("Test prompt")

        assert "total_duration_seconds" in result.meta
        assert isinstance(result.meta["total_duration_seconds"], float)

    def test_run_default_backend_is_openai(self):
        """run() should default to openai backend."""
        agent = LLMAgent("Test Agent", "System prompt")

        with patch.object(agent, '_call_openai', return_value=("content", {})) as mock_openai, \
             patch.object(agent, '_call_anthropic') as mock_anthropic:
            agent.run("Test prompt")

        mock_openai.assert_called_once()
        mock_anthropic.assert_not_called()
