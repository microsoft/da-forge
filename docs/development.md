# Development

## Setup development environment

```bash
# Clone and install with dev dependencies
git clone https://github.com/yourusername/da-forge.git
cd da-forge
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

## Format code

```bash
black da_forge/
ruff check da_forge/
```

## Release Process

The project uses [Semantic Versioning](https://semver.org/) (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Creating a Release

1. **Update version in pyproject.toml**

   Edit [pyproject.toml](../pyproject.toml) and update the version:
   ```toml
   version = "1.0.1"  # Update to your new version
   ```

2. **Commit the version change**

   ```bash
   git add pyproject.toml
   git commit -m "chore: bump version to 1.0.1"
   ```

3. **Create a matching git tag**

   ```bash
   git tag v1.0.1
   ```

   Note: The tag must be prefixed with `v` and match the version in `pyproject.toml`

4. **Push to GitHub**

   ```bash
   git push origin main
   git push origin v1.0.1
   ```

5. **Automated release workflow**

   Once the tag is pushed, the [release workflow](../.github/workflows/release.yml) will automatically:
   - Validate that the git tag version matches `pyproject.toml` version
   - Run all tests to ensure quality
   - Build distribution packages (`.whl` and `.tar.gz`)
   - Create a GitHub Release with auto-generated changelog
   - Attach built artifacts to the release

### Version Validation

The release workflow enforces consistency between the git tag and `pyproject.toml` version:

- If tag is `v1.0.1`, then `pyproject.toml` must have `version = "1.0.1"`
- Mismatches will fail the workflow with a clear error message

### Installing Specific Versions

Users can install specific versions using:

```bash
# Install latest release
pip install git+https://github.com/yourusername/da-forge.git

# Install specific version
pip install git+https://github.com/yourusername/da-forge.git@v1.0.1
```

## Code Maintenance

### Keeping up with Microsoft AI Backend Changes

The critical component [da_forge/manifest.py](../da_forge/manifest.py) serves as a bridge between ChatHub API requests and DA manifest generation. This module processes client-side requests from Microsoft AI, which has specific hardcoded logic for different grounding capabilities.

**Important**: The Microsoft AI codebase backend may change over time. Maintainers need to regularly monitor and sync with the upstream codebase to ensure compatibility.

#### Key Capabilities to Monitor

The following capabilities have specific processing logic that may be updated in the Microsoft AI backend:

- **[Email Capability](https://office.visualstudio.com/Sydney/_git/Sydney?path=/services/TuringBot/Microsoft.TuringBot.Common/Contract/GPT/Capabilities/EmailCapability.cs&_a=contents&version=GBmaster)**: Monitor changes to email grounding and processing
- *[*Meeting Capability](https://office.visualstudio.com/Sydney/_git/Sydney?path=/services/TuringBot/Microsoft.TuringBot.Common/Contract/GPT/Capabilities/MeetingsCapability.cs&_a=contents&version=GBmaster)**: Track updates to calendar/meeting integrations
- **[File Capability](https://office.visualstudio.com/Sydney/_git/Sydney?path=/services/TuringBot/Microsoft.TuringBot.Common/Contract/GPT/Capabilities/OneDriveAndSharePointCapability.cs&_a=contents&version=GBmaster)**: Watch for changes in OneDrive/SharePoint file handling
- **[Web Page Capability](https://office.visualstudio.com/Sydney/_git/Sydney?path=%2Fservices%2FTuringBot%2FMicrosoft.TuringBot.Common%2FContract%2FGPT%2FCapabilities%2FEmailCapability.cs&_a=contents&version=GBmaster)**: Keep synchronized with web page grounding logic (internal access only)

#### Update Process

1. **Monitor upstream changes**: Regularly check the Microsoft AI backend codebase for updates to capability processing
2. **Review manifest.py**: Examine [revise_da_manifest()](../da_forge/manifest.py#L103) function, which handles capability categorization
3. **Update capability handling**: Modify the capability processing logic in [manifest.py](../da_forge/manifest.py) as needed
4. **Test with socket files**: Verify changes work with existing socket configurations
5. **Update documentation**: Document any breaking changes or new requirements