"""Rig discovery utilities."""

import os
from pathlib import Path
from typing import List


def list_rigs(source_dir: str | os.PathLike) -> List[str]:
    """List all rig directories containing BOP documents.
    
    Args:
        source_dir: Root directory containing rig subdirectories.
        
    Returns:
        Sorted list of rig names (directory names) that contain PDF or DOCX files.
        
    Example:
        >>> rigs = list_rigs("data/source_documents")
        >>> print(rigs)
        ['AlJubail', 'AlReem', 'Dana', 'Marawwah']
    """
    root = Path(source_dir)
    rigs: List[str] = []
    
    if not root.exists():
        return rigs

    for entry in root.iterdir():
        # Skip non-directories and hidden folders
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        
        # Check if directory contains BOP documents
        has_docs = any(
            f.suffix.lower() in {".pdf", ".docx", ".doc"}
            for f in entry.rglob("*")
            if f.is_file()
        )
        
        if has_docs:
            rigs.append(entry.name)

    return sorted(rigs)
