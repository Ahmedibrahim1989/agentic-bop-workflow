"""Unit tests for src/ingestion/extract_text.py module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from src.ingestion.extract_text import (
    extract_text_from_pdf,
    extract_text_from_docx,
    build_combined_file,
)


class TestExtractTextFromPdf:
    """Tests for extract_text_from_pdf function."""

    def test_extract_text_from_single_page_pdf(self):
        """Should extract text from a single-page PDF."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is page 1 content."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        with patch("src.ingestion.extract_text.PdfReader", return_value=mock_reader):
            result = extract_text_from_pdf(Path("/fake/document.pdf"))

        assert result == "This is page 1 content."

    def test_extract_text_from_multi_page_pdf(self):
        """Should extract and join text from multiple pages."""
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content."
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content."
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "Page 3 content."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]

        with patch("src.ingestion.extract_text.PdfReader", return_value=mock_reader):
            result = extract_text_from_pdf(Path("/fake/document.pdf"))

        assert "Page 1 content." in result
        assert "Page 2 content." in result
        assert "Page 3 content." in result
        assert result == "Page 1 content.\nPage 2 content.\nPage 3 content."

    def test_extract_text_handles_empty_page(self):
        """Should handle pages that return empty text."""
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = None  # Empty page

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]

        with patch("src.ingestion.extract_text.PdfReader", return_value=mock_reader):
            result = extract_text_from_pdf(Path("/fake/document.pdf"))

        assert "Content" in result

    def test_extract_text_from_empty_pdf(self):
        """Should return empty string for PDF with no pages."""
        mock_reader = MagicMock()
        mock_reader.pages = []

        with patch("src.ingestion.extract_text.PdfReader", return_value=mock_reader):
            result = extract_text_from_pdf(Path("/fake/empty.pdf"))

        assert result == ""


class TestExtractTextFromDocx:
    """Tests for extract_text_from_docx function."""

    def test_extract_text_from_docx(self):
        """Should extract text from DOCX paragraphs."""
        mock_para1 = MagicMock()
        mock_para1.text = "First paragraph."
        mock_para2 = MagicMock()
        mock_para2.text = "Second paragraph."

        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para1, mock_para2]

        with patch("src.ingestion.extract_text.docx.Document", return_value=mock_doc):
            result = extract_text_from_docx(Path("/fake/document.docx"))

        assert result == "First paragraph.\nSecond paragraph."

    def test_extract_text_from_docx_with_empty_paragraphs(self):
        """Should handle empty paragraphs in DOCX."""
        mock_para1 = MagicMock()
        mock_para1.text = "Content"
        mock_para2 = MagicMock()
        mock_para2.text = ""  # Empty paragraph

        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para1, mock_para2]

        with patch("src.ingestion.extract_text.docx.Document", return_value=mock_doc):
            result = extract_text_from_docx(Path("/fake/document.docx"))

        assert "Content" in result

    def test_extract_text_from_empty_docx(self):
        """Should return empty string for DOCX with no paragraphs."""
        mock_doc = MagicMock()
        mock_doc.paragraphs = []

        with patch("src.ingestion.extract_text.docx.Document", return_value=mock_doc):
            result = extract_text_from_docx(Path("/fake/empty.docx"))

        assert result == ""


class TestBuildCombinedFile:
    """Tests for build_combined_file function."""

    def test_build_combined_file_creates_output(self, temp_dir):
        """Should create output file with combined content."""
        # Set up source directory
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "TestRig"
        rig_dir.mkdir()

        output_file = temp_dir / "output" / "combined.txt"

        # Mock PDF extraction
        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF content for TestRig"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            # Create a PDF file
            (rig_dir / "document.pdf").touch()

            build_combined_file(["TestRig"], source_dir, output_file)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "=== RIG: TestRig" in content

    def test_build_combined_file_header_format(self, temp_dir):
        """Should format headers correctly."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "Dana"
        rig_dir.mkdir()

        output_file = temp_dir / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Content"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            (rig_dir / "BOP_Installation_ROP.pdf").touch()

            build_combined_file(["Dana"], source_dir, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "=== RIG: Dana – BOP_Installation_ROP ===" in content

    def test_build_combined_file_multiple_rigs(self, temp_dir):
        """Should combine documents from multiple rigs."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        for rig_name in ["Rig1", "Rig2"]:
            rig_dir = source_dir / rig_name
            rig_dir.mkdir()
            (rig_dir / "document.pdf").touch()

        output_file = temp_dir / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Content"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            build_combined_file(["Rig1", "Rig2"], source_dir, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "=== RIG: Rig1" in content
        assert "=== RIG: Rig2" in content

    def test_build_combined_file_skips_nonexistent_rig(self, temp_dir):
        """Should skip rigs that don't exist."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "ExistingRig"
        rig_dir.mkdir()
        (rig_dir / "document.pdf").touch()

        output_file = temp_dir / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Content"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            build_combined_file(["ExistingRig", "NonExistentRig"], source_dir, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "ExistingRig" in content
        assert "NonExistentRig" not in content

    def test_build_combined_file_handles_pdf_and_docx(self, temp_dir):
        """Should handle both PDF and DOCX files."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "MixedRig"
        rig_dir.mkdir()
        (rig_dir / "ROP.pdf").touch()
        (rig_dir / "JSA.docx").touch()

        output_file = temp_dir / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf, \
             patch("src.ingestion.extract_text.docx.Document") as mock_docx:
            # Mock PDF
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF content"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            # Mock DOCX
            mock_para = MagicMock()
            mock_para.text = "DOCX content"
            mock_doc = MagicMock()
            mock_doc.paragraphs = [mock_para]
            mock_docx.return_value = mock_doc

            build_combined_file(["MixedRig"], source_dir, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "ROP" in content
        assert "JSA" in content

    def test_build_combined_file_skips_unsupported_formats(self, temp_dir):
        """Should skip unsupported file formats."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "TestRig"
        rig_dir.mkdir()
        (rig_dir / "document.pdf").touch()
        (rig_dir / "readme.txt").touch()  # Unsupported

        output_file = temp_dir / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF content"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            build_combined_file(["TestRig"], source_dir, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "document" in content
        assert "readme" not in content

    def test_build_combined_file_handles_extraction_error(self, temp_dir):
        """Should handle errors during text extraction gracefully."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "ErrorRig"
        rig_dir.mkdir()
        (rig_dir / "corrupted.pdf").touch()

        output_file = temp_dir / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_pdf.side_effect = Exception("Corrupted PDF")

            build_combined_file(["ErrorRig"], source_dir, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "[ERROR:" in content
        assert "Could not extract text" in content

    def test_build_combined_file_creates_parent_directories(self, temp_dir):
        """Should create parent directories for output file."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "TestRig"
        rig_dir.mkdir()
        (rig_dir / "document.pdf").touch()

        # Deep nested output path
        output_file = temp_dir / "deep" / "nested" / "path" / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Content"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            build_combined_file(["TestRig"], source_dir, output_file)

        assert output_file.exists()

    def test_build_combined_file_utf8_encoding(self, temp_dir):
        """Should write output with UTF-8 encoding."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "TestRig"
        rig_dir.mkdir()
        (rig_dir / "document.pdf").touch()

        output_file = temp_dir / "combined.txt"

        with patch("src.ingestion.extract_text.PdfReader") as mock_pdf:
            mock_page = MagicMock()
            # Include Unicode characters
            mock_page.extract_text.return_value = "Content with unicode: \u00e9\u00e8\u00ea"
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            mock_pdf.return_value = mock_reader

            build_combined_file(["TestRig"], source_dir, output_file)

        content = output_file.read_text(encoding="utf-8")
        assert "\u00e9\u00e8\u00ea" in content

    def test_build_combined_file_empty_rigs_list(self, temp_dir):
        """Should create empty output file for empty rigs list."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        output_file = temp_dir / "combined.txt"

        build_combined_file([], source_dir, output_file)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert content == ""
