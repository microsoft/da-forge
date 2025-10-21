# DA-Forge 🔨

**Forge Declarative Agents for Copilot Notebooks - Deploy in seconds, not hours.**

Automate the creation and deployment of Declarative Agents that replicate Copilot Notebooks with specific grounding references (emails, meetings, files, webpages).

---

## The Problem

**Copilot Notebooks** is a powerful product for creating project-specific AI assistants with grounding context. However, for research purposes (DevUI and SEVAL), we need to use **Declarative Agents** as a proxy, which introduces significant complexity:

1. ⏰ **Manual manifest creation (~40 minutes)**: Declarative Agents require complex manifest files with specific formats
2. 🔑 **Unique ID extraction (~30 minutes)**: Files, emails, and meetings uploaded as Notebook references generate unique IDs that must be manually extracted and formatted
3. 📋 **Special formatting requirements**: Each capability type (Email, Meetings, Files, Webpages) has its own ID structure and JSON schema
4. 🔧 **DA initiation, and sideloading (~15 minutes)**: Multiple manual steps prone to errors

**Total: ~85 minutes per agent + high error rate**

## The Solution

DA-Forge automates the entire Declarative Agent creation process. Simply extract the socket JSON from your Copilot Notebook configuration, and deploy:

```bash
# After getting socket JSON from Notebook
da-forge deploy my-notebook-agent
```

**Result: Deployment time reduced from 85 minutes to ~2 minutes.**

Your Declarative Agent is now live in Teams with all the grounding context from your Copilot Notebook.

---

## Quick Start

### Prerequisites

- Python 3.10+
- [Teams Toolkit CLI](https://learn.microsoft.com/microsoftteams/platform/toolkit/teams-toolkit-cli) for sideloading

### Installation

**Option 1: Install from GitHub (Recommended)**

```bash
# Install latest release
pip install git+https://github.com/microsoft/da-forge.git

# Or install a specific version
pip install git+https://github.com/microsoft/da-forge.git@v1.0.0
```

**Option 2: Install from source (for development)**

```bash
# Clone the repository
git clone https://github.com/microsoft/da-forge.git
cd da-forge

# Install in editable mode
pip install -e .
```

After installation, the `da-forge` command will be available globally.

### Usage

**Step 1: Set up your project**

```bash
# Create a directory for your agents
mkdir my-agents
cd my-agents

# Create sockets folder for your socket files
mkdir sockets
```

**Step 2: Extract and save socket JSON**

📖 **Detailed guide:** See [docs/capabilities.md](docs/capabilities.md) for step-by-step extraction instructions.

Save the extracted socket JSON to `sockets/my-agent.json`

**Step 3: Deploy your agent**

```bash
da-forge deploy my-agent
```

The tool will automatically:
- Use bundled templates from the package
- Create `raw_manifests/` with generated manifest files
- Create `zipped_manifests/` with the deployment package
- Sideload to Teams (or skip with `--skip-sideload`)

That's it! Your Declarative Agent is now deployed to Teams with all your Notebook's grounding context.

---

## Features

✅ **Zero external dependencies** - Pure Python stdlib
✅ **Automated manifest generation** - From template with GUID generation
✅ **Smart capability injection** - Automatic categorization (regular vs experimental)
✅ **One-command deployment** - Create → Revise → Zip → Sideload
✅ **Socket-based config** - Separate grounding data from boilerplate

---

## CLI Commands

### Deploy an agent

```bash
da-forge deploy <name> [--description TEXT] [--instruction TEXT] [--skip-sideload]
```

**Examples:**
```bash
# Basic deployment
da-forge deploy my-copilot

# With custom description and instructions
da-forge deploy my-copilot --description "Email assistant" --instruction "Help with emails"

# Skip sideloading (just create package)
da-forge deploy my-copilot --skip-sideload
```

### List available agents

```bash
da-forge list
```

Shows all socket files in `sockets/` folder.

---

## Development

See [docs/development.md](docs/development.md) for development setup, testing, and code formatting instructions.

---

## Troubleshooting

### Socket file not found

**Error:** `✗ Socket file not found: sockets/my-agent.json`

**Solution:** Create the socket file first:
1. Extract capabilities JSON from your Copilot Notebook (see [docs/capabilities.md](docs/capabilities.md))
2. Save it to `sockets/my-agent.json`

### teamsapp command not found

**Error:** `✗ 'teamsapp' command not found`

**Solution:** Install Teams Toolkit CLI:
```bash
npm install -g @microsoft/teamsapp-cli
```

### Failed to create manifest

**Error:** `✗ Failed to create manifest: Template folder not found`

**Solution:** This error should not occur with pip-installed packages as templates are bundled. If you encounter this:
- Reinstall the package: `pip install --force-reinstall git+https://github.com/microsoft/da-forge.git`
- If you cloned the repo, ensure `da_forge/templates/default/` exists with all required files

### Failed to revise manifest

**Error:** `✗ Failed to revise manifest: [error details]`

**Common causes:**
- **Invalid JSON in socket file** - Verify your socket file contains valid JSON
- **Missing capabilities array** - Ensure socket file has a capabilities array
- **Corrupted manifest files** - Re-run deployment to regenerate manifests

### Failed to zip manifest

**Error:** `✗ Failed to zip manifest: Manifest folder not found`

**Solution:** This typically happens if earlier steps failed. Check that `raw_manifests/my-agent/` exists with all required files.

### Sideload failed

**Error:** `✗ Sideload failed with return code: 1`

**Solution:**
- Ensure you're logged into Teams Toolkit: `teamsapp account show`
- If authentication fails, run: `teamsapp account login m365`
- If sideload continues to fail, manually upload the zip from `zipped_manifests/` in Teams

**Note:** Even if sideload fails, your manifest zip is created successfully and can be manually installed.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.


**Made with ❤️ for Microsoft 365 developers**
