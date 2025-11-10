"""
Configuration constants for DA-Forge.
"""

from pathlib import Path

# Get package directory (where da_forge is installed)
PACKAGE_DIR = Path(__file__).parent

# Get current working directory
CURRENT_DIR = Path.cwd()


def _get_socket_folder() -> Path:
    """
    Get sockets folder path.

    Checks current directory first, then falls back to package directory.
    This allows both pip-installed and cloned-repo workflows.

    Returns:
        Path to sockets folder
    """
    current_dir_path = CURRENT_DIR / "sockets"
    package_dir_path = PACKAGE_DIR.parent / "sockets"

    if current_dir_path.exists():
        return current_dir_path

    return package_dir_path


def _get_output_folder(folder_name: str) -> Path:
    """
    Get output folder path in current directory.

    Auto-creates the folder if it doesn't exist.
    Output folders (raw_manifests, zipped_manifests) are always created
    in the current working directory.

    Args:
        folder_name: Name of the folder

    Returns:
        Path to the folder in current directory
    """
    folder_path = CURRENT_DIR / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


def _get_template_folder() -> Path:
    """
    Get templates folder path.

    Always uses the package's bundled templates.

    Returns:
        Path to templates/default folder in package
    """
    return PACKAGE_DIR / "templates" / "default"


# Folder paths
SOCKET_FOLDER = _get_socket_folder()
RAW_MANIFEST_FOLDER = _get_output_folder("raw_manifests")
ZIPPED_MANIFESTS_FOLDER = _get_output_folder("zipped_manifests")
TEMPLATE_FOLDER = _get_template_folder()

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

# OneNote field names
FIELD_X_PART_ID = "x-part_id"
FIELD_PART_ID = "part_id"
FIELD_X_PART_TYPE = "x-part_type"
FIELD_PART_TYPE = "part_type"

# Common fields to remove
FIELD_TYPE = "type"
FIELD_NAME = "name"

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
