#!/usr/bin/env python
"""Automated end-to-end BOP workflow execution.

This script automates the entire workflow:
1. List available rigs
2. Extract text from documents
3. Run multi-agent workflow
4. Generate reports
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.list_rigs import list_rigs
from src.ingestion.extract_text import build_combined_file
from src.workflow.orchestrator import ADNOCWorkflow, WorkflowConfig


def main() -> None:
    """Main entry point for automated workflow."""
    parser = argparse.ArgumentParser(
        description="Automated end-to-end BOP standardization workflow.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --operation "BOP Installation" --backend openai
  %(prog)s --operation "BOP Testing" --backend anthropic --source-dir data/source_documents
        """,
    )
    parser.add_argument(
        "--operation",
        required=True,
        help="Operation name (e.g., 'BOP Installation').",
    )
    parser.add_argument(
        "--backend",
        choices=["openai", "anthropic"],
        default="openai",
        help="LLM backend to use (default: openai).",
    )
    parser.add_argument(
        "--source-dir",
        default="data/source_documents",
        help="Source directory for rig documents (default: data/source_documents).",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Base directory for outputs (default: outputs).",
    )
    args = parser.parse_args()

    print("\n" + "="*80)
    print("AUTOMATED BOP STANDARDIZATION WORKFLOW")
    print("="*80 + "\n")

    # Step 1: Discover rigs
    print("Step 1: Discovering rigs...")
    rigs = list_rigs(args.source_dir)
    if not rigs:
        print(f"\n✗ No rigs found in {args.source_dir}")
        print("Please add rig documents and try again.\n")
        sys.exit(1)
    print(f"✓ Found {len(rigs)} rig(s): {', '.join(rigs)}\n")

    # Step 2: Extract text
    print("Step 2: Extracting text from documents...")
    temp_file = "temp-extracted-text.txt"
    try:
        build_combined_file(rigs, args.source_dir, temp_file)
        print(f"✓ Text extracted to {temp_file}\n")
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}\n")
        sys.exit(1)

    # Step 3: Load documents
    print("Step 3: Loading documents...")
    try:
        text = Path(temp_file).read_text(encoding="utf-8")
        documents = {"Combined BOP Documents": text}
        print(f"✓ Loaded {len(text):,} characters\n")
    except Exception as e:
        print(f"\n✗ Loading failed: {e}\n")
        sys.exit(1)

    # Step 4: Run workflow
    print(f"Step 4: Running multi-agent workflow ({args.backend})...\n")
    config = WorkflowConfig(
        backend=args.backend,
        output_base_dir=args.output_dir,
    )
    workflow = ADNOCWorkflow(config)

    try:
        output_dir = workflow.run_complete_workflow(
            operation_name=args.operation,
            documents=documents,
        )
        
        # Cleanup temp file
        Path(temp_file).unlink(missing_ok=True)
        
        print("\n" + "="*80)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\nResults: {output_dir}")
        print(f"\nReview outputs:")
        print(f"  - Agent 1 (Comparison): {output_dir}/agent1_comparison.md")
        print(f"  - Agent 2 (Gaps): {output_dir}/agent2_gaps.md")
        print(f"  - Agent 3 (HP): {output_dir}/agent3_hp_evaluation.md")
        print(f"  - Agent 4 (Equipment): {output_dir}/agent4_equipment_validation.md")
        print(f"  - Agent 5 (Final): {output_dir}/agent5_standardisation.md")
        print(f"  - Summary: {output_dir}/summary.json\n")
        
    except Exception as e:
        print(f"\n✗ Workflow failed: {e}\n")
        import traceback
        traceback.print_exc()
        
        # Cleanup temp file
        Path(temp_file).unlink(missing_ok=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
