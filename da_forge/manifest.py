"""
Manifest generation and revision logic for Declarative Agents.
"""

import json
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from da_forge import config


def create_raw_manifest(
    name: str,
    description: str = "-",
    instruction: str = "-",
    existing_ids: Optional[Tuple[str, str]] = None,
) -> Path:
    """
    Creates a raw manifest folder for a given DA name from template.

    Generates manifest files including:
    - declarativeAgent_0.json
    - manifest.json
    - outline.png
    - color.png

    Args:
        name: The name of the Declarative Agent
        description: Description for the DA (default: "-")
        instruction: Instructions for the DA (default: "-")
        existing_ids: Optional tuple of (manifest_id, declarative_agent_id) to preserve
                      from an existing manifest. If None, new UUIDs will be generated.

    Returns:
        Path to the created manifest folder

    Raises:
        FileNotFoundError: If template folder doesn't exist
    """
    # Create the raw manifest folder
    manifest_folder = config.RAW_MANIFEST_FOLDER / name
    manifest_folder.mkdir(parents=True, exist_ok=True)

    # Copy template files to the new manifest folder
    if not config.TEMPLATE_FOLDER.exists():
        raise FileNotFoundError(f"Template folder not found: {config.TEMPLATE_FOLDER}")

    for file_path in config.TEMPLATE_FOLDER.iterdir():
        if file_path.is_file():
            shutil.copy2(file_path, manifest_folder / file_path.name)

    # Use existing IDs if provided, otherwise generate new GUIDs
    if existing_ids:
        manifest_id, declarative_agent_id = existing_ids
        print(f"  - Reusing existing Manifest ID: {manifest_id}")
        print(f"  - Reusing existing Declarative Agent ID: {declarative_agent_id}")
    else:
        manifest_id = str(uuid.uuid4())
        declarative_agent_id = str(uuid.uuid4())

    # Update manifest.json
    manifest_json_path = manifest_folder / config.APP_MANIFEST_FILENAME
    with open(manifest_json_path, "r", encoding="utf-8") as f:
        manifest_json = json.load(f)

    # Update main id
    manifest_json["id"] = manifest_id

    # Update name (short name must be <= 30 characters for sideload)
    short_name = name[:30] if len(name) > 30 else name
    manifest_json["name"]["short"] = short_name
    manifest_json["name"]["full"] = name

    # Update description
    manifest_json["description"]["full"] = description

    # Update declarativeAgent id
    manifest_json["copilotAgents"]["declarativeAgents"][0]["id"] = declarative_agent_id

    # Save updated manifest.json
    with open(manifest_json_path, "w", encoding="utf-8") as f:
        json.dump(manifest_json, f, indent=2, ensure_ascii=False)

    # Update declarativeAgent_0.json
    da_json_path = manifest_folder / config.MANIFEST_FILENAME
    with open(da_json_path, "r", encoding="utf-8") as f:
        da_json = json.load(f)

    # Update declarativeAgent id (must match manifest.json)
    da_json["id"] = declarative_agent_id

    # Update name
    da_json["name"] = name

    # Update description
    da_json["description"] = description

    # Update instructions
    da_json["instructions"] = instruction

    # Save updated declarativeAgent_0.json
    with open(da_json_path, "w", encoding="utf-8") as f:
        json.dump(da_json, f, indent=2, ensure_ascii=False)

    print(f"✓ Created manifest folder: {manifest_folder}")
    print(f"  - Manifest ID: {manifest_id}")
    print(f"  - Declarative Agent ID: {declarative_agent_id}")

    return manifest_folder


def revise_da_manifest(name: str) -> Dict:
    """
    Revises a DA manifest by loading capabilities from a socket file.

    The socket file contains capability configurations that are injected
    into the manifest. Capabilities are automatically categorized into
    regular and experimental based on capability type.

    Args:
        name: The name of DA (must match folder name in raw_manifests and socket filename)

    Returns:
        The revised DA manifest as a dictionary

    Raises:
        FileNotFoundError: If socket file or manifest file doesn't exist

    Note:
        Workflow: sockets/{name}.json -> raw_manifests/{name}/ -> zipped_manifests/{name}.zip
    """
    # Load the capability from socket file
    socket_file_path = config.SOCKET_FOLDER / f"{name}.json"

    if not socket_file_path.exists():
        raise FileNotFoundError(f"Socket file not found: {socket_file_path}")

    with open(socket_file_path, "r", encoding="utf-8") as f:
        capability_from_socket = f.read()

    # Load the original manifest
    manifest_path = config.RAW_MANIFEST_FOLDER / name / config.MANIFEST_FILENAME

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Remove the original capabilities key if exists
    if config.FIELD_CAPABILITIES in manifest:
        del manifest[config.FIELD_CAPABILITIES]

    # Parse the capability string into a list
    capabilities_list = json.loads(capability_from_socket)

    # Add force flux v3 flag
    manifest[config.FIELD_FORCE_FLUXV3] = True

    # Add behavior_overrides
    manifest[config.FIELD_BEHAVIOR_OVERRIDES] = config.FIELD_BEHAVIOR_OVERRIDES_VALUE

    # Separate capabilities into regular and experimental
    regular_capabilities = []
    experimental_capabilities = []

    for cap in capabilities_list:
        cap_name = cap.get("name")

        if cap_name == config.CAPABILITY_ONEDRIVE_SHAREPOINT:
            # Remove "type" and "name" fields, rename x-part_* fields for OneNote items
            cleaned_cap = cap.copy()
            if config.FIELD_ITEMS_BY_SHAREPOINT_IDS in cleaned_cap:
                cleaned_items = []
                for item in cleaned_cap[config.FIELD_ITEMS_BY_SHAREPOINT_IDS]:
                    # Remove type and name fields
                    cleaned_item = {
                        k: v for k, v in item.items()
                        if k not in (config.FIELD_TYPE, config.FIELD_NAME)
                    }

                    # Rename x-part_id to part_id and x-part_type to part_type for OneNote items
                    if config.FIELD_X_PART_ID in cleaned_item:
                        cleaned_item[config.FIELD_PART_ID] = cleaned_item.pop(config.FIELD_X_PART_ID)
                    if config.FIELD_X_PART_TYPE in cleaned_item:
                        cleaned_item[config.FIELD_PART_TYPE] = cleaned_item.pop(config.FIELD_X_PART_TYPE)

                    cleaned_items.append(cleaned_item)

                cleaned_cap[config.FIELD_ITEMS_BY_SHAREPOINT_IDS] = cleaned_items
            # add default fields
            for field, default_value in config.CAPABILITY_DEFAULT_FIELDS.items():
                if field not in cleaned_cap:
                    cleaned_cap[field] = default_value
            regular_capabilities.append(cleaned_cap)

        elif cap_name == config.CAPABILITY_WEBSEARCH:
            # Always move WebSearch to experimental_capabilities
            experimental_capabilities.append(cap)

        elif cap_name == config.CAPABILITY_EMAIL:
            # Always keep Email in regular capabilities
            regular_capabilities.append(cap)

        elif cap_name == config.CAPABILITY_MEETINGS:
            # Move Meetings to experimental_capabilities
            regular_capabilities.append(cap)

        elif cap_name == config.CAPABILITY_PAGES:
            # Always move Pages to experimental_capabilities
            experimental_capabilities.append(cap)

        else:
            # Keep other capabilities as regular
            regular_capabilities.append(cap)

    # Update the manifest
    manifest[config.FIELD_CAPABILITIES] = regular_capabilities

    # Add experimental_capabilities if there are any
    if experimental_capabilities:
        manifest[config.FIELD_EXPERIMENTAL_CAPABILITIES] = experimental_capabilities

    # Save the revised manifest
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✓ Revised manifest with capabilities from socket")

    return manifest
