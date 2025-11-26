"""Base agent class with LLM backend abstraction."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.config import settings

# Lazy-loaded clients - initialized on first use for better testability
_openai_client: Optional[Any] = None
_anthropic_client: Optional[Any] = None
_clients_initialized = False


def _get_openai_client():
    """Get or create the OpenAI client (lazy initialization)."""
    global _openai_client, _clients_initialized
    if not _clients_initialized:
        _initialize_clients()
    return _openai_client


def _get_anthropic_client():
    """Get or create the Anthropic client (lazy initialization)."""
    global _anthropic_client, _clients_initialized
    if not _clients_initialized:
        _initialize_clients()
    return _anthropic_client


def _initialize_clients():
    """Initialize API clients on first use."""
    global _openai_client, _anthropic_client, _clients_initialized

    if _clients_initialized:
        return

    # Initialize OpenAI client
    if settings.openai_api_key:
        try:
            from openai import OpenAI
            _openai_client = OpenAI(api_key=settings.openai_api_key)
        except (ImportError, Exception):
            _openai_client = None

    # Initialize Anthropic client
    if settings.anthropic_api_key:
        try:
            import anthropic
            _anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        except (ImportError, Exception):
            _anthropic_client = None

    _clients_initialized = True


# For backwards compatibility and testing - expose module-level variables
openai_client = None  # Will be populated by _get_openai_client()
anthropic_client = None  # Will be populated by _get_anthropic_client()


@dataclass
class AgentResult:
    """Result from an agent execution.

    Attributes:
        content: The main output text (Markdown formatted).
        meta: Metadata about the execution (timing, tokens, model, etc.).
    """
    content: str
    meta: Dict[str, Any]


class LLMAgent:
    """Base class for LLM-powered agents.

    Provides a unified interface for calling OpenAI or Anthropic models,
    with automatic error handling and metadata tracking.

    Attributes:
        name: Agent name for logging and metadata.
        system_prompt: System-level instructions for the agent.
    """

    def __init__(self, name: str, system_prompt: str):
        """Initialize the agent.

        Args:
            name: Agent identifier.
            system_prompt: Instructions defining the agent's role and behavior.
        """
        self.name = name
        self.system_prompt = system_prompt

    def _call_openai(self, prompt: str) -> tuple[str, Dict[str, Any]]:
        """Call OpenAI API.

        Args:
            prompt: User prompt to send to the model.

        Returns:
            Tuple of (response_text, metadata_dict).
        """
        client = _get_openai_client()
        if client is None:
            return (
                f"[{self.name}] OPENAI_API_KEY not set; returning stub output.\n\nPROMPT:\n{prompt[:1000]}",
                {"error": "No OpenAI client available"},
            )

        start = time.time()

        try:
            response = client.chat.completions.create(
                model=settings.model_name_openai,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
            )

            duration = time.time() - start

            # Extract response text
            content = response.choices[0].message.content or ""

            # Build metadata
            metadata = {
                "model": settings.model_name_openai,
                "tokens_prompt": response.usage.prompt_tokens if response.usage else 0,
                "tokens_completion": response.usage.completion_tokens if response.usage else 0,
                "tokens_total": response.usage.total_tokens if response.usage else 0,
                "duration_seconds": round(duration, 2),
            }

            return content, metadata

        except Exception as e:
            duration = time.time() - start
            return (
                f"[{self.name}] Error calling OpenAI: {e}",
                {"error": str(e), "duration_seconds": round(duration, 2)},
            )

    def _call_anthropic(self, prompt: str) -> tuple[str, Dict[str, Any]]:
        """Call Anthropic API.

        Args:
            prompt: User prompt to send to the model.

        Returns:
            Tuple of (response_text, metadata_dict).
        """
        client = _get_anthropic_client()
        if client is None:
            return (
                f"[{self.name}] ANTHROPIC_API_KEY not set; returning stub output.\n\nPROMPT:\n{prompt[:1000]}",
                {"error": "No Anthropic client available"},
            )

        start = time.time()

        try:
            message = client.messages.create(
                model=settings.model_name_anthropic,
                system=self.system_prompt,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            duration = time.time() - start

            # Extract response text
            text_parts = [block.text for block in message.content if block.type == "text"]
            content = "\n".join(text_parts)

            # Build metadata
            metadata = {
                "model": settings.model_name_anthropic,
                "tokens_prompt": message.usage.input_tokens if message.usage else 0,
                "tokens_completion": message.usage.output_tokens if message.usage else 0,
                "tokens_total": (message.usage.input_tokens + message.usage.output_tokens) if message.usage else 0,
                "duration_seconds": round(duration, 2),
            }

            return content, metadata

        except Exception as e:
            duration = time.time() - start
            return (
                f"[{self.name}] Error calling Anthropic: {e}",
                {"error": str(e), "duration_seconds": round(duration, 2)},
            )

    def run(
        self,
        prompt: str,
        backend: str = "openai",
    ) -> AgentResult:
        """Execute the agent with the given prompt.

        Args:
            prompt: User prompt describing the task.
            backend: LLM backend to use ("openai" or "anthropic").

        Returns:
            AgentResult with content and metadata.
        """
        start = time.time()

        if backend == "anthropic":
            content, llm_meta = self._call_anthropic(prompt)
        else:
            content, llm_meta = self._call_openai(prompt)

        end = time.time()

        return AgentResult(
            content=content,
            meta={
                "agent": self.name,
                "backend": backend,
                "total_duration_seconds": round(end - start, 2),
                **llm_meta,
            },
        )
