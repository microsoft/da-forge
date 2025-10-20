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

```bash
# Clone the repository
git clone https://github.com/yourusername/da-forge.git
cd da-forge

# Install in editable mode
pip install -e .
```

After installation, the `da-forge` command will be available globally.

### Usage

**Step 1: Extract Socket JSON from Copilot Notebook**

1. Open your Copilot Notebook in Microsoft 365
2. Add your grounding references (emails, meetings, files, pages)
3. Open Browser DevTools (F12) → **Network** tab
4. Look for API calls to `create` or `update` endpoints
5. Find the request payload containing your capabilities array
6. Copy the capabilities JSON array
7. Save to: `sockets/my-notebook-agent.json`

📖 **Detailed guide:** See [docs/capabilities.md](docs/capabilities.md) for step-by-step instructions with screenshots.

**Step 2: Deploy Your Agent**

```bash
da-forge deploy my-notebook-agent
```

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

### Setup development environment

```bash
# Clone and install with dev dependencies
git clone https://github.com/yourusername/da-forge.git
cd da-forge
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Format code

```bash
black da_forge/
ruff check da_forge/
```

---

## Troubleshooting

### Socket file not found

**Error:** `✗ Socket file not found: sockets/my-agent.json`

**Solution:** Make sure you've created the socket file first. See [examples/README.md](examples/README.md).

### teamsapp command not found

**Error:** `✗ 'teamsapp' command not found`

**Solution:** Install Teams Toolkit CLI:
```bash
npm install -g @microsoft/teamsapp-cli
```

### Sideload failed

**Error:** `✗ Sideload failed with return code: 1`

**Solution:**
- Ensure you're logged into Teams Toolkit: `teamsapp account show`
- Check if the manifest is valid
- Try manual installation: Upload the zip from `zipped_manifests/` in Teams

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built to simplify Declarative Agent development with Microsoft 365 grounding.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/da-forge/issues)
- **Documentation**: See [examples/](examples/) folder

---

**Made with ❤️ for Microsoft 365 developers**
