"""Agent 5: Standardisation Writer."""

from pathlib import Path
from typing import Dict, Any

from src.agents.base import LLMAgent, AgentResult


class StandardisationWriterAgent:
    """Agent 5: Synthesizes findings into standardized procedures.
    
    This agent:
    - Synthesizes all previous agent outputs
    - Creates standardized ROP and JSA documents
    - Develops implementation package
    - Provides rig-specific guidance where needed
    """

    def __init__(self, prompt_path: str = "prompts/AGENT-5-STANDARDISATION-WRITER.md"):
        """Initialize the standardisation writer agent.
        
        Args:
            prompt_path: Path to the prompt template file.
        """
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            system_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            system_prompt = self._get_default_prompt()
        
        self.agent = LLMAgent("Agent 5 – Standardisation Writer", system_prompt)

    def _get_default_prompt(self) -> str:
        """Get default system prompt if template file is not found."""
        return """# Agent 5 – Standardisation Writer

You are the Standardisation Writer for ADNOC's BOP standardisation initiative.

Your tasks:

1. **Synthesize all findings**: Integrate outputs from all previous agents.
2. **Create standardized ROP**: Write a comprehensive, standardized BOP installation procedure.
3. **Create standardized JSA**: Develop a unified job safety analysis.
4. **Develop implementation package**: Provide guidance for rollout across rigs.
5. **Address rig-specific variations**: Document necessary exceptions and adaptations.

Output format (Markdown):

- **Section 1 – Executive summary**
- **Section 2 – Standardized ROP (full procedure)**
- **Section 3 – Standardized JSA (full analysis)**
- **Section 4 – Implementation package**
- **Section 5 – Rig-specific variations and exceptions**
- **Section 6 – Recommendations and next steps**
"""

    def run(
        self,
        documents: Dict[str, str],
        previous_outputs: Dict[str, Any],
        backend: str = "openai",
    ) -> AgentResult:
        """Execute standardisation writing.
        
        Args:
            documents: Original documents (for reference).
            previous_outputs: Outputs from all previous agents.
            backend: LLM backend to use.
            
        Returns:
            AgentResult with standardized procedures.
        """
        agent1_output = previous_outputs.get("agent1", "")
        agent2_output = previous_outputs.get("agent2", "")
        agent3_output = previous_outputs.get("agent3", "")
        agent4_output = previous_outputs.get("agent4", "")
        
        user_prompt = (
            "You are creating the final standardized BOP procedures.\n\n"
            "# Agent 1 – Comparison Analysis\n\n"
            f"{agent1_output[:5000]}...\n\n"
            "# Agent 2 – Gap Analysis\n\n"
            f"{agent2_output[:4000]}...\n\n"
            "# Agent 3 – HP Evaluation\n\n"
            f"{agent3_output[:4000]}...\n\n"
            "# Agent 4 – Equipment Validation\n\n"
            f"{agent4_output[:4000]}...\n\n"
            "Synthesize all findings into a comprehensive standardized ROP and JSA."
        )
        
        return self.agent.run(user_prompt, backend=backend)
