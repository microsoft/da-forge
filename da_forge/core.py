"""
Core deployment orchestration logic for Declarative Agents.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from da_forge import config
from da_forge.manifest import create_raw_manifest, revise_da_manifest
from da_forge.packaging import zip_manifest


def validate_socket_file(name: str) -> bool:
    """
    Validate that the socket file exists.

    Args:
        name: Name of the DA (socket filename without .json)

    Returns:
        True if socket file exists, False otherwise
    """
    socket_path = config.SOCKET_FOLDER / f"{name}.json"
    if not socket_path.exists():
        print(f"✗ Socket file not found: {socket_path}")
        print(f"\nPlease create the socket file first:")
        print(f"  1. Extract socket JSON from Copilot Notebook (see docs/capabilities.md)")
        print(f"  2. Save it to: {socket_path}")
        return False
    print(f"✓ Socket file found: {socket_path}")
    return True


def sideload_to_teams(zip_path: Path) -> bool:
    """
    Sideload the agent to Teams using teamsapp CLI.

    Args:
        zip_path: Path to the zip file to sideload

    Returns:
        True if sideload succeeded, False otherwise
    """
    if not zip_path.exists():
        print(f"✗ Zip file not found: {zip_path}")
        return False

    try:
        cmd = ["teamsapp", "install", "--file-path", str(zip_path)]
        print(f"Running: {' '.join(cmd)}")

        # On Windows, use shell=True to ensure PATH is properly resolved
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=True if sys.platform == "win32" else False,
        )

        # Log stdout and stderr
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print("✓ Successfully sideloaded to Teams!")
            return True
        else:
            print(f"✗ Sideload failed with return code: {result.returncode}")
            return False

    except FileNotFoundError:
        print("✗ 'teamsapp' command not found.")
        print("\nPlease install Teams Toolkit CLI:")
        print("  npm install -g @microsoft/teamsapp-cli")
        return False
    except Exception as e:
        print(f"✗ Failed to sideload: {e}")
        return False


def deploy_agent(
    name: str, description: str = "-", instruction: str = "-", skip_sideload: bool = False
) -> bool:
    """
    Main deployment function that orchestrates all steps.

    Workflow:
        1. Validate socket file exists
        2. Create raw manifest from template
        3. Revise manifest with capabilities from socket
        4. Zip the manifest
        5. Sideload to Teams (optional)

    Args:
        name: Name of the DA (must match socket file name)
        description: Description for the DA (default: "-")
        instruction: Instructions for the DA (default: "-")
        skip_sideload: If True, skip sideloading to Teams

    Returns:
        True if all steps succeeded, False otherwise
    """
    print("=" * 60)
    print(f"  DEPLOYING DECLARATIVE AGENT: {name}")
    print("=" * 60)
    print()

    # Step 1: Validate socket file exists
    print("STEP 1: Validating socket file")
    if not validate_socket_file(name):
        return False
    print()

    # Step 2: Create raw manifest
    print("STEP 2: Creating raw manifest from template")
    try:
        create_raw_manifest(name, description, instruction)
    except Exception as e:
        print(f"✗ Failed to create manifest: {e}")
        return False
    print()

    # Step 3: Revise manifest with capabilities
    print("STEP 3: Revising manifest with capabilities from socket")
    try:
        revise_da_manifest(name)
    except Exception as e:
        print(f"✗ Failed to revise manifest: {e}")
        return False
    print()

    # Step 4: Zip manifest
    print("STEP 4: Zipping manifest")
    try:
        zip_path = zip_manifest(name)
    except Exception as e:
        print(f"✗ Failed to zip manifest: {e}")
        return False
    print()

    # Step 5: Sideload to Teams (optional)
    if not skip_sideload:
        print("STEP 5: Sideloading to Teams")
        if not sideload_to_teams(zip_path):
            print()
            print("=" * 60)
            print("  DEPLOYMENT COMPLETED WITH ERRORS")
            print("=" * 60)
            print()
            print(f"Manifest created at: {zip_path}")
            print("You can manually install the agent in Teams.")
            return False
        print()

    # Success!
    print("=" * 60)
    print("  DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print(f"Agent '{name}' has been deployed!")
    if skip_sideload:
        print(f"Package location: {zip_path}")

    return True


def list_agents() -> None:
    """
    List all available agents (socket files in sockets/ folder).
    """
    print("Available agents (socket files):")
    print()

    socket_files = sorted(config.SOCKET_FOLDER.glob("*.json"))

    if not socket_files:
        print("  No agents found in sockets/ folder")
        print()
        print("Create a socket file to get started:")
        print("  1. See examples/ folder for reference")
        print("  2. Create sockets/your-agent-name.json")
        return

    for socket_file in socket_files:
        agent_name = socket_file.stem
        print(f"  - {agent_name}")

    print()
    print(f"Total: {len(socket_files)} agent(s)")
