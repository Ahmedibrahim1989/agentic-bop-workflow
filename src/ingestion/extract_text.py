"""Text extraction from PDF and DOCX files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from PyPDF2 import PdfReader
import docx  # type: ignore


def extract_text_from_pdf(path: Path) -> str:
    """Extract text content from a PDF file.
    
    Args:
        path: Path to the PDF file.
        
    Returns:
        Extracted text content.
        
    Note:
        PDF extraction may not preserve formatting perfectly,
        especially for complex tables and multi-column layouts.
        Manual verification is recommended for production use.
    """
    reader = PdfReader(str(path))
    parts: list[str] = []
    
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    
    return "\n".join(parts)


def extract_text_from_docx(path: Path) -> str:
    """Extract text content from a DOCX file.
    
    Args:
        path: Path to the DOCX file.
        
    Returns:
        Extracted text content.
    """
    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)


def build_combined_file(
    rigs: Iterable[str],
    source_dir: str | os.PathLike,
    output_file: str | os.PathLike,
) -> None:
    """Build a combined text file from all rig documents.
    
    Args:
        rigs: List of rig names to process.
        source_dir: Root directory containing rig subdirectories.
        output_file: Path for the combined output file.
        
    The output file follows this format:
        === RIG: DANA – BOP INSTALLATION ROP ===
        
        [document text]
        
        === RIG: DANA – BOP INSTALLATION JSA ===
        
        [document text]
        
    Note:
        This function will overwrite the output file if it exists.
    """
    root = Path(source_dir)
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as out:
        for rig in rigs:
            rig_dir = root / rig
            if not rig_dir.exists():
                continue

            for doc_path in sorted(rig_dir.rglob("*")):
                if not doc_path.is_file():
                    continue
                    
                suffix = doc_path.suffix.lower()
                if suffix not in {".pdf", ".docx"}:
                    continue

                # Create header for this document
                header = f"=== RIG: {rig} – {doc_path.stem} ==="
                out.write(header + "\n\n")

                # Extract and write text
                try:
                    if suffix == ".pdf":
                        text = extract_text_from_pdf(doc_path)
                    else:
                        text = extract_text_from_docx(doc_path)
                    
                    out.write(text.strip() + "\n\n")
                except Exception as e:
                    out.write(f"[ERROR: Could not extract text from {doc_path}: {e}]\n\n")
