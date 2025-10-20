"""
Tests for core deployment orchestration logic.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from da_forge import config, core


@pytest.fixture
def temp_dirs(monkeypatch):
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        socket_folder = tmp_path / "sockets"
        raw_manifest_folder = tmp_path / "raw_manifests"
        zipped_folder = tmp_path / "zipped_manifests"
        template_folder = tmp_path / "templates" / "default"

        socket_folder.mkdir(parents=True)
        raw_manifest_folder.mkdir(parents=True)
        zipped_folder.mkdir(parents=True)
        template_folder.mkdir(parents=True)

        # Copy template files from real template folder
        import shutil
        for file_path in config.TEMPLATE_FOLDER.iterdir():
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


def test_validate_socket_file_exists(temp_dirs, capsys):
    """Test validation passes when socket file exists."""
    name = "TestAgent"
    socket_file = temp_dirs["socket"] / f"{name}.json"
    socket_file.write_text("[]")

    result = core.validate_socket_file(name)

    assert result is True
    captured = capsys.readouterr()
    assert "✓ Socket file found" in captured.out


def test_validate_socket_file_missing(temp_dirs, capsys):
    """Test validation fails when socket file doesn't exist."""
    result = core.validate_socket_file("NonExistent")

    assert result is False
    captured = capsys.readouterr()
    assert "✗ Socket file not found" in captured.out
    assert "Please create the socket file first" in captured.out


def test_sideload_to_teams_missing_zip(capsys):
    """Test sideload fails when zip file doesn't exist."""
    result = core.sideload_to_teams(Path("/nonexistent/file.zip"))

    assert result is False
    captured = capsys.readouterr()
    assert "✗ Zip file not found" in captured.out


@patch("subprocess.run")
def test_sideload_to_teams_success(mock_run, tmp_path, capsys):
    """Test successful sideload to Teams."""
    # Create a dummy zip file
    zip_path = tmp_path / "test.zip"
    zip_path.write_bytes(b"fake zip")

    # Mock successful subprocess
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="Installation successful",
        stderr="",
    )

    result = core.sideload_to_teams(zip_path)

    assert result is True
    captured = capsys.readouterr()
    assert "✓ Successfully sideloaded to Teams!" in captured.out

    # Verify teamsapp command was called
    mock_run.assert_called_once()
    call_args = mock_run.call_args
    assert "teamsapp" in call_args[0][0]
    assert "install" in call_args[0][0]
    assert str(zip_path) in call_args[0][0]


@patch("subprocess.run")
def test_sideload_to_teams_failure(mock_run, tmp_path, capsys):
    """Test sideload failure."""
    zip_path = tmp_path / "test.zip"
    zip_path.write_bytes(b"fake zip")

    # Mock failed subprocess
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout="",
        stderr="Error: Installation failed",
    )

    result = core.sideload_to_teams(zip_path)

    assert result is False
    captured = capsys.readouterr()
    assert "✗ Sideload failed" in captured.out


@patch("subprocess.run")
def test_sideload_to_teams_command_not_found(mock_run, tmp_path, capsys):
    """Test sideload when teamsapp command not found."""
    zip_path = tmp_path / "test.zip"
    zip_path.write_bytes(b"fake zip")

    # Mock command not found
    mock_run.side_effect = FileNotFoundError()

    result = core.sideload_to_teams(zip_path)

    assert result is False
    captured = capsys.readouterr()
    assert "✗ 'teamsapp' command not found" in captured.out
    assert "npm install -g @microsoft/teamsapp-cli" in captured.out


def test_deploy_agent_skip_sideload(temp_dirs, capsys):
    """Test full deployment workflow with skip_sideload=True."""
    name = "TestAgent"

    # Create socket file
    socket_file = temp_dirs["socket"] / f"{name}.json"
    socket_file.write_text('[{"name": "WebSearch"}]')

    # Deploy with skip_sideload
    result = core.deploy_agent(
        name=name,
        description="Test description",
        instruction="Test instruction",
        skip_sideload=True,
    )

    assert result is True

    # Check output
    captured = capsys.readouterr()
    assert "STEP 1: Validating socket file" in captured.out
    assert "STEP 2: Creating raw manifest" in captured.out
    assert "STEP 3: Revising manifest" in captured.out
    assert "STEP 4: Zipping manifest" in captured.out
    assert "DEPLOYMENT COMPLETED SUCCESSFULLY" in captured.out

    # Verify files created
    assert (temp_dirs["raw_manifest"] / name).exists()
    assert (temp_dirs["zipped"] / f"{name}.zip").exists()


def test_deploy_agent_missing_socket(temp_dirs, capsys):
    """Test deployment fails when socket file missing."""
    result = core.deploy_agent("NonExistent", skip_sideload=True)

    assert result is False
    captured = capsys.readouterr()
    assert "STEP 1: Validating socket file" in captured.out
    assert "✗ Socket file not found" in captured.out


@patch("da_forge.core.sideload_to_teams")
def test_deploy_agent_with_sideload_success(mock_sideload, temp_dirs, capsys):
    """Test deployment with successful sideload."""
    name = "TestAgent"

    # Create socket file
    socket_file = temp_dirs["socket"] / f"{name}.json"
    socket_file.write_text('[{"name": "Pages"}]')

    # Mock successful sideload
    mock_sideload.return_value = True

    # Deploy with sideload
    result = core.deploy_agent(name, skip_sideload=False)

    assert result is True
    captured = capsys.readouterr()
    assert "STEP 5: Sideloading to Teams" in captured.out
    assert "DEPLOYMENT COMPLETED SUCCESSFULLY" in captured.out

    # Verify sideload was called
    mock_sideload.assert_called_once()


@patch("da_forge.core.sideload_to_teams")
def test_deploy_agent_with_sideload_failure(mock_sideload, temp_dirs, capsys):
    """Test deployment when sideload fails."""
    name = "TestAgent"

    # Create socket file
    socket_file = temp_dirs["socket"] / f"{name}.json"
    socket_file.write_text('[{"name": "CodeInterpreter"}]')

    # Mock failed sideload
    mock_sideload.return_value = False

    # Deploy with sideload
    result = core.deploy_agent(name, skip_sideload=False)

    assert result is False
    captured = capsys.readouterr()
    assert "STEP 5: Sideloading to Teams" in captured.out
    assert "DEPLOYMENT COMPLETED WITH ERRORS" in captured.out
    assert "You can manually install the agent" in captured.out


def test_list_agents_with_agents(temp_dirs, capsys):
    """Test listing agents when socket files exist."""
    # Create some socket files
    (temp_dirs["socket"] / "Agent1.json").write_text("[]")
    (temp_dirs["socket"] / "Agent2.json").write_text("[]")
    (temp_dirs["socket"] / "Agent3.json").write_text("[]")

    core.list_agents()

    captured = capsys.readouterr()
    assert "Available agents" in captured.out
    assert "Agent1" in captured.out
    assert "Agent2" in captured.out
    assert "Agent3" in captured.out
    assert "Total: 3 agent(s)" in captured.out


def test_list_agents_no_agents(temp_dirs, capsys):
    """Test listing agents when no socket files exist."""
    core.list_agents()

    captured = capsys.readouterr()
    assert "No agents found in sockets/ folder" in captured.out
    assert "Create a socket file to get started" in captured.out
