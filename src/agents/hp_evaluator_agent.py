"""Agent 3: Human Performance Evaluator."""

from pathlib import Path
from typing import Dict, Any

from src.agents.base import LLMAgent, AgentResult


class HPEvaluatorAgent:
    """Agent 3: Evaluates human performance factors and critical controls.
    
    This agent:
    - Assesses human performance maturity in procedures
    - Evaluates critical step verification methods
    - Reviews checklists and barriers
    - Identifies human error traps
    """

    def __init__(self, prompt_path: str = "prompts/AGENT-3-HP-EVALUATOR.md"):
        """Initialize the HP evaluator agent.
        
        Args:
            prompt_path: Path to the prompt template file.
        """
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            system_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            system_prompt = self._get_default_prompt()
        
        self.agent = LLMAgent("Agent 3 – HP Evaluator", system_prompt)

    def _get_default_prompt(self) -> str:
        """Get default system prompt if template file is not found."""
        return """# Agent 3 – Human Performance Evaluator

You are the Human Performance Evaluator for ADNOC's BOP standardisation initiative.

Your tasks:

1. **Evaluate HP maturity**: Assess how well procedures support human performance.
2. **Review critical step verification**: Check if critical steps have adequate verification.
3. **Assess checklists and barriers**: Evaluate quality and completeness of safety barriers.
4. **Identify error traps**: Find areas where human error is likely.

Output format (Markdown):

- **Section 1 – Human performance maturity assessment**
- **Section 2 – Critical step verification evaluation**
- **Section 3 – Checklist and barrier analysis**
- **Section 4 – Human error traps and mitigation**
- **Section 5 – Recommendations for HP improvement**
"""

    def run(
        self,
        documents: Dict[str, str],
        previous_outputs: Dict[str, Any],
        backend: str = "openai",
    ) -> AgentResult:
        """Execute human performance evaluation.
        
        Args:
            documents: Original documents (for reference).
            previous_outputs: Outputs from previous agents.
            backend: LLM backend to use.
            
        Returns:
            AgentResult with HP evaluation.
        """
        agent1_output = previous_outputs.get("agent1", "")
        agent2_output = previous_outputs.get("agent2", "")
        
        user_prompt = (
            "You are evaluating human performance factors in BOP procedures.\n\n"
            "# Agent 1 Comparison Output\n\n"
            f"{agent1_output[:6000]}...\n\n"
            "# Agent 2 Gap Analysis\n\n"
            f"{agent2_output[:4000]}...\n\n"
            "Evaluate human performance maturity, critical controls, and error prevention."
        )
        
        return self.agent.run(user_prompt, backend=backend)
