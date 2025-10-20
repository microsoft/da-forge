"""
Tests for manifest generation and revision logic.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from da_forge import config, manifest


@pytest.fixture
def temp_dirs(monkeypatch):
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create temporary directories
        socket_folder = tmp_path / "sockets"
        raw_manifest_folder = tmp_path / "raw_manifests"
        zipped_folder = tmp_path / "zipped_manifests"
        template_folder = tmp_path / "templates" / "default"

        socket_folder.mkdir(parents=True)
        raw_manifest_folder.mkdir(parents=True)
        zipped_folder.mkdir(parents=True)
        template_folder.mkdir(parents=True)

        # Copy template files
        original_template = config.TEMPLATE_FOLDER
        for file_path in original_template.iterdir():
            if file_path.is_file():
                shutil.copy2(file_path, template_folder / file_path.name)

        # Patch config paths
        monkeypatch.setattr(config, "SOCKET_FOLDER", socket_folder)
        monkeypatch.setattr(config, "RAW_MANIFEST_FOLDER", raw_manifest_folder)
        monkeypatch.setattr(config, "ZIPPED_MANIFESTS_FOLDER", zipped_folder)
        monkeypatch.setattr(config, "TEMPLATE_FOLDER", template_folder)

        yield {
            "socket": socket_folder,
            "raw_manifest": raw_manifest_folder,
            "zipped": zipped_folder,
            "template": template_folder,
        }


def test_create_raw_manifest(temp_dirs):
    """Test creating a raw manifest from template."""
    name = "TestAgent"
    description = "Test description"
    instruction = "Test instruction"

    manifest_folder = manifest.create_raw_manifest(name, description, instruction)

    # Check folder created
    assert manifest_folder.exists()
    assert manifest_folder.name == name

    # Check files copied
    assert (manifest_folder / config.MANIFEST_FILENAME).exists()
    assert (manifest_folder / config.APP_MANIFEST_FILENAME).exists()
    assert (manifest_folder / config.COLOR_ICON).exists()
    assert (manifest_folder / config.OUTLINE_ICON).exists()

    # Check manifest.json updated correctly
    with open(manifest_folder / config.APP_MANIFEST_FILENAME) as f:
        app_manifest = json.load(f)

    assert app_manifest["name"]["short"] == name
    assert app_manifest["name"]["full"] == name
    assert app_manifest["description"]["full"] == description
    assert len(app_manifest["id"]) == 36  # UUID length
    assert len(app_manifest["copilotAgents"]["declarativeAgents"][0]["id"]) == 36

    # Check declarativeAgent_0.json updated correctly
    with open(manifest_folder / config.MANIFEST_FILENAME) as f:
        da_manifest = json.load(f)

    assert da_manifest["name"] == name
    assert da_manifest["description"] == description
    assert da_manifest["instructions"] == instruction
    assert len(da_manifest["id"]) == 36  # UUID length

    # IDs should match between files
    assert da_manifest["id"] == app_manifest["copilotAgents"]["declarativeAgents"][0]["id"]


def test_revise_da_manifest_basic(temp_dirs):
    """Test revising a manifest with capabilities from socket file."""
    name = "TestAgent"

    # Create raw manifest first
    manifest.create_raw_manifest(name, "desc", "inst")

    # Create socket file with capabilities
    socket_capabilities = [
        {"name": "OneDriveAndSharePoint", "items_by_sharepoint_ids": []},
        {"name": "Email", "x-items_by_id": []},
    ]

    socket_file = temp_dirs["socket"] / f"{name}.json"
    with open(socket_file, "w") as f:
        json.dump(socket_capabilities, f)

    # Revise the manifest
    revised = manifest.revise_da_manifest(name)

    # Check capabilities added
    assert config.FIELD_CAPABILITIES in revised
    assert len(revised[config.FIELD_CAPABILITIES]) == 2

    # Check force flux v3 flag added
    assert revised[config.FIELD_FORCE_FLUXV3] is True

    # Check behavior overrides added
    assert config.FIELD_BEHAVIOR_OVERRIDES in revised
    assert revised[config.FIELD_BEHAVIOR_OVERRIDES] == config.FIELD_BEHAVIOR_OVERRIDES_VALUE


def test_revise_da_manifest_capability_categorization(temp_dirs):
    """Test that capabilities are categorized into regular and experimental."""
    name = "TestAgent"
    manifest.create_raw_manifest(name, "desc", "inst")

    # Create socket with mixed capabilities
    socket_capabilities = [
        {"name": "OneDriveAndSharePoint", "items_by_sharepoint_ids": []},
        {"name": "Email", "x-items_by_id": []},
        {"name": "WebSearch", "sites": []},  # Should go to experimental
        {"name": "Pages"},  # Should go to experimental
        {"name": "Meetings", "x-items_by_id": []},  # Should stay in regular
    ]

    socket_file = temp_dirs["socket"] / f"{name}.json"
    with open(socket_file, "w") as f:
        json.dump(socket_capabilities, f)

    revised = manifest.revise_da_manifest(name)

    # Regular capabilities: OneDrive, Email, Meetings
    regular_caps = revised[config.FIELD_CAPABILITIES]
    regular_names = [cap["name"] for cap in regular_caps]
    assert "OneDriveAndSharePoint" in regular_names
    assert "Email" in regular_names
    assert "Meetings" in regular_names

    # Experimental capabilities: WebSearch, Pages
    experimental_caps = revised.get(config.FIELD_EXPERIMENTAL_CAPABILITIES, [])
    experimental_names = [cap["name"] for cap in experimental_caps]
    assert "WebSearch" in experimental_names
    assert "Pages" in experimental_names


def test_revise_da_manifest_onedrive_cleanup(temp_dirs):
    """Test that OneDrive capability gets 'type' field removed and defaults added."""
    name = "TestAgent"
    manifest.create_raw_manifest(name, "desc", "inst")

    # Create socket with OneDrive capability containing 'type' field
    socket_capabilities = [
        {
            "name": "OneDriveAndSharePoint",
            "items_by_sharepoint_ids": [
                {
                    "site_id": "test-site",
                    "web_id": "test-web",
                    "list_id": "test-list",
                    "unique_id": "test-unique",
                    "type": "File",  # This should be removed
                }
            ],
        }
    ]

    socket_file = temp_dirs["socket"] / f"{name}.json"
    with open(socket_file, "w") as f:
        json.dump(socket_capabilities, f)

    revised = manifest.revise_da_manifest(name)

    # Find OneDrive capability
    onedrive_cap = next(
        cap for cap in revised[config.FIELD_CAPABILITIES]
        if cap["name"] == "OneDriveAndSharePoint"
    )

    # Check 'type' field removed from items
    for item in onedrive_cap["items_by_sharepoint_ids"]:
        assert "type" not in item
        assert "site_id" in item

    # Check default fields added
    assert onedrive_cap["items_by_url"] == []
    assert onedrive_cap["x-force_botspeak"] is False


def test_create_raw_manifest_missing_template(temp_dirs, monkeypatch):
    """Test that creating manifest fails when template folder missing."""
    # Point to non-existent template
    monkeypatch.setattr(config, "TEMPLATE_FOLDER", Path("/nonexistent"))

    with pytest.raises(FileNotFoundError, match="Template folder not found"):
        manifest.create_raw_manifest("TestAgent")


def test_revise_da_manifest_missing_socket(temp_dirs):
    """Test that revising fails when socket file missing."""
    name = "TestAgent"
    manifest.create_raw_manifest(name, "desc", "inst")

    # Don't create socket file
    with pytest.raises(FileNotFoundError, match="Socket file not found"):
        manifest.revise_da_manifest(name)


def test_revise_da_manifest_missing_manifest(temp_dirs):
    """Test that revising fails when manifest file missing."""
    name = "TestAgent"

    # Create socket but no manifest
    socket_file = temp_dirs["socket"] / f"{name}.json"
    with open(socket_file, "w") as f:
        json.dump([], f)

    with pytest.raises(FileNotFoundError, match="Manifest file not found"):
        manifest.revise_da_manifest(name)
