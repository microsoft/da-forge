"""
Configuration constants for DA-Forge.
"""

from pathlib import Path

# Get project root directory (package installation location)
PROJECT_ROOT = Path(__file__).parent.parent

# Get current working directory
CURRENT_DIR = Path.cwd()


def _get_folder_path(folder_name: str) -> Path:
    """
    Get folder path, checking current directory first, then package directory.

    This allows users to work in their own project directory or use the package directory.

    Args:
        folder_name: Name of the folder to find

    Returns:
        Path to the folder (current dir takes precedence)
    """
    current_dir_path = CURRENT_DIR / folder_name
    package_dir_path = PROJECT_ROOT / folder_name

    # Check current directory first
    if current_dir_path.exists():
        return current_dir_path

    # Fall back to package directory
    return package_dir_path


# Folder paths (check current directory first, then package directory)
SOCKET_FOLDER = _get_folder_path("sockets")
RAW_MANIFEST_FOLDER = _get_folder_path("raw_manifests")
ZIPPED_MANIFESTS_FOLDER = _get_folder_path("zipped_manifests")
TEMPLATE_FOLDER = _get_folder_path("templates") / "default"

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
