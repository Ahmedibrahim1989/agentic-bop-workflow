"""Unit tests for src/ingestion/list_rigs.py module."""

import pytest
from pathlib import Path

from src.ingestion.list_rigs import list_rigs


class TestListRigs:
    """Tests for the list_rigs function."""

    def test_list_rigs_returns_sorted_list(self, temp_dir):
        """list_rigs should return alphabetically sorted rig names."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        # Create rig directories in non-alphabetical order
        for name in ["Zebra", "Alpha", "Middle"]:
            rig_dir = source_dir / name
            rig_dir.mkdir()
            (rig_dir / "document.pdf").touch()

        result = list_rigs(source_dir)

        assert result == ["Alpha", "Middle", "Zebra"]

    def test_list_rigs_with_pdf_files(self, temp_dir):
        """list_rigs should find directories containing PDF files."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "DanaRig"
        rig_dir.mkdir()
        (rig_dir / "BOP_Installation.pdf").touch()

        result = list_rigs(source_dir)

        assert "DanaRig" in result

    def test_list_rigs_with_docx_files(self, temp_dir):
        """list_rigs should find directories containing DOCX files."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "AlReemRig"
        rig_dir.mkdir()
        (rig_dir / "Procedure.docx").touch()

        result = list_rigs(source_dir)

        assert "AlReemRig" in result

    def test_list_rigs_with_doc_files(self, temp_dir):
        """list_rigs should find directories containing DOC files."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "OldRig"
        rig_dir.mkdir()
        (rig_dir / "Legacy.doc").touch()

        result = list_rigs(source_dir)

        assert "OldRig" in result

    def test_list_rigs_with_mixed_file_types(self, temp_dir):
        """list_rigs should find directories with mixed document types."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "MixedRig"
        rig_dir.mkdir()
        (rig_dir / "ROP.pdf").touch()
        (rig_dir / "JSA.docx").touch()

        result = list_rigs(source_dir)

        assert "MixedRig" in result
        assert len(result) == 1  # Only one rig

    def test_list_rigs_excludes_directories_without_documents(self, temp_dir):
        """list_rigs should exclude directories without PDF/DOCX files."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        # Directory with documents
        valid_rig = source_dir / "ValidRig"
        valid_rig.mkdir()
        (valid_rig / "document.pdf").touch()

        # Directory without documents
        invalid_rig = source_dir / "InvalidRig"
        invalid_rig.mkdir()
        (invalid_rig / "readme.txt").touch()

        result = list_rigs(source_dir)

        assert "ValidRig" in result
        assert "InvalidRig" not in result

    def test_list_rigs_excludes_hidden_directories(self, temp_dir):
        """list_rigs should exclude hidden directories (starting with .)."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        # Normal directory
        normal_rig = source_dir / "NormalRig"
        normal_rig.mkdir()
        (normal_rig / "document.pdf").touch()

        # Hidden directory
        hidden_rig = source_dir / ".HiddenRig"
        hidden_rig.mkdir()
        (hidden_rig / "document.pdf").touch()

        result = list_rigs(source_dir)

        assert "NormalRig" in result
        assert ".HiddenRig" not in result

    def test_list_rigs_excludes_files_in_root(self, temp_dir):
        """list_rigs should not include files directly in source_dir."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        # File in root (not a directory)
        (source_dir / "standalone.pdf").touch()

        # Valid rig directory
        rig_dir = source_dir / "ValidRig"
        rig_dir.mkdir()
        (rig_dir / "document.pdf").touch()

        result = list_rigs(source_dir)

        assert result == ["ValidRig"]

    def test_list_rigs_with_nested_documents(self, temp_dir):
        """list_rigs should find documents in nested subdirectories."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "NestedRig"
        rig_dir.mkdir()
        subdir = rig_dir / "documents" / "2024"
        subdir.mkdir(parents=True)
        (subdir / "procedure.pdf").touch()

        result = list_rigs(source_dir)

        assert "NestedRig" in result

    def test_list_rigs_returns_empty_for_nonexistent_directory(self, temp_dir):
        """list_rigs should return empty list for non-existent directory."""
        nonexistent = temp_dir / "does_not_exist"

        result = list_rigs(nonexistent)

        assert result == []

    def test_list_rigs_returns_empty_for_empty_directory(self, temp_dir):
        """list_rigs should return empty list for empty directory."""
        source_dir = temp_dir / "empty_source"
        source_dir.mkdir()

        result = list_rigs(source_dir)

        assert result == []

    def test_list_rigs_handles_string_path(self, temp_dir):
        """list_rigs should accept string path."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "StringPathRig"
        rig_dir.mkdir()
        (rig_dir / "document.pdf").touch()

        result = list_rigs(str(source_dir))

        assert "StringPathRig" in result

    def test_list_rigs_handles_path_object(self, temp_dir):
        """list_rigs should accept Path object."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "PathObjectRig"
        rig_dir.mkdir()
        (rig_dir / "document.pdf").touch()

        result = list_rigs(Path(source_dir))

        assert "PathObjectRig" in result

    def test_list_rigs_case_insensitive_extension(self, temp_dir):
        """list_rigs should match extensions case-insensitively."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rig_dir = source_dir / "CaseRig"
        rig_dir.mkdir()
        (rig_dir / "document.PDF").touch()  # Uppercase extension

        result = list_rigs(source_dir)

        assert "CaseRig" in result

    def test_list_rigs_multiple_rigs(self, temp_dir):
        """list_rigs should correctly find multiple rigs."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()

        rigs = ["Dana", "AlReem", "Marawwah", "AlJubail"]
        for name in rigs:
            rig_dir = source_dir / name
            rig_dir.mkdir()
            (rig_dir / "document.pdf").touch()

        result = list_rigs(source_dir)

        assert len(result) == 4
        assert result == sorted(rigs)
