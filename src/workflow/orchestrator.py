"""Multi-agent workflow orchestrator."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from src.agents.comparison_agent import ComparisonAgent
from src.agents.gap_detector_agent import GapDetectorAgent
from src.agents.hp_evaluator_agent import HPEvaluatorAgent
from src.agents.equipment_validator_agent import EquipmentValidatorAgent
from src.agents.standardisation_writer_agent import StandardisationWriterAgent
from src.agents.base import AgentResult


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution.
    
    Attributes:
        backend: LLM backend to use ("openai" or "anthropic").
        output_base_dir: Base directory for outputs (default: "outputs").
    """
    backend: str = "openai"
    output_base_dir: str = "outputs"


class ADNOCWorkflow:
    """Orchestrates the complete multi-agent BOP standardization workflow.
    
    This class manages the sequential execution of 5 agents:
    1. Comparison Analyst
    2. Gap Detector
    3. HP Evaluator
    4. Equipment Validator
    5. Standardisation Writer
    
    Each agent receives:
    - Original documents
    - Outputs from all previous agents
    
    Results are saved to timestamped output directories with:
    - Markdown files for each agent's output
    - JSON metadata files with timing and token usage
    - Summary report aggregating all metrics
    """

    def __init__(self, config: WorkflowConfig):
        """Initialize the workflow orchestrator.
        
        Args:
            config: Workflow configuration.
        """
        self.config = config
        
        # Initialize all agents
        self.agent1 = ComparisonAgent()
        self.agent2 = GapDetectorAgent()
        self.agent3 = HPEvaluatorAgent()
        self.agent4 = EquipmentValidatorAgent()
        self.agent5 = StandardisationWriterAgent()

    def run_complete_workflow(
        self,
        operation_name: str,
        documents: Dict[str, str],
    ) -> Path:
        """Run the complete multi-agent workflow.
        
        Args:
            operation_name: Name of the operation (e.g., "BOP Installation").
            documents: Dictionary mapping document names to their text content.
            
        Returns:
            Path to the output directory containing all results.
            
        Example:
            >>> workflow = ADNOCWorkflow(WorkflowConfig(backend="openai"))
            >>> docs = {"Combined BOP Text": "..."}
            >>> output_dir = workflow.run_complete_workflow("BOP Installation", docs)
            >>> print(f"Results saved to: {output_dir}")
        """
        # Create timestamped output directory
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        out_dir = Path(self.config.output_base_dir) / operation_name / timestamp
        out_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*80}")
        print(f"Starting ADNOC BOP Standardization Workflow")
        print(f"Operation: {operation_name}")
        print(f"Backend: {self.config.backend}")
        print(f"Output: {out_dir}")
        print(f"{'='*80}\n")
        
        # Initialize summary and previous outputs
        summary: Dict[str, Any] = {
            "operation": operation_name,
            "timestamp": timestamp,
            "backend": self.config.backend,
            "agents": [],
            "total_tokens": 0,
            "total_duration_seconds": 0,
        }
        
        previous: Dict[str, Any] = {}

        def save_result(name: str, result: AgentResult) -> None:
            """Save agent result to files and update summary."""
            # Save Markdown content
            md_path = out_dir / f"{name}.md"
            md_path.write_text(result.content, encoding="utf-8")
            
            # Save metadata as JSON
            meta_path = out_dir / f"{name}.meta.json"
            meta_path.write_text(
                json.dumps(result.meta, indent=2),
                encoding="utf-8",
            )
            
            # Update summary
            summary["agents"].append({**result.meta, "name": name})
            summary["total_tokens"] += result.meta.get("tokens_total", 0)
            summary["total_duration_seconds"] += result.meta.get("total_duration_seconds", 0)
            
            print(f"✓ {name} completed")
            print(f"  Duration: {result.meta.get('total_duration_seconds', 0):.2f}s")
            print(f"  Tokens: {result.meta.get('tokens_total', 0)}")
            print()

        # ============================================================
        # Agent 1: Comparison Analyst
        # ============================================================
        print("Running Agent 1: Comparison Analyst...")
        r1 = self.agent1.run(
            documents,
            previous,
            backend=self.config.backend,
            operation_name=operation_name,
        )
        save_result("agent1_comparison", r1)
        previous["agent1"] = r1.content

        # ============================================================
        # Agent 2: Gap Detector
        # ============================================================
        print("Running Agent 2: Gap Detector...")
        r2 = self.agent2.run(
            documents,
            previous,
            backend=self.config.backend,
            operation_name=operation_name,
        )
        save_result("agent2_gaps", r2)
        previous["agent2"] = r2.content

        # ============================================================
        # Agent 3: HP Evaluator
        # ============================================================
        print("Running Agent 3: Human Performance Evaluator...")
        r3 = self.agent3.run(
            documents,
            previous,
            backend=self.config.backend,
            operation_name=operation_name,
        )
        save_result("agent3_hp_evaluation", r3)
        previous["agent3"] = r3.content

        # ============================================================
        # Agent 4: Equipment Validator
        # ============================================================
        print("Running Agent 4: Equipment Validator...")
        r4 = self.agent4.run(
            documents,
            previous,
            backend=self.config.backend,
            operation_name=operation_name,
        )
        save_result("agent4_equipment_validation", r4)
        previous["agent4"] = r4.content

        # ============================================================
        # Agent 5: Standardisation Writer
        # ============================================================
        print("Running Agent 5: Standardisation Writer...")
        r5 = self.agent5.run(
            documents,
            previous,
            backend=self.config.backend,
            operation_name=operation_name,
        )
        save_result("agent5_standardisation", r5)
        previous["agent5"] = r5.content

        # ============================================================
        # Save summary
        # ============================================================
        summary_path = out_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, indent=2),
            encoding="utf-8",
        )
        
        print(f"{'='*80}")
        print(f"Workflow completed successfully!")
        print(f"Total tokens used: {summary['total_tokens']:,}")
        print(f"Total duration: {summary['total_duration_seconds']:.2f}s")
        print(f"Results saved to: {out_dir}")
        print(f"{'='*80}\n")

        return out_dir
