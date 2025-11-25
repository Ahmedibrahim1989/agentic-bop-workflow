#!/usr/bin/env python
"""Convert BOP PDFs and DOCX files to a combined text file."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.list_rigs import list_rigs
from src.ingestion.extract_text import build_combined_file


def print_manual_instructions(rigs, source_dir, output_file):
    """Print instructions for manual text extraction."""
    print("\n" + "="*80)
    print("MANUAL TEXT EXTRACTION MODE")
    print("="*80)
    print("\nFor highest accuracy, manually copy/paste text from documents.\n")
    print(f"Rigs detected: {', '.join(rigs)}\n")
    print("Steps:")
    print(f"  1. Create the file: {output_file}")
    print("  2. For each rig and document, add a header and paste the text:")
    print("\n     === RIG: DANA – BOP INSTALLATION ROP ===")
    print("     ")
    print("     [paste full text here]")
    print("     ")
    print("     === RIG: DANA – BOP INSTALLATION JSA ===")
    print("     ")
    print("     [paste full text here]")
    print("\n  3. Repeat for all rigs and documents.")
    print("  4. Save the file.\n")
    print(f"Reference format: data/sample/test-data-bop-installation.txt\n")
    print("="*80 + "\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert BOP PDFs/DOCX into a combined text file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Manual mode (recommended):
  %(prog)s
  
  # Automatic extraction:
  %(prog)s --auto --source-dir data/source_documents --output-file production-data-bop-real.txt
        """,
    )
    parser.add_argument(
        "--source-dir",
        default="data/source_documents",
        help="Root folder containing rig subdirectories (default: data/source_documents).",
    )
    parser.add_argument(
        "--output-file",
        default="production-data-bop-real.txt",
        help="Path for combined text output (default: production-data-bop-real.txt).",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically extract text instead of manual copy/paste.",
    )
    args = parser.parse_args()

    # Discover rigs
    rigs = list_rigs(args.source_dir)
    
    if not rigs:
        print(f"\n⚠️  No rigs found under {args.source_dir}")
        print("Please run 'python scripts/list_available_rigs.py' first.\n")
        return

    # Manual mode
    if not args.auto:
        print_manual_instructions(rigs, args.source_dir, args.output_file)
        return

    # Auto mode
    print(f"\nAuto-extracting from {len(rigs)} rig(s): {', '.join(rigs)}")
    print(f"Source: {args.source_dir}")
    print(f"Output: {args.output_file}\n")
    
    try:
        build_combined_file(rigs, args.source_dir, args.output_file)
        print(f"✓ Successfully wrote combined text to {args.output_file}\n")
        print("⚠️  IMPORTANT: Manually verify the output file!")
        print("   PDF extraction may mis-handle tables and formatting.")
        print("   Review the file before running the workflow.\n")
    except Exception as e:
        print(f"\n✗ Error during extraction: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
