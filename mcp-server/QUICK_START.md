# GL Publisher MCP Server - Quick Start

## What You Need
- ✅ Claude Desktop ([download](https://claude.ai/download))
- ✅ Python 3.9+
- ✅ oracle-gl-publisher repo cloned locally

## Install (3 commands)

```bash
# 1. Clone this repo
git clone <repo-url>
cd ledger-bot-app

# 2. Install
pip install -e .
cd mcp-server && pip install -e .

# 3. Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json
```

Add this:
```json
{
  "mcpServers": {
    "gl-publisher": {
      "command": "python",
      "args": ["-m", "gl_publisher_mcp.server"],
      "env": {
        "GL_PUBLISHER_PATH": "/path/to/your/oracle-gl-publisher"
      }
    }
  }
}
```

Restart Claude Desktop. Look for 🔌 icon.

## Try It

In Claude Desktop:
```
Use search_adrs to find ADRs about idempotency
```

## Full Guide
See `TEAM_INSTALL_GUIDE.md` for detailed instructions and troubleshooting.

## Questions?
Ask in #bor-write-eng or DM Kayla
