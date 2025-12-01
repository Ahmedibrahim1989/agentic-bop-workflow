"""Agent 4: Equipment Validator."""

from pathlib import Path
from typing import Dict, Any, Optional

from src.agents.base import LLMAgent, AgentResult


class EquipmentValidatorAgent:
    """Agent 4: Validates equipment specifications and standardization feasibility.
    
    This agent:
    - Extracts equipment specifications from all rigs
    - Compares equipment capabilities and limitations
    - Assesses feasibility of standardized procedures
    - Identifies rig-specific constraints
    """

    def __init__(self, prompt_path: str = "prompts/AGENT-4-EQUIPMENT-VALIDATOR.md"):
        """Initialize the equipment validator agent.
        
        Args:
            prompt_path: Path to the prompt template file.
        """
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            system_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            system_prompt = self._get_default_prompt()
        
        self.base_prompt = system_prompt
        self.agent = LLMAgent("Agent 4 – Equipment Validator", system_prompt)

    def _get_default_prompt(self) -> str:
        """Get default system prompt if template file is not found."""
        return """# Agent 4 – Equipment Validator

You are the Equipment Validator for ADNOC's BOP standardisation initiative.

Your tasks:

1. **Extract equipment specs**: List all BOP equipment and specifications per rig.
2. **Compare capabilities**: Identify common capabilities and differences.
3. **Assess standardization feasibility**: Determine if procedures can be standardized.
4. **Identify constraints**: Note rig-specific limitations that require procedure variations.

Output format (Markdown):

- **Section 1 – Equipment inventory per rig**
- **Section 2 – Capability comparison matrix**
- **Section 3 – Standardization feasibility assessment**
- **Section 4 – Rig-specific constraints and exceptions**
- **Section 5 – Equipment-related recommendations**
"""

    def run(
        self,
        documents: Dict[str, str],
        previous_outputs: Dict[str, Any],
        backend: str = "openai",
        operation_name: Optional[str] = None,
    ) -> AgentResult:
        """Execute equipment validation.
        
        Args:
            documents: Original documents (for equipment specs).
            previous_outputs: Outputs from previous agents.
            backend: LLM backend to use.
            operation_name: Name of the operation.
            
        Returns:
            AgentResult with equipment validation.
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

        # Extract equipment-related sections from documents
        docs_summary = "\n\n".join(
            f"### {name}\n\n{text[:6000]}..."
            for name, text in documents.items()
        )
        
        agent1_output = previous_outputs.get("agent1", "")
        
        user_prompt = (
            "You are validating equipment specifications for BOP standardization.\n\n"
            "# Documents (Equipment Sections)\n\n"
            f"{docs_summary}\n\n"
            "# Agent 1 Comparison (for context)\n\n"
            f"{agent1_output[:4000]}...\n\n"
            "Extract and compare all equipment specifications. Assess standardization feasibility."
        )
        
        return self.agent.run(user_prompt, backend=backend)
