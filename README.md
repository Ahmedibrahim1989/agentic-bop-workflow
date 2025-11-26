# Agentic BOP Standardisation Workflow

This project implements a repeatable, traceable and scalable **multi-agent workflow**
for comparing rig operating procedures (ROPs) and job safety analyses (JSAs) across
multiple rigs, and generating standardised ADNOC-aligned procedures.

It is designed to be:

- **Repeatable** – same inputs + same config ⇒ same outputs
- **Traceable** – every run produces timestamped outputs and metadata
- **Scalable** – add rigs, documents or agents without changing the core pipeline

---

## 1. Architecture overview

### 1.1 High-level flow

```mermaid
flowchart LR
    A[Source PDFs/DOCX per rig] --> B[Ingestion: extract_text.py]
    B --> C[Combined text file: production-data-bop-real.txt]
    C --> D[ADNOCWorkflow.run_complete_workflow()]
    D --> E1[Agent 1: Comparison Analyst]
    E1 --> E2[Agent 2: Gap Detector]
    E2 --> E3[Agent 3: HP Evaluator]
    E3 --> E4[Agent 4: Equipment Validator]
    E4 --> E5[Agent 5: Standardisation Writer]
    E5 --> F[Outputs directory with timestamped results]
```

### 1.2 Data-flow pipeline

1. **Raw documents**

   * Location: `data/source_documents/<RigName>/`
   * Formats: PDF / DOCX for ROPs and JSAs.

2. **Rig discovery**

   * `scripts/list_available_rigs.py` scans `data/source_documents/`
   * Outputs the list of rig folders (e.g. Dana, AlJubail, AlReem, Marawwah).

3. **Text extraction & compilation**

   * `scripts/convert_pdfs_to_text.py`
   * Manual mode: prints instructions to copy/paste clean text into a single `.txt` file.
   * Auto mode (`--auto`): uses PyPDF2 / python-docx to extract text into
     `production-data-bop-real.txt` in the project root.

4. **Combined text file format**

   * Matches `data/sample/test-data-bop-installation.txt`:

     * Each rig section starts with a marker like:
       `=== RIG: DANA – BOP INSTALLATION ROP ===`
     * Sections separated by blank lines.
     * ROP sections contain risk assessments, permits, critical lifts, equipment lists, steps.
     * JSA sections contain step-by-step hazard/control tables.

5. **Agentic workflow orchestration**

   * `src/workflow/orchestrator.py` provides `ADNOCWorkflow`.
   * `scripts/claude_api_deployment.py` and `scripts/openai_api_deployment.py` wire agents to LLM backends.
   * `run_complete_workflow(operation_name, documents_dict)`:

     * Creates `outputs/<operation>/<timestamp>/` directory.
     * Runs agents 1 → 5 sequentially.
     * Saves each agent output as Markdown and its metadata (tokens, timing) as JSON.
     * Writes a summary report aggregating metrics.

6. **Outputs**

   * Location: `outputs/<operation>/<timestamp>/`
   * Contents:

     * `agent1_comparison.md`, `agent2_gaps.md`, …, `agent5_standardised_rop_jsa.md`
     * `agent1_comparison.meta.json`, …
     * `summary.json` with total tokens, durations and basic run info.

---

## 2. Agent roles

Each agent has:

* A **prompt template** in `prompts/`
* A **Python class** in `src/agents/`
* A **logical responsibility** in the workflow

| Agent | File (prompt)                       | Class (code)                                                     | Purpose                                                                                                                    |
| ----- | ----------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 1     | `AGENT-1-PROMPT-TEMPLATE.md`        | `ComparisonAgent` (`comparison_agent.py`)                        | Inventory all docs, map structure, perform line-by-line comparison of ROPs & JSAs, highlight variances and best practices. |
| 2     | `AGENT-2-GAP-DETECTOR.md`           | `GapDetectorAgent` (`gap_detector_agent.py`)                     | Analyse Agent 1 output to find missing steps, hazards, misalignments between ROPs and JSAs.                                |
| 3     | `AGENT-3-HP-EVALUATOR.md`           | `HPEvaluatorAgent` (`hp_evaluator_agent.py`)                     | Evaluate human-performance maturity, critical step verification, checklists, barriers.                                     |
| 4     | `AGENT-4-EQUIPMENT-VALIDATOR.md`    | `EquipmentValidatorAgent` (`equipment_validator_agent.py`)       | Extract and compare equipment specs, assess feasibility of standardisation per rig.                                        |
| 5     | `AGENT-5-STANDARDISATION-WRITER.md` | `StandardisationWriterAgent` (`standardisation_writer_agent.py`) | Synthesise all findings into standardised ROP + JSA and implementation package.                                            |

Each agent receives:

* `documents`: prepared text per rig / doc
* `previous_outputs`: dict of previous agents' results
* A specific prompt template

and returns:

* `content`: Markdown body
* `meta`: basic metadata (tokens used, duration, etc.)

---

## 3. Environment & installation

### 3.1 Python environment

```bash
# From project root
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2 Environment variables

Copy `.env.example` to `.env` and fill in keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
ANTHROPIC_API_KEY="your-anthropic-key"
OPENAI_API_KEY="your-openai-key"
MODEL_NAME_OPENAI="gpt-4o"
MODEL_NAME_ANTHROPIC="claude-3-5-sonnet"
TEMPERATURE="0.2"
```

### 3.3 Test API connectivity

```bash
python scripts/test_api_connection.py
```

This will:

* Confirm it can see the environment variables
* Optionally probe OpenAI / Anthropic (if keys are present)
* Report success / failure without using sensitive data

---

## 4. Running the workflow

Assume your PDFs/DOCX are under:

```text
data/source_documents/Dana/...
data/source_documents/AlJubail/...
...
```

### 4.1 List available rigs

```bash
python scripts/list_available_rigs.py
```

Optional: specify custom source directory:

```bash
python scripts/list_available_rigs.py --source-dir data/source_documents
```

### 4.2 Build combined text file

**Manual-guided (recommended for highest accuracy):**

```bash
python scripts/convert_pdfs_to_text.py
```

This prints instructions on how to:

* Open each PDF/DOCX
* Copy text into `production-data-bop-real.txt`
* Use headings like `=== RIG: DANA – BOP INSTALLATION ROP ===`

**Automatic extraction (optional):**

```bash
python scripts/convert_pdfs_to_text.py \
  --auto \
  --source-dir data/source_documents \
  --output-file production-data-bop-real.txt
```

You must manually verify the resulting file, as PDF extraction can mis-handle tables and formatting.

### 4.3 Run full multi-agent workflow (OpenAI)

```bash
python scripts/openai_api_deployment.py \
  --operation "BOP Installation" \
  --documents-file production-data-bop-real.txt
```

### 4.4 Run full multi-agent workflow (Claude)

```bash
python scripts/claude_api_deployment.py \
  --operation "BOP Installation" \
  --documents-file production-data-bop-real.txt
```

Outputs will appear under:

```text
outputs/BOP Installation/<timestamp>/
```

---

## 5. Makefile & Codex CLI usage

### 5.1 Makefile targets

Use `make` for reproducible commands:

* `make install` – create venv and install dependencies
* `make list-rigs` – list rigs in `data/source_documents`
* `make extract-auto` – auto text extraction
* `make workflow-openai` – run full workflow with OpenAI
* `make workflow-claude` – run full workflow with Claude

Example:

```bash
make workflow-openai OPERATION="BOP Installation"
```

### 5.2 Codex CLI integration

If you're using Codex CLI to execute the pipeline end-to-end, you can wrap commands in a script or directly:

```bash
# 1. Extract documents (manual guidance)
codex run python scripts/convert_pdfs_to_text.py

# Or auto extraction
codex run python scripts/convert_pdfs_to_text.py \
  --auto \
  --source-dir data/source_documents \
  --output-file production-data-bop-real.txt

# 2. Run workflow with Claude
codex run python scripts/claude_api_deployment.py \
  --operation "BOP Installation" \
  --documents-file production-data-bop-real.txt

# Or with OpenAI
codex run python scripts/openai_api_deployment.py \
  --operation "BOP Installation" \
  --documents-file production-data-bop-real.txt
```

Because `run_complete_workflow()` takes explicit inputs (operation name, documents) and writes into timestamped output folders, every Codex CLI run is repeatable and auditable.

---

## 6. Extending the system

### 6.1 Adding more rigs

1. Drop additional PDFs/DOCX into `data/source_documents/<RigName>/`.
2. Run `list_available_rigs.py` to confirm detection.
3. Re-run `convert_pdfs_to_text.py` and the workflow.

No changes to code are required.

### 6.2 Adding a new agent (e.g. Environmental Analyst)

1. Add a prompt: `prompts/AGENT-6-ENVIRONMENTAL-ANALYST.md`
2. Add a class: `src/agents/environmental_analyst_agent.py`
3. Register it in `src/workflow/orchestrator.py` in the `AGENT_ORDER` sequence and wiring.
4. The orchestrator will automatically pass previous outputs to the new agent.

### 6.3 Switching models

Change `MODEL_NAME_OPENAI`, `MODEL_NAME_ANTHROPIC`, or temperature in `.env`.
The orchestrator uses a simple `LLMAgent` abstraction, so backends are swappable without rewriting agent logic.

---

## 7. Traceability practices

* **Version control**: commit scripts, prompts, configs and outputs (or at least metadata) per run.
* **Output directories**: never overwrite; each run uses a timestamped folder.
* **Metadata JSON**: store token counts, timestamps, model names in `*.meta.json` and `summary.json`.
* **Reviews & sign-off**: attach the summary report and key outputs to GitHub pull requests for structured review.

---

## 8. Project structure

```text
agentic-bop-workflow/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ Makefile
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ ingestion/
│  │  ├─ __init__.py
│  │  ├─ list_rigs.py
│  │  └─ extract_text.py
│  ├─ agents/
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ comparison_agent.py
│  │  ├─ gap_detector_agent.py
│  │  ├─ hp_evaluator_agent.py
│  │  ├─ equipment_validator_agent.py
│  │  └─ standardisation_writer_agent.py
│  └─ workflow/
│     ├─ __init__.py
│     └─ orchestrator.py
├─ scripts/
│  ├─ list_available_rigs.py
│  ├─ convert_pdfs_to_text.py
│  ├─ claude_api_deployment.py
│  ├─ openai_api_deployment.py
│  ├─ run_bop_auto.py
│  └─ test_api_connection.py
├─ prompts/
│  ├─ AGENT-1-PROMPT-TEMPLATE.md
│  ├─ AGENT-2-GAP-DETECTOR.md
│  ├─ AGENT-3-HP-EVALUATOR.md
│  ├─ AGENT-4-EQUIPMENT-VALIDATOR.md
│  └─ AGENT-5-STANDARDISATION-WRITER.md
└─ data/
   ├─ source_documents/
   │  └─ (rig folders: Dana/, AlJubail/, … with PDFs/DOCX)
   └─ sample/
      └─ test-data-bop-installation.txt
```

---

## License

MIT License - See LICENSE file for details.

---

## Contact

For questions or contributions, please open an issue on GitHub.
