"""Agent 2: Gap Detector."""

from pathlib import Path
from typing import Dict, Any, Optional

from src.agents.base import LLMAgent, AgentResult


class GapDetectorAgent:
    """Agent 2: Identifies gaps and misalignments in procedures.
    
    This agent:
    - Analyzes Agent 1's comparison output
    - Identifies missing steps, hazards, or controls
    - Finds misalignments between ROPs and JSAs
    - Flags critical safety gaps
    """

    def __init__(self, prompt_path: str = "prompts/AGENT-2-GAP-DETECTOR.md"):
        """Initialize the gap detector agent.
        
        Args:
            prompt_path: Path to the prompt template file.
        """
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            system_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            system_prompt = self._get_default_prompt()
        
        self.base_prompt = system_prompt
        self.agent = LLMAgent("Agent 2 – Gap Detector", system_prompt)

    def _get_default_prompt(self) -> str:
        """Get default system prompt if template file is not found."""
        return """# Agent 2 – Gap Detector

You are the Gap Detector for ADNOC's BOP standardisation initiative.

Your tasks:

1. **Analyze the comparison output** from Agent 1.
2. **Identify gaps**: Missing steps, hazards not covered, inadequate controls.
3. **Find misalignments**: Discrepancies between ROPs and JSAs.
4. **Flag critical safety gaps**: Especially for critical operations and barriers.

Output format (Markdown):

- **Section 1 – Missing steps and procedures**
- **Section 2 – Hazards not adequately addressed**
- **Section 3 – ROP-JSA misalignments**
- **Section 4 – Critical safety gaps requiring immediate attention**
- **Section 5 – Recommendations for gap closure**
"""

    def run(
        self,
        documents: Dict[str, str],
        previous_outputs: Dict[str, Any],
        backend: str = "openai",
        operation_name: Optional[str] = None,
    ) -> AgentResult:
        """Execute gap detection analysis.
        
        Args:
            documents: Original documents (for reference).
            previous_outputs: Outputs from previous agents (especially Agent 1).
            backend: LLM backend to use.
            operation_name: Name of the operation.
            
        Returns:
            AgentResult with gap analysis.
        """
        # Update system prompt with operation context
        op_label = operation_name or "the current operation described in the documents"
        
        # Get a snippet from the first document for grounding
        first_doc = next(iter(documents.values()), "") if documents else ""
        source_snippet = first_doc[:1500]
        
        self.agent.system_prompt = (
            f"{self.base_prompt}\n\n"
            f"Operation context: {op_label}.\n"
            "Source document snippet (for grounding):\n"
            f"{source_snippet}"
        )

        agent1_output = previous_outputs.get("agent1", "")
        
        user_prompt = (
            "You are analyzing BOP procedures for gaps and misalignments.\n\n"
            "# Agent 1 Comparison Output\n\n"
            f"{agent1_output}\n\n"
            "Based on this comparison, identify all gaps, missing steps, hazards, and misalignments."
        )
        
        return self.agent.run(user_prompt, backend=backend)
