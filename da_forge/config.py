"""
Configuration constants for DA-Forge.
"""

import os
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Folder paths (relative to project root)
SOCKET_FOLDER = PROJECT_ROOT / "sockets"
RAW_MANIFEST_FOLDER = PROJECT_ROOT / "raw_manifests"
ZIPPED_MANIFESTS_FOLDER = PROJECT_ROOT / "zipped_manifests"
TEMPLATE_FOLDER = PROJECT_ROOT / "templates" / "default"

# File names
MANIFEST_FILENAME = "declarativeAgent_0.json"
APP_MANIFEST_FILENAME = "manifest.json"
COLOR_ICON = "color.png"
OUTLINE_ICON = "outline.png"

# Capability names
CAPABILITY_ONEDRIVE_SHAREPOINT = "OneDriveAndSharePoint"
CAPABILITY_WEBSEARCH = "WebSearch"
CAPABILITY_EMAIL = "Email"
CAPABILITY_MEETINGS = "Meetings"
CAPABILITY_PAGES = "Pages"
CAPABILITY_CODE_INTERPRETER = "CodeInterpreter"

# Manifest field names
FIELD_CAPABILITIES = "capabilities"
FIELD_EXPERIMENTAL_CAPABILITIES = "x-experimental_capabilities"
FIELD_FORCE_FLUXV3 = "x-force_fluxv3"
FIELD_BEHAVIOR_OVERRIDES = "behavior_overrides"
FIELD_ITEMS_BY_SHAREPOINT_IDS = "items_by_sharepoint_ids"
FIELD_ITEMS_BY_ID = "x-items_by_id"

# Behavior override configuration
FIELD_BEHAVIOR_OVERRIDES_VALUE = {
    "special_instructions": {
        "discourage_model_knowledge": True
    }
}

# Default fields to add to each capability
CAPABILITY_DEFAULT_FIELDS = {
    "items_by_url": [],
    "x-force_botspeak": False
}
