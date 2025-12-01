### Mission Snapshot
- Multi-agent workflow in `src/workflow/orchestrator.py` runs agents 1→5 (`src/agents/*`, prompts under `prompts/AGENT-*`) to compare rig ROP/JSAs, detect gaps, and draft ADNOC-standard outputs.
- Documents are ingested into a single text blob; each agent receives the raw `documents` dict plus cumulative `previous_outputs` keys (`agent1` … `agent5`).

### Data & Ingestion
- Canonical input is `production-data-bop-real.txt` built by `scripts/convert_pdfs_to_text.py` using headers like `=== RIG: DANA – BOP INSTALLATION ROP ===`; see `data/sample/test-data-bop-installation.txt` for structure.
- `src/ingestion/list_rigs.py` and `src/ingestion/extract_text.py` expect PDFs/DOCX in `data/source_documents/<Rig>/`; unsupported files are skipped, extraction errors are logged inline.
- When adding ingestion features, preserve UTF-8 writes and `Path` usage, and keep auto-mode optional because manual curation remains the accuracy baseline.

### Agent Contracts
- Each agent wrapper loads its system prompt from `prompts/…` and delegates to `src/agents/base.LLMAgent`; defaults exist but treat prompt files as source of truth.
- `LLMAgent` lazily initializes OpenAI/Anthropic clients via `.env` values (`src/config.py`). Respect `_get_*_client` helpers so tests can patch them.
- Pass `backend` explicitly through agents; new agents should mirror the save pattern to emit `<name>.md` plus `<name>.meta.json` for traceability.

### Orchestration & Outputs
- `ADNOCWorkflow.run_complete_workflow()` timestamps runs under `outputs/<operation>/<YYYYmmdd-HHMMSS>/` and saves Markdown, metadata, and `summary.json` aggregating tokens + durations.
- Always update the `summary` structure if you add metrics; `tests/unit/test_workflow/test_orchestrator.py` asserts file names and summary contents (5 entries, token totals, etc.).
- Keep log prints consistent (ASCII banners, “Running Agent X”) because downstream automations scrape stdout to show progress.

### Execution Shortcuts
- `Makefile` targets: `install` (venv + deps), `list-rigs`, `extract-auto`, `workflow-openai`, `workflow-claude`, `test`; override `OPERATION`, `DOCS_FILE`, `SOURCE_DIR` via environment.
- Single-command runners live in `scripts/`: `openai_api_deployment.py`, `claude_api_deployment.py`, and `run_bop_auto.py` (orchestrates list→extract→run).
- `scripts/test_api_connection.py` validates env keys and can perform minimal API calls; keep it lightweight to stay CI-friendly.

### Environment & Secrets
- Copy `.env.example` to `.env`; `src/config.Settings.validate()` requires at least one of `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` before the workflow runs.
- Default models (`gpt-4o`, `claude-3-5-sonnet-20241022`) and `TEMPERATURE=0.2` live in env vars; expose overrides via CLI flags only if you also update `Settings`.

### Testing & CI
- `pytest.ini` pins `tests/` as the root with `-v --tb=short`; unit tests rely on fixtures in `tests/conftest.py` that mock env vars, LLM clients, and temp rigs.
- CI (`.github/workflows/python-package.yml`) runs flake8, pytest across Python 3.9–3.11, and uploads coverage on 3.11; keep new dependencies compatible with that matrix.
- When writing tests for new agents/components, follow the existing pattern: return `AgentResult` instances, assert file outputs via temporary directories, and avoid real API calls.

### Coding Patterns
- Prefer `pathlib.Path`, explicit UTF-8 reads/writes, and structured print banners for user feedback.
- Gate any filesystem writes behind `Path.mkdir(parents=True, exist_ok=True)`; outputs are treated as immutable run artifacts.
- Keep instructions and docstrings actionable—operators rely on CLI help text baked into the scripts.
- Reuse `documents` + `previous_outputs` payloads to thread context instead of re-reading files inside agents.
