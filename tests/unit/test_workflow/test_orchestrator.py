"""Unit tests for src/workflow/orchestrator.py module."""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import time

from src.workflow.orchestrator import WorkflowConfig, ADNOCWorkflow
from src.agents.base import AgentResult


class TestWorkflowConfig:
    """Tests for the WorkflowConfig dataclass."""

    def test_workflow_config_default_values(self):
        """WorkflowConfig should have correct default values."""
        config = WorkflowConfig()

        assert config.backend == "openai"
        assert config.output_base_dir == "outputs"

    def test_workflow_config_custom_backend(self):
        """WorkflowConfig should accept custom backend."""
        config = WorkflowConfig(backend="anthropic")

        assert config.backend == "anthropic"

    def test_workflow_config_custom_output_dir(self):
        """WorkflowConfig should accept custom output directory."""
        config = WorkflowConfig(output_base_dir="/custom/output/path")

        assert config.output_base_dir == "/custom/output/path"

    def test_workflow_config_all_custom_values(self):
        """WorkflowConfig should accept all custom values."""
        config = WorkflowConfig(
            backend="anthropic",
            output_base_dir="/my/outputs"
        )

        assert config.backend == "anthropic"
        assert config.output_base_dir == "/my/outputs"

    def test_workflow_config_mode_default(self):
        """WorkflowConfig should default to sequential mode."""
        config = WorkflowConfig()

        assert config.mode == "sequential"

    def test_workflow_config_integrated_mode(self):
        """WorkflowConfig should accept integrated mode."""
        config = WorkflowConfig(mode="integrated")

        assert config.mode == "integrated"

    def test_workflow_config_integrated_mode_with_context(self):
        """WorkflowConfig should accept all integrated mode context fields."""
        config = WorkflowConfig(
            mode="integrated",
            rig_name="Dana",
            operation_type="BOP Installation",
            adnoc_cps=["HSE-PSW-CP01", "HSE-PSW-CP04"],
            constraints="Limited crane capacity"
        )

        assert config.mode == "integrated"
        assert config.rig_name == "Dana"
        assert config.operation_type == "BOP Installation"
        assert len(config.adnoc_cps) == 2
        assert config.constraints == "Limited crane capacity"


class TestADNOCWorkflowInitialization:
    """Tests for ADNOCWorkflow initialization."""

    def test_workflow_initialization(self):
        """ADNOCWorkflow should initialize with config."""
        config = WorkflowConfig()

        with patch("src.workflow.orchestrator.ComparisonAgent"), \
             patch("src.workflow.orchestrator.GapDetectorAgent"), \
             patch("src.workflow.orchestrator.HPEvaluatorAgent"), \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent"), \
             patch("src.workflow.orchestrator.StandardisationWriterAgent"), \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent"):
            workflow = ADNOCWorkflow(config)

        assert workflow.config == config

    def test_workflow_creates_all_agents(self):
        """ADNOCWorkflow should create all 5 sequential agents plus integrated agent."""
        config = WorkflowConfig()

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5, \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent") as mock_integrated:
            workflow = ADNOCWorkflow(config)

        mock_agent1.assert_called_once()
        mock_agent2.assert_called_once()
        mock_agent3.assert_called_once()
        mock_agent4.assert_called_once()
        mock_agent5.assert_called_once()
        mock_integrated.assert_called_once()

    def test_workflow_creates_integrated_agent(self):
        """ADNOCWorkflow should create the integrated compliance agent."""
        config = WorkflowConfig()

        with patch("src.workflow.orchestrator.ComparisonAgent"), \
             patch("src.workflow.orchestrator.GapDetectorAgent"), \
             patch("src.workflow.orchestrator.HPEvaluatorAgent"), \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent"), \
             patch("src.workflow.orchestrator.StandardisationWriterAgent"), \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent") as mock_integrated:
            workflow = ADNOCWorkflow(config)

        assert workflow.integrated_agent is not None
        mock_integrated.assert_called_once()


class TestADNOCWorkflowRunCompleteWorkflow:
    """Tests for ADNOCWorkflow.run_complete_workflow method."""

    @pytest.fixture
    def mock_agent_result(self):
        """Create a mock agent result."""
        return AgentResult(
            content="# Mock Agent Output\n\nThis is test content.",
            meta={
                "agent": "Mock Agent",
                "backend": "openai",
                "total_duration_seconds": 1.0,
                "model": "gpt-4o",
                "tokens_prompt": 100,
                "tokens_completion": 50,
                "tokens_total": 150,
            }
        )

    @pytest.fixture
    def mock_workflow(self, mock_agent_result):
        """Create a workflow with mocked agents."""
        config = WorkflowConfig()

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5:

            # Configure all agent mocks to return the mock result
            for mock_agent in [mock_agent1, mock_agent2, mock_agent3, mock_agent4, mock_agent5]:
                instance = mock_agent.return_value
                instance.run.return_value = mock_agent_result

            workflow = ADNOCWorkflow(config)

            # Re-assign the mocked instances
            workflow.agent1 = mock_agent1.return_value
            workflow.agent2 = mock_agent2.return_value
            workflow.agent3 = mock_agent3.return_value
            workflow.agent4 = mock_agent4.return_value
            workflow.agent5 = mock_agent5.return_value

        return workflow

    def test_run_complete_workflow_creates_output_directory(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should create timestamped output directory."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):  # Suppress print output
            output_dir = mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        assert output_dir.exists()
        assert output_dir.is_dir()
        assert "BOP Installation" in str(output_dir)

    def test_run_complete_workflow_runs_all_agents(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should run all 5 agents."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        mock_workflow.agent1.run.assert_called_once()
        mock_workflow.agent2.run.assert_called_once()
        mock_workflow.agent3.run.assert_called_once()
        mock_workflow.agent4.run.assert_called_once()
        mock_workflow.agent5.run.assert_called_once()

    def test_run_complete_workflow_passes_backend_to_agents(self, temp_dir, sample_documents, mock_agent_result):
        """run_complete_workflow should pass correct backend to all agents."""
        config = WorkflowConfig(backend="anthropic", output_base_dir=str(temp_dir))

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5:

            for mock_agent in [mock_agent1, mock_agent2, mock_agent3, mock_agent4, mock_agent5]:
                mock_agent.return_value.run.return_value = mock_agent_result

            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                workflow.run_complete_workflow("Test", sample_documents)

            # Check that agents were called with anthropic backend
            for mock_agent in [mock_agent1, mock_agent2, mock_agent3, mock_agent4, mock_agent5]:
                call_kwargs = mock_agent.return_value.run.call_args[1]
                assert call_kwargs["backend"] == "anthropic"

    def test_run_complete_workflow_creates_markdown_files(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should create markdown files for each agent."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        expected_files = [
            "agent1_comparison.md",
            "agent2_gaps.md",
            "agent3_hp_evaluation.md",
            "agent4_equipment_validation.md",
            "agent5_standardisation.md",
        ]

        for filename in expected_files:
            filepath = output_dir / filename
            assert filepath.exists(), f"Expected file {filename} not found"

    def test_run_complete_workflow_creates_metadata_files(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should create JSON metadata files for each agent."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        expected_files = [
            "agent1_comparison.meta.json",
            "agent2_gaps.meta.json",
            "agent3_hp_evaluation.meta.json",
            "agent4_equipment_validation.meta.json",
            "agent5_standardisation.meta.json",
        ]

        for filename in expected_files:
            filepath = output_dir / filename
            assert filepath.exists(), f"Expected file {filename} not found"

            # Verify it's valid JSON
            content = filepath.read_text()
            data = json.loads(content)
            assert "agent" in data

    def test_run_complete_workflow_creates_summary(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should create summary.json file."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        summary_file = output_dir / "summary.json"
        assert summary_file.exists()

        content = summary_file.read_text()
        summary = json.loads(content)

        assert summary["operation"] == "BOP Installation"
        assert summary["backend"] == "openai"
        assert "timestamp" in summary
        assert "agents" in summary
        assert len(summary["agents"]) == 5
        assert "total_tokens" in summary
        assert "total_duration_seconds" in summary

    def test_run_complete_workflow_aggregates_tokens(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should aggregate total tokens correctly."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        summary_file = output_dir / "summary.json"
        summary = json.loads(summary_file.read_text())

        # Each agent returns 150 tokens, 5 agents = 750 total
        assert summary["total_tokens"] == 750

    def test_run_complete_workflow_returns_output_path(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should return the output directory path."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            result = mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        assert isinstance(result, Path)
        assert result.exists()

    def test_run_complete_workflow_passes_previous_outputs(self, temp_dir, sample_documents):
        """run_complete_workflow should pass previous agent outputs to subsequent agents."""
        config = WorkflowConfig(output_base_dir=str(temp_dir))

        # Create agent results with unique content
        results = {}
        for i in range(1, 6):
            results[f"agent{i}"] = AgentResult(
                content=f"Agent {i} unique output",
                meta={"agent": f"Agent {i}", "backend": "openai", "total_duration_seconds": 1.0, "tokens_total": 100}
            )

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5:

            mock_agent1.return_value.run.return_value = results["agent1"]
            mock_agent2.return_value.run.return_value = results["agent2"]
            mock_agent3.return_value.run.return_value = results["agent3"]
            mock_agent4.return_value.run.return_value = results["agent4"]
            mock_agent5.return_value.run.return_value = results["agent5"]

            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                workflow.run_complete_workflow("Test", sample_documents)

            # Check Agent 2 receives Agent 1 output
            agent2_call = mock_agent2.return_value.run.call_args
            assert "agent1" in agent2_call[0][1]  # previous_outputs dict

            # Check Agent 5 receives all previous outputs
            agent5_call = mock_agent5.return_value.run.call_args
            previous = agent5_call[0][1]
            assert "agent1" in previous
            assert "agent2" in previous
            assert "agent3" in previous
            assert "agent4" in previous

    def test_run_complete_workflow_with_empty_documents(self, mock_workflow, temp_dir):
        """run_complete_workflow should handle empty documents dictionary."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_workflow.run_complete_workflow("Empty Test", {})

        assert output_dir.exists()

    def test_run_complete_workflow_output_directory_structure(self, mock_workflow, temp_dir, sample_documents):
        """run_complete_workflow should create correct directory structure."""
        mock_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_workflow.run_complete_workflow("BOP Installation", sample_documents)

        # Should be: temp_dir / "BOP Installation" / timestamp
        assert output_dir.parent.name == "BOP Installation"
        assert output_dir.parent.parent == temp_dir


class TestADNOCWorkflowEdgeCases:
    """Edge case tests for ADNOCWorkflow."""

    def test_workflow_with_special_characters_in_operation_name(self, temp_dir, sample_documents):
        """Workflow should handle special characters in operation name."""
        config = WorkflowConfig(output_base_dir=str(temp_dir))

        mock_result = AgentResult(
            content="Test",
            meta={"agent": "Test", "backend": "openai", "total_duration_seconds": 1.0, "tokens_total": 100}
        )

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5:

            for mock_agent in [mock_agent1, mock_agent2, mock_agent3, mock_agent4, mock_agent5]:
                mock_agent.return_value.run.return_value = mock_result

            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                # Note: Filesystem-safe operation name
                output_dir = workflow.run_complete_workflow("BOP-Installation_v2", sample_documents)

        assert output_dir.exists()

    def test_workflow_markdown_content_preserved(self, temp_dir, sample_documents):
        """Workflow should preserve markdown formatting in output files."""
        config = WorkflowConfig(output_base_dir=str(temp_dir))

        markdown_content = """# Analysis Results

## Section 1
- Item 1
- Item 2

## Section 2
```python
code_example()
```
"""

        mock_result = AgentResult(
            content=markdown_content,
            meta={"agent": "Test", "backend": "openai", "total_duration_seconds": 1.0, "tokens_total": 100}
        )

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5:

            for mock_agent in [mock_agent1, mock_agent2, mock_agent3, mock_agent4, mock_agent5]:
                mock_agent.return_value.run.return_value = mock_result

            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                output_dir = workflow.run_complete_workflow("Test", sample_documents)

        # Read the first agent's markdown file
        md_file = output_dir / "agent1_comparison.md"
        content = md_file.read_text(encoding="utf-8")

        assert "# Analysis Results" in content
        assert "## Section 1" in content
        assert "```python" in content


class TestADNOCWorkflowIntegratedMode:
    """Tests for ADNOCWorkflow integrated mode functionality."""

    @pytest.fixture
    def mock_integrated_result(self):
        """Create a mock integrated agent result."""
        return AgentResult(
            content="""# Integrated ROP Package

## Part 1: Rig Operating Procedure
### 1. General Information
Document number: ROP-001

## Part 2: Gap Analysis Report
No critical gaps identified.

## Part 3: Human Performance Assessment
All steps reviewed for HP risks.

## Part 4: Equipment Validation Matrix
| Equipment | Status |
|-----------|--------|
| Crane | Compliant |

## Part 5: Document Control
Revision: 1.0
""",
            meta={
                "agent": "Integrated Compliance Agent",
                "backend": "openai",
                "total_duration_seconds": 5.0,
                "model": "gpt-4o",
                "tokens_prompt": 500,
                "tokens_completion": 300,
                "tokens_total": 800,
            }
        )

    @pytest.fixture
    def mock_integrated_workflow(self, mock_integrated_result):
        """Create a workflow with mocked integrated agent."""
        config = WorkflowConfig(mode="integrated")

        with patch("src.workflow.orchestrator.ComparisonAgent"), \
             patch("src.workflow.orchestrator.GapDetectorAgent"), \
             patch("src.workflow.orchestrator.HPEvaluatorAgent"), \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent"), \
             patch("src.workflow.orchestrator.StandardisationWriterAgent"), \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent") as mock_integrated:

            mock_integrated.return_value.run.return_value = mock_integrated_result
            workflow = ADNOCWorkflow(config)
            workflow.integrated_agent = mock_integrated.return_value

        return workflow

    def test_run_integrated_workflow_creates_output_directory(
        self, mock_integrated_workflow, temp_dir, sample_documents
    ):
        """run_integrated_workflow should create timestamped output directory."""
        mock_integrated_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_integrated_workflow.run_integrated_workflow(
                "BOP Installation", sample_documents
            )

        assert output_dir.exists()
        assert output_dir.is_dir()
        assert "integrated" in str(output_dir)
        assert "BOP Installation" in str(output_dir)

    def test_run_integrated_workflow_calls_integrated_agent(
        self, mock_integrated_workflow, temp_dir, sample_documents
    ):
        """run_integrated_workflow should call the integrated agent."""
        mock_integrated_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            mock_integrated_workflow.run_integrated_workflow(
                "BOP Installation", sample_documents
            )

        mock_integrated_workflow.integrated_agent.run.assert_called_once()

    def test_run_integrated_workflow_passes_context(
        self, temp_dir, sample_documents, mock_integrated_result
    ):
        """run_integrated_workflow should pass context to the agent."""
        config = WorkflowConfig(
            mode="integrated",
            output_base_dir=str(temp_dir),
            rig_name="Dana",
            operation_type="BOP Installation",
            adnoc_cps=["HSE-PSW-CP01"],
            constraints="Limited crane capacity"
        )

        with patch("src.workflow.orchestrator.ComparisonAgent"), \
             patch("src.workflow.orchestrator.GapDetectorAgent"), \
             patch("src.workflow.orchestrator.HPEvaluatorAgent"), \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent"), \
             patch("src.workflow.orchestrator.StandardisationWriterAgent"), \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent") as mock_integrated:

            mock_integrated.return_value.run.return_value = mock_integrated_result
            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                workflow.run_integrated_workflow("BOP Installation", sample_documents)

            call_args = mock_integrated.return_value.run.call_args
            context = call_args[1]["context"]

            assert context["rig_name"] == "Dana"
            assert context["operation_type"] == "BOP Installation"
            assert "HSE-PSW-CP01" in context["adnoc_cps"]
            assert context["constraints"] == "Limited crane capacity"

    def test_run_integrated_workflow_creates_rop_package_file(
        self, mock_integrated_workflow, temp_dir, sample_documents
    ):
        """run_integrated_workflow should create the ROP package markdown file."""
        mock_integrated_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_integrated_workflow.run_integrated_workflow(
                "BOP Installation", sample_documents
            )

        rop_file = output_dir / "integrated_rop_package.md"
        assert rop_file.exists()
        content = rop_file.read_text()
        assert "Integrated ROP Package" in content

    def test_run_integrated_workflow_creates_metadata_file(
        self, mock_integrated_workflow, temp_dir, sample_documents
    ):
        """run_integrated_workflow should create JSON metadata file."""
        mock_integrated_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_integrated_workflow.run_integrated_workflow(
                "BOP Installation", sample_documents
            )

        meta_file = output_dir / "integrated_rop_package.meta.json"
        assert meta_file.exists()

        content = meta_file.read_text()
        data = json.loads(content)
        assert "agent" in data
        assert data["agent"] == "Integrated Compliance Agent"

    def test_run_integrated_workflow_creates_summary(
        self, mock_integrated_workflow, temp_dir, sample_documents
    ):
        """run_integrated_workflow should create summary.json file."""
        mock_integrated_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            output_dir = mock_integrated_workflow.run_integrated_workflow(
                "BOP Installation", sample_documents
            )

        summary_file = output_dir / "summary.json"
        assert summary_file.exists()

        content = summary_file.read_text()
        summary = json.loads(content)

        assert summary["operation"] == "BOP Installation"
        assert summary["mode"] == "integrated"
        assert "total_tokens" in summary
        assert "total_duration_seconds" in summary

    def test_run_integrated_workflow_returns_output_path(
        self, mock_integrated_workflow, temp_dir, sample_documents
    ):
        """run_integrated_workflow should return the output directory path."""
        mock_integrated_workflow.config.output_base_dir = str(temp_dir)

        with patch("builtins.print"):
            result = mock_integrated_workflow.run_integrated_workflow(
                "BOP Installation", sample_documents
            )

        assert isinstance(result, Path)
        assert result.exists()

    def test_run_integrated_workflow_with_anthropic_backend(
        self, temp_dir, sample_documents, mock_integrated_result
    ):
        """run_integrated_workflow should work with Anthropic backend."""
        config = WorkflowConfig(
            mode="integrated",
            backend="anthropic",
            output_base_dir=str(temp_dir)
        )

        with patch("src.workflow.orchestrator.ComparisonAgent"), \
             patch("src.workflow.orchestrator.GapDetectorAgent"), \
             patch("src.workflow.orchestrator.HPEvaluatorAgent"), \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent"), \
             patch("src.workflow.orchestrator.StandardisationWriterAgent"), \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent") as mock_integrated:

            mock_integrated.return_value.run.return_value = mock_integrated_result
            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                workflow.run_integrated_workflow("Test", sample_documents)

            call_kwargs = mock_integrated.return_value.run.call_args[1]
            assert call_kwargs["backend"] == "anthropic"


class TestADNOCWorkflowRunMethod:
    """Tests for ADNOCWorkflow.run convenience method."""

    @pytest.fixture
    def mock_result(self):
        """Create a mock agent result."""
        return AgentResult(
            content="# Test Output",
            meta={
                "agent": "Test",
                "backend": "openai",
                "total_duration_seconds": 1.0,
                "tokens_total": 100,
            }
        )

    def test_run_dispatches_to_sequential_by_default(
        self, temp_dir, sample_documents, mock_result
    ):
        """run() should dispatch to sequential workflow by default."""
        config = WorkflowConfig(output_base_dir=str(temp_dir))

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5, \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent") as mock_integrated:

            for mock_agent in [mock_agent1, mock_agent2, mock_agent3, mock_agent4, mock_agent5]:
                mock_agent.return_value.run.return_value = mock_result

            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                output_dir = workflow.run("Test", sample_documents)

            # Should have called sequential agents
            mock_agent1.return_value.run.assert_called_once()
            mock_agent5.return_value.run.assert_called_once()
            # Should NOT have called integrated agent
            mock_integrated.return_value.run.assert_not_called()

    def test_run_dispatches_to_integrated_when_configured(
        self, temp_dir, sample_documents, mock_result
    ):
        """run() should dispatch to integrated workflow when mode is integrated."""
        config = WorkflowConfig(mode="integrated", output_base_dir=str(temp_dir))

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent"), \
             patch("src.workflow.orchestrator.HPEvaluatorAgent"), \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent"), \
             patch("src.workflow.orchestrator.StandardisationWriterAgent"), \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent") as mock_integrated:

            mock_integrated.return_value.run.return_value = mock_result

            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                output_dir = workflow.run("Test", sample_documents)

            # Should have called integrated agent
            mock_integrated.return_value.run.assert_called_once()
            # Should NOT have called sequential agents
            mock_agent1.return_value.run.assert_not_called()

    def test_run_returns_output_path(self, temp_dir, sample_documents, mock_result):
        """run() should return the output directory path."""
        config = WorkflowConfig(output_base_dir=str(temp_dir))

        with patch("src.workflow.orchestrator.ComparisonAgent") as mock_agent1, \
             patch("src.workflow.orchestrator.GapDetectorAgent") as mock_agent2, \
             patch("src.workflow.orchestrator.HPEvaluatorAgent") as mock_agent3, \
             patch("src.workflow.orchestrator.EquipmentValidatorAgent") as mock_agent4, \
             patch("src.workflow.orchestrator.StandardisationWriterAgent") as mock_agent5, \
             patch("src.workflow.orchestrator.IntegratedComplianceAgent"):

            for mock_agent in [mock_agent1, mock_agent2, mock_agent3, mock_agent4, mock_agent5]:
                mock_agent.return_value.run.return_value = mock_result

            workflow = ADNOCWorkflow(config)

            with patch("builtins.print"):
                result = workflow.run("Test", sample_documents)

            assert isinstance(result, Path)
            assert result.exists()
