#!/usr/bin/env python
"""List available rigs in the source documents directory."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.list_rigs import list_rigs


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="List all available rigs with BOP documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --source-dir data/source_documents
        """,
    )
    parser.add_argument(
        "--source-dir",
        default="data/source_documents",
        help="Root folder containing one subfolder per rig (default: data/source_documents).",
    )
    args = parser.parse_args()

    rigs = list_rigs(args.source_dir)
    
    if not rigs:
        print(f"\n⚠️  No rigs found under {args.source_dir}")
        print("\nPlease ensure:")
        print(f"  1. The directory {args.source_dir} exists")
        print("  2. It contains subdirectories named after rigs")
        print("  3. Each rig subdirectory contains PDF or DOCX files")
        print("\nExample structure:")
        print(f"  {args.source_dir}/")
        print("    ├─ Dana/")
        print("    │  ├─ BOP_Installation_ROP.pdf")
        print("    │  └─ BOP_Installation_JSA.pdf")
        print("    ├─ AlJubail/")
        print("    │  └─ ...")
        return

    print(f"\n✓ Found {len(rigs)} rig(s) with BOP documents:\n")
    for i, rig in enumerate(rigs, 1):
        print(f"  {i}. {rig}")
    
    print(f"\nSource directory: {args.source_dir}\n")


if __name__ == "__main__":
    main()
