# Integrated "All Agents" Compliance Template

## (ADNOC Offshore Drilling - Field & Audit Ready)

---

## Document Purpose

This template provides a fully integrated, field-ready set of instructions that combine the strengths and compliance depth of all five original specialist agents. It is structured to maximize clarity, auditability, and operational control, fully aligned with ADNOC HSE and operational excellence expectations.

**Usage**: This master template serves as the governing reference for all agent operations. Each individual agent prompt (AGENT-1 through AGENT-5) implements the specific section requirements defined here.

---

## Section 1: Rig Procedure Technical Writer

**Role:**

* Rewrite and modernize Rig Operating Procedures (ROPs) for ADNOC offshore rigs.

**Success Criteria:**

* Procedures are safe, clear, compliant, practical, and trusted by all users.
* All controls are mapped to relevant ADNOC Corporate Practices (HSE-PSW-CP01 to CP22, GHSE-MAN-05, etc.).
* Outcomes: Zero incidents due to procedural failure, >95% compliance in audits, and no operational delays resulting from unclear procedures.

**Key Tasks:**

* Accurately reflect rig-specific equipment and operational conditions.
* Test procedures against real-world constraints (time, resources, crew capability).
* Maintain up-to-date references and documentation controls (revision history, approvals, distribution lists).

**Implementing Agent:** Agent 1 (Comparison Analyst) initiates the analysis; Agent 5 (Standardisation Writer) produces the final ROP.

---

## Section 2: Gap Detector (Compliance & Coverage)

**Role:**

* Identify and report gaps, mismatches, and missing controls in procedures to ensure full compliance and field usability.

**Stepwise Instructions:**

1. Map every step and control in the ROP against all relevant ADNOC CPs (list each CP in a comparison matrix).
2. Highlight all missing, incomplete, or unclear controls or requirements.
3. Flag any procedural gaps that could impact safety, audit readiness, or usability at the rig.
4. Recommend targeted remediation actions for each gap.
5. Clearly document all findings, references, and actions taken, ensuring traceability.

**Output:**

* A fully auditable, traceable gap analysis report formatted for both management and field review.

**Implementing Agent:** Agent 2 (Gap Detector)

**Reference:** See `AGENT-2-GAP-DETECTOR.md` for detailed implementation.

---

## Section 3: Human Performance (HP) Evaluator

**Role:**

* Ensure robust integration of human factors and behavioral safety in all procedures.

**Instructions:**

1. Review procedure language for clarity, error traps, and "crew-friendly" sequencing.
2. Identify steps with elevated risk of human error or misunderstanding.
3. Recommend explicit error prevention and remediation controls (such as checklists, cross-checks, and situational warnings).
4. Integrate behavioral safety cues, peer verification, and resilience engineering concepts throughout.
5. Document all identified human performance risks and corresponding mitigations for every critical step.

**Outcome:**

* An annotated procedure highlighting all human-factor risks and mitigations, supporting continuous improvement.

**Implementing Agent:** Agent 3 (HP Evaluator)

**Reference:** See `AGENT-3-HP-EVALUATOR.md` for detailed implementation.

---

## Section 4: Equipment Validator

**Role:**

* Validate that all tools, equipment, and materials are correct, ADNOC-compliant, and available for every procedure step.

**Instructions:**

1. Cross-check all equipment and tool references against the latest ADNOC-approved lists.
2. Highlight any obsolete, missing, or non-compliant items.
3. Ensure every critical step lists required equipment with catalog numbers and specification references.
4. Recommend substitutions or updates as needed to maintain compliance and operational efficiency.
5. Document findings in a structured validation table (step, equipment/tool, compliance status, comments).

**Output:**

* A complete equipment validation matrix, attached to the ROP for use in pre-task checks and audits.

**Implementing Agent:** Agent 4 (Equipment Validator)

**Reference:** See `AGENT-4-EQUIPMENT-VALIDATOR.md` for detailed implementation.

---

## Section 5: Standardisation Writer (Formatting & Language)

**Role:**

* Guarantee unified language, structure, and format across all ROPs in line with ADNOC documentation standards.

**Key Requirements:**

1. Apply official ADNOC ROP templates, including section headers, style guide (font, color, logos, revision boxes).
2. Standardize all risk and control phrases, abbreviations, and terminology (provide a glossary or footnotes where needed).
3. Remove redundancies, inconsistencies, and formatting errors (using a pre/post checklist).
4. Enforce "One ADNOC" voice: active, direct, instructional, and relevant to field operations.
5. Prepare the document for upload to ADNOC document control systems and digital platforms (M365 Copilot, SAP Fiori, SharePoint, etc.), with correct metadata and version control.

**Output:**

* A final, field-ready procedure with full ADNOC formatting and complete revision history.

**Implementing Agent:** Agent 5 (Standardisation Writer)

**Reference:** See `AGENT-5-STANDARDISATION-WRITER.md` for detailed implementation.

---

## Section 6: Integrated Workflow & Accountability Table

| Agent/Section | Main Responsibilities | Output/Deliverable | Accountable Role(s) |
|---------------|----------------------|-------------------|---------------------|
| Agent 1 - Technical Writer/Comparison | Drafting, compliance, document control, comparison analysis | Draft & Final ROP, control page, comparison report | Procedure SME, Technical Writer |
| Agent 2 - Gap Detector | Compliance mapping, reporting, closure | Gap matrix, action log | Compliance/QA Lead |
| Agent 3 - HP Evaluator | HP error-proofing, behavioral safety | Annotated ROP, HP risk table | HP Specialist, HSE |
| Agent 4 - Equipment Validator | Tools/equipment compliance | Equipment validation matrix | Maintenance, Operations |
| Agent 5 - Standardisation Writer | Formatting, language, revision control, final synthesis | Field-ready, standardized ROP | Document Control, Technical Writer |

### Workflow Sequence

```
┌─────────────────┐
│  Input Documents │
│  (ROPs, JSAs)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent 1:       │ ──► Comparison Analysis Output
│  Comparison     │
│  Analyst        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent 2:       │ ──► Gap Analysis Report
│  Gap Detector   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent 3:       │ ──► HP Evaluation & Risk Table
│  HP Evaluator   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent 4:       │ ──► Equipment Validation Matrix
│  Equipment      │
│  Validator      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent 5:       │ ──► Final Standardized ROP + JSA
│  Standardisation│     + Implementation Package
│  Writer         │
└─────────────────┘
```

### Data Flow

Each agent receives:
- **Original Documents**: Input ROPs and JSAs
- **Previous Agent Outputs**: All outputs from preceding agents in the workflow

This ensures cumulative knowledge building and comprehensive coverage.

---

## Section 7: References & Document Control

### Mandatory References

* All relevant ADNOC Corporate Practices (HSE-PSW-CP01 to CP22, GHSE-MAN-05, etc.)
* IOGP Life Saving Rules, ADNOC Safety Flashes, and rig-specific manuals
* The latest ADNOC ROP template and style guide
* ADNOC master equipment/tool lists
* API Standards (API Spec 53, API RP 53)
* IADC Guidelines for BOP Installation and Testing

### ADNOC Corporate Practices Reference Matrix

| CP Number | Title | Applicable Sections |
|-----------|-------|---------------------|
| HSE-PSW-CP01 | HSE Management System | All |
| HSE-PSW-CP02 | Risk Management | Sections 2, 3 |
| HSE-PSW-CP03 | Permit to Work | Section 1, 5 |
| HSE-PSW-CP04 | Lifting Operations | Section 4 |
| HSE-PSW-CP05 | Pressure Testing | Section 4 |
| HSE-PSW-CP06 | Lockout/Tagout | Section 4 |
| HSE-PSW-CP07 | Working at Height | Section 4 |
| HSE-PSW-CP08 | Confined Space | Section 4 |
| HSE-PSW-CP09 | Process Safety Management | Sections 2, 3 |
| HSE-PSW-CP10 | Emergency Response | Section 1, 5 |
| HSE-PSW-CP11-22 | Various HSE Requirements | As applicable |
| GHSE-MAN-05 | Global HSE Manual | All |

### Document Control

* Maintain a full revision history, approval record, and distribution list in line with the ADNOC template.
* Attach all supporting matrices, gap analyses, and validation tables as appendices.
* Use standardized document numbering: `ADNOC-AOD-ROP-XXX-Rev.X`
* Version control format: Major.Minor (e.g., 1.0, 1.1, 2.0)

### Revision History Template

| Revision | Date | Author | Description of Changes | Approved By |
|----------|------|--------|----------------------|-------------|
| 1.0 | YYYY-MM-DD | Name | Initial release | Name/Role |
| 1.1 | YYYY-MM-DD | Name | Minor updates per field feedback | Name/Role |

---

## Section 8: Quality Assurance Checklist

Before finalizing any ROP, verify completion of all sections:

### Pre-Release Checklist

- [ ] **Agent 1 Output**: Comparison analysis complete and reviewed
- [ ] **Agent 2 Output**: All gaps identified and remediation planned
- [ ] **Agent 3 Output**: HP risks assessed and mitigations in place
- [ ] **Agent 4 Output**: Equipment validation matrix complete
- [ ] **Agent 5 Output**: Final ROP formatted per ADNOC standards

### Compliance Verification

- [ ] All ADNOC CPs mapped and referenced
- [ ] IOGP Life Saving Rules integrated
- [ ] Critical controls clearly identified
- [ ] HOLD POINTS defined for critical decisions
- [ ] Emergency procedures included
- [ ] Sign-off blocks for all required approvals

### Field Readiness

- [ ] Language is clear, active, and imperative
- [ ] Steps are numbered and sequenced logically
- [ ] Equipment specifications are complete and accurate
- [ ] Checklists and verification steps included
- [ ] Rig-specific appendices complete (where applicable)

---

## Section 9: Completion & Usage Instructions

* Each section above must be completed in full for every procedure revision.
* All findings, supporting matrices, and validation outputs must be included as appendices.
* Maintain all outputs for audit, investigation, and ongoing improvement reviews.
* This template is the official controlling document for all ROP development, review, and deployment activities in ADNOC Offshore Drilling operations.

### Implementation Workflow

1. **Initiation**: Gather source documents (existing ROPs, JSAs, equipment lists)
2. **Analysis Phase**: Run Agents 1-4 sequentially
3. **Synthesis Phase**: Agent 5 produces final deliverables
4. **Review**: Subject matter experts review outputs
5. **Approval**: Management sign-off per document control requirements
6. **Distribution**: Deploy to rigs and document control systems
7. **Training**: Conduct crew training on new/revised procedures
8. **Monitoring**: Track compliance and gather feedback for continuous improvement

---

## Section 10: Glossary of Terms

| Term | Definition |
|------|------------|
| BOP | Blowout Preventer - a large valve assembly used to control well pressure |
| CP | Corporate Practice - ADNOC standard operating requirement |
| HP | Human Performance - focus on human factors in safety |
| JSA | Job Safety Analysis - systematic hazard identification for tasks |
| ROP | Rig Operating Procedure - step-by-step operational instructions |
| SIMOPS | Simultaneous Operations - concurrent activities requiring coordination |
| SWL | Safe Working Load - maximum rated load for lifting equipment |
| HOLD POINT | Mandatory pause requiring supervisor approval to proceed |
| Critical Control | Essential barrier preventing catastrophic outcomes |

---

## Appendix A: Agent Prompt File Mapping

| Section | Agent | Prompt File |
|---------|-------|-------------|
| Technical Writer/Comparison | Agent 1 | `AGENT-1-PROMPT-TEMPLATE.md` |
| Gap Detector | Agent 2 | `AGENT-2-GAP-DETECTOR.md` |
| HP Evaluator | Agent 3 | `AGENT-3-HP-EVALUATOR.md` |
| Equipment Validator | Agent 4 | `AGENT-4-EQUIPMENT-VALIDATOR.md` |
| Standardisation Writer | Agent 5 | `AGENT-5-STANDARDISATION-WRITER.md` |

---

## Appendix B: Output File Structure

When the workflow completes, outputs are organized as:

```
outputs/{operation_name}/{timestamp}/
├── agent1_comparison.md          # Comparison analysis
├── agent1_comparison.meta.json   # Metadata
├── agent2_gaps.md                # Gap analysis
├── agent2_gaps.meta.json
├── agent3_hp_evaluation.md       # HP evaluation
├── agent3_hp_evaluation.meta.json
├── agent4_equipment_validation.md # Equipment validation
├── agent4_equipment_validation.meta.json
├── agent5_standardisation.md     # Final standardized ROP + JSA
├── agent5_standardisation.meta.json
└── summary.json                  # Aggregated workflow metrics
```

---

**End of Template**

*Document Control: ADNOC-AOD-INTEGRATED-COMPLIANCE-TEMPLATE*
*Version: 1.0*
*Effective Date: 2024*
