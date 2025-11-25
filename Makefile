# Makefile for agentic BOP workflow

PYTHON := python
VENV := .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python

OPERATION ?= BOP Installation
DOCS_FILE ?= production-data-bop-real.txt
SOURCE_DIR ?= data/source_documents

.PHONY: install list-rigs extract-auto workflow-openai workflow-claude clean test

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "\n✓ Virtual environment created and dependencies installed"
	@echo "Activate with: source $(VENV)/bin/activate"

list-rigs:
	$(PY) scripts/list_available_rigs.py --source-dir $(SOURCE_DIR)

extract-auto:
	$(PY) scripts/convert_pdfs_to_text.py --auto --source-dir $(SOURCE_DIR) --output-file $(DOCS_FILE)

workflow-openai:
	$(PY) scripts/openai_api_deployment.py --operation "$(OPERATION)" --documents-file $(DOCS_FILE)

workflow-claude:
	$(PY) scripts/claude_api_deployment.py --operation "$(OPERATION)" --documents-file $(DOCS_FILE)

test:
	$(PY) scripts/test_api_connection.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✓ Cleaned up Python cache files"

help:
	@echo "Available targets:"
	@echo "  install          - Create virtual environment and install dependencies"
	@echo "  list-rigs        - List available rigs in source directory"
	@echo "  extract-auto     - Auto-extract text from PDFs/DOCX"
	@echo "  workflow-openai  - Run full workflow with OpenAI"
	@echo "  workflow-claude  - Run full workflow with Claude"
	@echo "  test             - Test API connectivity"
	@echo "  clean            - Remove Python cache files"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "Example usage:"
	@echo "  make workflow-openai OPERATION=\"BOP Installation\""
