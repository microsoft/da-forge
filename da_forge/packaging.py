"""
ZIP packaging logic for Declarative Agent manifests.
"""

import shutil
from pathlib import Path
from typing import Optional

from da_forge import config


def zip_manifest(name: str) -> Path:
    """
    Zip a manifest folder from raw_manifests into zipped_manifests.

    Args:
        name: Name of the DA folder to zip

    Returns:
        Path to the created zip file

    Raises:
        FileNotFoundError: If source folder doesn't exist

    Note:
        If the zip already exists, it will be replaced.
        Workflow: raw_manifests/{name}/ -> zipped_manifests/{name}.zip
    """
    # Create zipped_manifests directory if it doesn't exist
    config.ZIPPED_MANIFESTS_FOLDER.mkdir(parents=True, exist_ok=True)

    # Get source folder
    source_folder = config.RAW_MANIFEST_FOLDER / name

    # Check if source folder exists
    if not source_folder.exists():
        raise FileNotFoundError(f"Manifest folder not found: {source_folder}")

    # Define the zip file path (without .zip extension, shutil will add it)
    zip_base_path = config.ZIPPED_MANIFESTS_FOLDER / name
    zip_file_path = Path(f"{zip_base_path}.zip")

    # Remove existing zip file if it exists
    if zip_file_path.exists():
        zip_file_path.unlink()
        print(f"✓ Removed existing zip: {zip_file_path.name}")

    # Create the zip file
    shutil.make_archive(str(zip_base_path), "zip", source_folder)
    print(f"✓ Created zip: {zip_file_path}")

    return zip_file_path
