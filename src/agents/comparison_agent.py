"""Agent 1: Comparison Analyst."""

from pathlib import Path
from typing import Dict, Any

from src.agents.base import LLMAgent, AgentResult


class ComparisonAgent:
    """Agent 1: Performs inventory, structure mapping, and detailed comparison.
    
    This agent:
    - Creates an inventory of all provided documents
    - Maps the structure of ROPs and JSAs
    - Performs line-by-line comparison across rigs
    - Identifies variations, best practices, and common patterns
    """

    def __init__(self, prompt_path: str = "prompts/AGENT-1-PROMPT-TEMPLATE.md"):
        """Initialize the comparison agent.
        
        Args:
            prompt_path: Path to the prompt template file.
        """
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            system_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            # Fallback prompt if file doesn't exist
            system_prompt = self._get_default_prompt()
        
        self.agent = LLMAgent("Agent 1 – Comparison Analyst", system_prompt)

    def _get_default_prompt(self) -> str:
        """Get default system prompt if template file is not found."""
        return """# Agent 1 – Comparison Analyst

You are the Comparison Analyst for ADNOC's BOP standardisation initiative.

Your tasks:

1. **Inventory all provided documents**: List each rig name, document type (ROP/JSA), version, and date if present.
2. **Map their structure**: Identify sections, annexes, JSAs, risk matrices, equipment lists, permits.
3. **Perform line-by-line comparison**: Compare ROPs and JSAs across rigs step-by-step.
4. **Identify**:
   - Common baseline steps and controls
   - Variations and missing steps
   - Notable best practices or stronger controls

Output format (Markdown):

- **Section 1 – Document inventory**
- **Section 2 – Structure mapping**
- **Section 3 – Detailed comparison by phase / step**
- **Section 4 – Summary of best practices and divergences**
"""

    def run(
        self,
        documents: Dict[str, str],
        previous_outputs: Dict[str, Any],
        backend: str = "openai",
    ) -> AgentResult:
        """Execute the comparison analysis.
        
        Args:
            documents: Dictionary mapping document names to their text content.
            previous_outputs: Outputs from previous agents (empty for Agent 1).
            backend: LLM backend to use.
            
        Returns:
            AgentResult with comparison analysis.
        """
        # Build a comprehensive prompt with all documents
        docs_summary = "\n\n".join(
            f"### {name}\n\n{text[:8000]}..." if len(text) > 8000 else f"### {name}\n\n{text}"
            for name, text in documents.items()
        )
        
        user_prompt = (
            "You are given multiple rig procedures and JSAs for BOP operations.\n"
            "Perform a comprehensive inventory, structure mapping, and detailed comparison.\n\n"
            "# Documents\n\n"
            f"{docs_summary}"
        )
        
        return self.agent.run(user_prompt, backend=backend)
