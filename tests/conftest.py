"""Shared test fixtures for the agentic-bop-workflow test suite."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Environment Fixtures
# =============================================================================

@pytest.fixture
def clean_env():
    """Provide a clean environment without API keys."""
    env_backup = os.environ.copy()
    # Remove API keys if present
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("ANTHROPIC_API_KEY", None)
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(env_backup)


@pytest.fixture
def env_with_openai_key():
    """Provide environment with only OpenAI key."""
    env_backup = os.environ.copy()
    os.environ["OPENAI_API_KEY"] = "test-openai-key-12345"
    os.environ.pop("ANTHROPIC_API_KEY", None)
    yield
    os.environ.clear()
    os.environ.update(env_backup)


@pytest.fixture
def env_with_anthropic_key():
    """Provide environment with only Anthropic key."""
    env_backup = os.environ.copy()
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key-12345"
    yield
    os.environ.clear()
    os.environ.update(env_backup)


@pytest.fixture
def env_with_both_keys():
    """Provide environment with both API keys."""
    env_backup = os.environ.copy()
    os.environ["OPENAI_API_KEY"] = "test-openai-key-12345"
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key-12345"
    yield
    os.environ.clear()
    os.environ.update(env_backup)


# =============================================================================
# Document Fixtures
# =============================================================================

@pytest.fixture
def sample_documents() -> Dict[str, str]:
    """Provide sample documents for testing."""
    return {
        "Dana ROP": """=== RIG: DANA – BOP INSTALLATION ROP ===

1. PRE-JOB PREPARATIONS
1.1 Ensure all personnel are briefed on the procedure
1.2 Verify equipment is in good working condition
1.3 Check weather conditions

2. BOP HANDLING
2.1 Connect lifting equipment to BOP
2.2 Lift BOP from deck
2.3 Position over wellhead

3. BOP INSTALLATION
3.1 Lower BOP onto wellhead
3.2 Engage locking mechanism
3.3 Verify proper seating
""",
        "Dana JSA": """=== RIG: DANA – BOP INSTALLATION JSA ===

JOB SAFETY ANALYSIS

Step 1: Pre-job meeting
- Hazard: Miscommunication
- Control: Conduct toolbox talk

Step 2: BOP lifting
- Hazard: Dropped load
- Control: Use certified rigging, exclusion zone

Step 3: BOP positioning
- Hazard: Pinch points
- Control: Keep hands clear, use tag lines
""",
        "AlReem ROP": """=== RIG: ALREEM – BOP INSTALLATION ROP ===

1. PREPARATION PHASE
1.1 Brief all personnel
1.2 Inspect equipment
1.3 Monitor weather

2. LIFTING OPERATIONS
2.1 Attach lifting gear
2.2 Lift BOP
2.3 Position carefully

3. INSTALLATION
3.1 Lower onto wellhead
3.2 Lock in place
3.3 Verify installation
""",
    }


@pytest.fixture
def sample_previous_outputs() -> Dict[str, Any]:
    """Provide sample previous agent outputs for testing."""
    return {
        "agent1": """# Agent 1 – Comparison Analysis

## Document Inventory
- Dana ROP v1.0
- Dana JSA v1.0
- AlReem ROP v1.0

## Structure Mapping
Both procedures follow similar structure:
1. Preparation
2. Lifting
3. Installation

## Key Findings
- Dana has more detailed pre-job checklist
- AlReem has streamlined lifting procedure
""",
        "agent2": """# Agent 2 – Gap Analysis

## Missing Steps
- Weather monitoring frequency not specified
- Communication protocol gaps

## Safety Gaps
- Emergency stop procedure not detailed
- Exclusion zone dimensions not specified
""",
        "agent3": """# Agent 3 – HP Evaluation

## Human Performance Assessment
- Good use of checklists
- Clear step-by-step instructions

## Recommendations
- Add verification steps
- Implement peer checking
""",
        "agent4": """# Agent 4 – Equipment Validation

## Equipment Inventory
- Dana: Cameron BOP 18-3/4" 15K
- AlReem: Shaffer BOP 18-3/4" 10K

## Standardization Feasibility
Partial standardization possible with equipment-specific annexes.
""",
    }


# =============================================================================
# File System Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Provide a temporary directory that is cleaned up after tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_source_dir(temp_dir):
    """Create a temporary source directory with rig folders and documents."""
    source_dir = temp_dir / "source_documents"
    source_dir.mkdir()

    # Create rig directories with sample files
    for rig_name in ["Dana", "AlReem", "Marawwah"]:
        rig_dir = source_dir / rig_name
        rig_dir.mkdir()

        # Create a simple text file (we'll mock PDF/DOCX extraction)
        (rig_dir / f"{rig_name}_ROP.txt").write_text(f"ROP content for {rig_name}")

    yield source_dir


@pytest.fixture
def temp_source_dir_with_pdfs(temp_dir):
    """Create a temporary source directory with mock PDF files."""
    source_dir = temp_dir / "source_documents"
    source_dir.mkdir()

    for rig_name in ["Dana", "AlReem"]:
        rig_dir = source_dir / rig_name
        rig_dir.mkdir()
        # Create empty files with PDF extension
        (rig_dir / f"{rig_name}_ROP.pdf").write_bytes(b"")
        (rig_dir / f"{rig_name}_JSA.docx").write_bytes(b"")

    yield source_dir


# =============================================================================
# Mock API Response Fixtures
# =============================================================================

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a mock OpenAI response for testing."
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_response.usage.total_tokens = 150
    return mock_response


@pytest.fixture
def mock_anthropic_response():
    """Create a mock Anthropic API response."""
    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.type = "text"
    mock_content.text = "This is a mock Anthropic response for testing."
    mock_response.content = [mock_content]
    mock_response.usage = MagicMock()
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    return mock_response


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Create a mock OpenAI client."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_openai_response
    return mock_client


@pytest.fixture
def mock_anthropic_client(mock_anthropic_response):
    """Create a mock Anthropic client."""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_anthropic_response
    return mock_client


# =============================================================================
# Agent Result Fixtures
# =============================================================================

@pytest.fixture
def sample_agent_result():
    """Create a sample AgentResult for testing."""
    from src.agents.base import AgentResult
    return AgentResult(
        content="# Sample Agent Output\n\nThis is test content.",
        meta={
            "agent": "Test Agent",
            "backend": "openai",
            "total_duration_seconds": 1.5,
            "model": "gpt-4o",
            "tokens_prompt": 100,
            "tokens_completion": 50,
            "tokens_total": 150,
        }
    )


# =============================================================================
# Prompt File Fixtures
# =============================================================================

@pytest.fixture
def temp_prompt_file(temp_dir):
    """Create a temporary prompt file for testing."""
    prompt_path = temp_dir / "test_prompt.md"
    prompt_path.write_text("""# Test Agent Prompt

You are a test agent for unit testing purposes.

Your tasks:
1. Process input documents
2. Generate structured output
3. Follow test protocols
""", encoding="utf-8")
    return prompt_path
