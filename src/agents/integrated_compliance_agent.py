"""Integrated Compliance Agent - All-in-one ADNOC ROP development agent."""

from pathlib import Path
from typing import Dict, Any

from src.agents.base import LLMAgent, AgentResult


class IntegratedComplianceAgent:
    """Integrated Compliance Agent for ADNOC offshore drilling operations.

    This agent combines the full capabilities of all five specialist agents:
    1. Rig Procedure Technical Writer - Drafts and modernizes ROPs
    2. Gap Detector - Identifies compliance and coverage gaps
    3. HP Evaluator - Ensures human performance and behavioral safety
    4. Equipment Validator - Validates tools and equipment compliance
    5. Standardisation Writer - Applies ADNOC formatting and language standards

    The output is a complete, field-ready ROP package that includes:
    - Fully compliant Rig Operating Procedure
    - Gap analysis with closure actions
    - Human performance risk assessment and mitigations
    - Equipment validation matrix
    - Standardized formatting per ADNOC template requirements
    - Full traceability and document control
    """

    def __init__(
        self,
        prompt_path: str = "prompts/ADNOC-INTEGRATED-COMPLIANCE-TEMPLATE.md"
    ):
        """Initialize the integrated compliance agent.

        Args:
            prompt_path: Path to the integrated compliance template file.
        """
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            system_prompt = prompt_file.read_text(encoding="utf-8")
        else:
            system_prompt = self._get_default_prompt()

        self.agent = LLMAgent("Integrated Compliance Agent", system_prompt)

    def _get_default_prompt(self) -> str:
        """Get default system prompt if template file is not found."""
        return """# Integrated Compliance Agent

You are the Integrated Compliance Agent for ADNOC's offshore drilling operations.

Your mission is to produce a complete, field-ready ROP package that combines the work of:
1. Rig Procedure Technical Writer
2. Gap Detector
3. HP Evaluator
4. Equipment Validator
5. Standardisation Writer

## Key Requirements

### Technical Writing
- Draft clear, compliant procedures
- Map controls to ADNOC Corporate Practices (HSE-PSW-CP01 to CP22)
- Use active voice, imperative mood
- Include HOLD POINTS for critical decisions

### Gap Detection
- Map every step against relevant ADNOC CPs
- Identify missing, incomplete, or unclear controls
- Recommend targeted remediation actions
- Document all findings with traceability

### Human Performance
- Review for clarity and error traps
- Identify high-risk steps
- Apply error prevention controls
- Integrate behavioral safety cues

### Equipment Validation
- Cross-check equipment against approved lists
- Verify compliance status
- Document catalog numbers and specifications
- Recommend substitutions as needed

### Standardisation
- Apply ADNOC ROP template format
- Enforce consistent terminology
- Prepare for digital platform upload
- Include full document control

## Output Structure

1. Part 1: Rig Operating Procedure (full ROP per ADNOC template)
2. Part 2: Gap Analysis Report
3. Part 3: Human Performance Assessment
4. Part 4: Equipment Validation Matrix
5. Part 5: Document Control & Appendices
6. Part 6: Compliance Certification

Produce a complete, audit-ready package.
"""

    def run(
        self,
        documents: Dict[str, str],
        context: Dict[str, Any] = None,
        backend: str = "openai",
    ) -> AgentResult:
        """Execute integrated compliance analysis and ROP generation.

        This method processes source documents and produces a complete
        ROP package including all compliance artifacts.

        Args:
            documents: Dictionary mapping document names to their text content.
                       Keys should describe the document type (e.g., "Existing ROP",
                       "JSA", "Equipment List", "Permits").
            context: Optional additional context including:
                     - rig_name: Name of the target rig
                     - operation_type: Type of operation (e.g., "BOP Installation")
                     - adnoc_cps: List of applicable Corporate Practices
                     - constraints: Any rig-specific constraints
            backend: LLM backend to use ("openai" or "anthropic").

        Returns:
            AgentResult with complete ROP package including:
            - Full Rig Operating Procedure
            - Gap Analysis Report
            - Human Performance Assessment
            - Equipment Validation Matrix
            - Document Control and Appendices

        Example:
            >>> agent = IntegratedComplianceAgent()
            >>> docs = {
            ...     "Existing ROP": "...",
            ...     "JSA": "...",
            ...     "Equipment List": "..."
            ... }
            >>> context = {
            ...     "rig_name": "Dana",
            ...     "operation_type": "BOP Installation"
            ... }
            >>> result = agent.run(docs, context, backend="anthropic")
            >>> print(result.content)
        """
        context = context or {}

        # Build comprehensive user prompt
        user_prompt = self._build_user_prompt(documents, context)

        return self.agent.run(user_prompt, backend=backend)

    def _build_user_prompt(
        self,
        documents: Dict[str, str],
        context: Dict[str, Any]
    ) -> str:
        """Build the user prompt from documents and context.

        Args:
            documents: Source documents to analyze.
            context: Additional context for the analysis.

        Returns:
            Formatted user prompt string.
        """
        # Extract context fields
        rig_name = context.get("rig_name", "Not specified")
        operation_type = context.get("operation_type", "ROP Development")
        adnoc_cps = context.get("adnoc_cps", [])
        constraints = context.get("constraints", "None specified")

        # Build document section
        doc_sections = []
        for name, content in documents.items():
            # Truncate very large documents
            if len(content) > 10000:
                content = content[:10000] + "\n\n[... Document truncated for processing ...]"
            doc_sections.append(f"## {name}\n\n{content}")

        documents_text = "\n\n---\n\n".join(doc_sections)

        # Build CP reference section if provided
        cp_section = ""
        if adnoc_cps:
            cp_list = "\n".join(f"- {cp}" for cp in adnoc_cps)
            cp_section = f"""
## Applicable ADNOC Corporate Practices

{cp_list}
"""

        # Construct complete prompt
        prompt = f"""# Integrated Compliance Analysis Request

## Context

- **Rig Name**: {rig_name}
- **Operation Type**: {operation_type}
- **Constraints**: {constraints}
{cp_section}

## Source Documents

{documents_text}

---

## Instructions

Using the integrated compliance template, produce a complete ROP package that includes:

1. **Part 1: Rig Operating Procedure**
   - Follow ADNOC ROP template structure exactly
   - All 13 required sections must be present
   - Include HOLD POINTS and critical controls

2. **Part 2: Gap Analysis Report**
   - Map against all applicable ADNOC CPs
   - Identify all gaps with priority ratings
   - Provide remediation actions for each gap

3. **Part 3: Human Performance Assessment**
   - Identify error-prone steps
   - Document HP controls applied
   - Include verification requirements

4. **Part 4: Equipment Validation Matrix**
   - List all equipment with catalog numbers
   - Verify compliance status
   - Flag any non-compliant items

5. **Part 5: Document Control & Appendices**
   - Revision history
   - Distribution list
   - All supporting matrices

6. **Part 6: Compliance Certification**
   - Confirm review against all requirements
   - Signature blocks for approval

Ensure the output is:
- Field-ready and immediately usable
- Audit-compliant with full traceability
- Consistent in terminology and formatting
- Aligned with ADNOC operational excellence standards

Proceed with the complete integrated analysis.
"""

        return prompt

    def run_with_previous_outputs(
        self,
        documents: Dict[str, str],
        previous_outputs: Dict[str, Any],
        context: Dict[str, Any] = None,
        backend: str = "openai",
    ) -> AgentResult:
        """Execute with previous agent outputs for enhanced context.

        This method can be used when individual agents have already run
        and their outputs should be incorporated into the integrated analysis.

        Args:
            documents: Original source documents.
            previous_outputs: Dictionary with keys like "agent1", "agent2", etc.
                             containing outputs from individual agent runs.
            context: Optional additional context.
            backend: LLM backend to use.

        Returns:
            AgentResult with enhanced integrated analysis.
        """
        context = context or {}

        # Build base prompt
        base_prompt = self._build_user_prompt(documents, context)

        # Add previous outputs if available
        previous_sections = []

        if "agent1" in previous_outputs:
            output = previous_outputs["agent1"]
            if len(output) > 5000:
                output = output[:5000] + "\n[... truncated ...]"
            previous_sections.append(
                f"## Previous Analysis: Comparison (Agent 1)\n\n{output}"
            )

        if "agent2" in previous_outputs:
            output = previous_outputs["agent2"]
            if len(output) > 4000:
                output = output[:4000] + "\n[... truncated ...]"
            previous_sections.append(
                f"## Previous Analysis: Gap Detection (Agent 2)\n\n{output}"
            )

        if "agent3" in previous_outputs:
            output = previous_outputs["agent3"]
            if len(output) > 4000:
                output = output[:4000] + "\n[... truncated ...]"
            previous_sections.append(
                f"## Previous Analysis: HP Evaluation (Agent 3)\n\n{output}"
            )

        if "agent4" in previous_outputs:
            output = previous_outputs["agent4"]
            if len(output) > 4000:
                output = output[:4000] + "\n[... truncated ...]"
            previous_sections.append(
                f"## Previous Analysis: Equipment Validation (Agent 4)\n\n{output}"
            )

        if "agent5" in previous_outputs:
            output = previous_outputs["agent5"]
            if len(output) > 5000:
                output = output[:5000] + "\n[... truncated ...]"
            previous_sections.append(
                f"## Previous Analysis: Standardisation (Agent 5)\n\n{output}"
            )

        if previous_sections:
            previous_text = "\n\n---\n\n".join(previous_sections)
            enhanced_prompt = f"""{base_prompt}

---

## Previous Agent Analyses (For Reference)

The following analyses have already been performed. Incorporate their findings
into your integrated output while ensuring consistency and completeness.

{previous_text}
"""
        else:
            enhanced_prompt = base_prompt

        return self.agent.run(enhanced_prompt, backend=backend)
