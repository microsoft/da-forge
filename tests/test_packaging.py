"""
Tests for manifest packaging (zipping) logic.
"""

import tempfile
import zipfile
from pathlib import Path

import pytest

from da_forge import config, packaging


@pytest.fixture
def temp_dirs(monkeypatch):
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        raw_manifest_folder = tmp_path / "raw_manifests"
        zipped_folder = tmp_path / "zipped_manifests"

        raw_manifest_folder.mkdir(parents=True)
        # Don't create zipped_folder - let the function create it

        monkeypatch.setattr(config, "RAW_MANIFEST_FOLDER", raw_manifest_folder)
        monkeypatch.setattr(config, "ZIPPED_MANIFESTS_FOLDER", zipped_folder)

        yield {
            "raw_manifest": raw_manifest_folder,
            "zipped": zipped_folder,
        }


def test_zip_manifest_basic(temp_dirs):
    """Test zipping a manifest folder."""
    name = "TestAgent"

    # Create a manifest folder with some files
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()

    (manifest_folder / "declarativeAgent_0.json").write_text('{"name": "test"}')
    (manifest_folder / "manifest.json").write_text('{"id": "123"}')
    (manifest_folder / "color.png").write_bytes(b"fake png")

    # Zip it
    zip_path = packaging.zip_manifest(name)

    # Check zip file created
    assert zip_path.exists()
    assert zip_path.name == f"{name}.zip"
    assert zip_path.parent == temp_dirs["zipped"]

    # Check zip contents
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "declarativeAgent_0.json" in names
        assert "manifest.json" in names
        assert "color.png" in names

        # Verify file contents
        assert zf.read("declarativeAgent_0.json") == b'{"name": "test"}'
        assert zf.read("color.png") == b"fake png"


def test_zip_manifest_creates_zipped_folder(temp_dirs):
    """Test that zip_manifest creates the zipped_manifests folder if it doesn't exist."""
    name = "TestAgent"

    # Create manifest folder
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()
    (manifest_folder / "test.txt").write_text("test")

    # Ensure zipped folder doesn't exist
    assert not temp_dirs["zipped"].exists()

    # Zip it
    zip_path = packaging.zip_manifest(name)

    # Check zipped folder was created
    assert temp_dirs["zipped"].exists()
    assert zip_path.exists()


def test_zip_manifest_replaces_existing_zip(temp_dirs, capsys):
    """Test that existing zip files are replaced."""
    name = "TestAgent"

    # Create manifest folder
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()
    (manifest_folder / "file1.txt").write_text("version 1")

    # Create first zip
    zip_path = packaging.zip_manifest(name)
    first_size = zip_path.stat().st_size

    # Update the manifest
    (manifest_folder / "file1.txt").write_text("version 2 - much longer content")
    (manifest_folder / "file2.txt").write_text("new file")

    # Zip again
    zip_path2 = packaging.zip_manifest(name)

    # Check paths are the same
    assert zip_path == zip_path2

    # Check content updated
    with zipfile.ZipFile(zip_path2, "r") as zf:
        assert zf.read("file1.txt") == b"version 2 - much longer content"
        assert "file2.txt" in zf.namelist()

    # Check output message
    captured = capsys.readouterr()
    assert "Removed existing zip" in captured.out
    assert "Created zip" in captured.out


def test_zip_manifest_nested_folders(temp_dirs):
    """Test zipping a manifest with nested folder structure."""
    name = "TestAgent"

    # Create manifest with nested folders
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()
    (manifest_folder / "root.json").write_text("{}")

    subfolder = manifest_folder / "assets" / "icons"
    subfolder.mkdir(parents=True)
    (subfolder / "icon.png").write_bytes(b"icon data")

    # Zip it
    zip_path = packaging.zip_manifest(name)

    # Check nested structure preserved
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "root.json" in names
        assert "assets/icons/icon.png" in names
        assert zf.read("assets/icons/icon.png") == b"icon data"


def test_zip_manifest_missing_folder(temp_dirs):
    """Test that zipping fails when source folder doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Manifest folder not found"):
        packaging.zip_manifest("NonExistentAgent")


def test_zip_manifest_empty_folder(temp_dirs):
    """Test zipping an empty manifest folder."""
    name = "EmptyAgent"

    # Create empty manifest folder
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()

    # Zip it
    zip_path = packaging.zip_manifest(name)

    # Check zip created but empty
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert len(zf.namelist()) == 0


def test_extract_ids_from_zip(temp_dirs):
    """Test extracting IDs from an existing zip file."""
    name = "TestAgent"

    # Create a manifest folder with proper structure
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()

    # Create manifest.json with IDs
    manifest_content = {
        "id": "test-manifest-id-12345",
        "name": {"short": name, "full": name},
        "copilotAgents": {
            "declarativeAgents": [
                {"id": "test-da-id-67890"}
            ]
        }
    }

    import json
    (manifest_folder / "manifest.json").write_text(json.dumps(manifest_content))

    # Create the zip
    zip_path = packaging.zip_manifest(name)

    # Extract IDs from the zip
    result = packaging.extract_ids_from_zip(zip_path)

    # Verify the IDs
    assert result is not None
    manifest_id, da_id = result
    assert manifest_id == "test-manifest-id-12345"
    assert da_id == "test-da-id-67890"


def test_extract_ids_from_zip_nonexistent(temp_dirs):
    """Test extracting IDs from a non-existent zip file."""
    zip_path = temp_dirs["zipped"] / "NonExistent.zip"
    result = packaging.extract_ids_from_zip(zip_path)
    assert result is None


def test_extract_ids_from_zip_invalid_structure(temp_dirs):
    """Test extracting IDs from a zip with invalid manifest structure."""
    name = "InvalidAgent"

    # Create a manifest folder with incomplete structure
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()

    import json

    # Missing required fields
    manifest_content = {
        "name": {"short": name}
        # No "id" or "copilotAgents"
    }

    (manifest_folder / "manifest.json").write_text(json.dumps(manifest_content))

    # Create the zip
    zip_path = packaging.zip_manifest(name)

    # Try to extract IDs (should return None due to missing fields)
    result = packaging.extract_ids_from_zip(zip_path)
    assert result is None


def test_extract_ids_from_zip_corrupted_json(temp_dirs):
    """Test extracting IDs from a zip with corrupted manifest.json."""
    name = "CorruptedAgent"

    # Create a manifest folder with invalid JSON
    manifest_folder = temp_dirs["raw_manifest"] / name
    manifest_folder.mkdir()

    (manifest_folder / "manifest.json").write_text("{invalid json content")

    # Create the zip
    zip_path = packaging.zip_manifest(name)

    # Try to extract IDs (should return None due to JSON error)
    result = packaging.extract_ids_from_zip(zip_path)
    assert result is None
