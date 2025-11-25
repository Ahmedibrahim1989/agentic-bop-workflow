#!/usr/bin/env python
"""Run the complete BOP standardization workflow using OpenAI."""

import argparse
import sys
from pathlib import Path
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflow.orchestrator import ADNOCWorkflow, WorkflowConfig


def load_documents(path: str) -> Dict[str, str]:
    """Load documents from a combined text file.
    
    Args:
        path: Path to the combined text file.
        
    Returns:
        Dictionary with document name mapped to content.
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Documents file not found: {path}")
    
    text = file_path.read_text(encoding="utf-8")
    
    # For now, treat entire file as one document
    # Could be enhanced to split by rig markers
    docs: Dict[str, str] = {
        "Combined BOP Documents": text
    }
    
    return docs


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run ADNOC BOP standardization workflow with OpenAI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --operation "BOP Installation" --documents-file production-data-bop-real.txt
  %(prog)s --operation "BOP Testing" --documents-file bop-testing-docs.txt
        """,
    )
    parser.add_argument(
        "--operation",
        required=True,
        help="Operation name (e.g., 'BOP Installation', 'BOP Testing').",
    )
    parser.add_argument(
        "--documents-file",
        required=True,
        help="Path to combined documents text file.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Base directory for outputs (default: outputs).",
    )
    args = parser.parse_args()

    # Load documents
    print(f"\nLoading documents from: {args.documents_file}")
    try:
        documents = load_documents(args.documents_file)
        total_chars = sum(len(text) for text in documents.values())
        print(f"✓ Loaded {len(documents)} document(s) ({total_chars:,} characters)\n")
    except Exception as e:
        print(f"\n✗ Error loading documents: {e}\n")
        sys.exit(1)

    # Create workflow
    config = WorkflowConfig(
        backend="openai",
        output_base_dir=args.output_dir,
    )
    workflow = ADNOCWorkflow(config)

    # Run workflow
    try:
        output_dir = workflow.run_complete_workflow(
            operation_name=args.operation,
            documents=documents,
        )
        print(f"\n✓ Workflow completed successfully!")
        print(f"\nResults available at: {output_dir}")
        print(f"\nNext steps:")
        print(f"  1. Review outputs: cd {output_dir}")
        print(f"  2. Check summary: cat {output_dir}/summary.json")
        print(f"  3. Read final output: cat {output_dir}/agent5_standardisation.md\n")
    except Exception as e:
        print(f"\n✗ Workflow failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
