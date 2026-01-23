# GL Publisher MCP Server - Team Installation Guide

## What This Is

An MCP (Model Context Protocol) server that gives **your Claude Desktop** access to GL Publisher knowledge. Claude can search ADRs, read code, find Impact Builders, etc. while helping you code.

**Important:** This runs on YOUR machine, integrated with YOUR Claude Desktop. It's a personal coding assistant, not a shared service.

---

## Prerequisites

- [ ] Claude Desktop installed ([download here](https://claude.ai/download))
- [ ] Python 3.9+ installed
- [ ] Access to oracle-gl-publisher repository (cloned locally)
- [ ] Git installed

---

## Installation Steps

### 1. Clone the Ledger Bot Repository

```bash
cd ~/
git clone <repo-url>  # Get URL from Kayla
cd ledger-bot-app
```

### 2. Install the Shared Knowledge Library

```bash
# From the root of ledger-bot-app
pip install -e .
```

This installs the `gl_publisher_knowledge` library that powers the MCP server.

### 3. Install the MCP Server

```bash
cd mcp-server
pip install -e .
```

### 4. Configure Claude Desktop

Edit your Claude Desktop config file:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

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

**Important:** Change `/path/to/your/oracle-gl-publisher` to where you have the repo cloned!

Example:
- Mac: `/Users/yourname/IdeaProjects/oracle-gl-publisher`
- Windows: `C:\Users\yourname\IdeaProjects\oracle-gl-publisher`

### 5. Restart Claude Desktop

1. Quit Claude Desktop completely
2. Reopen it
3. Look for the 🔌 icon in the bottom right
4. You should see "gl-publisher" listed as connected

---

## Verify It's Working

In Claude Desktop, try:

```
Use the search_adrs tool to find ADRs about idempotency
```

Claude should automatically:
1. Call the `search_adrs` tool
2. Return results from your local oracle-gl-publisher repo
3. Explain what it found

---

## Available Tools

Once installed, Claude can use these tools automatically:

### search_adrs
Search Architecture Decision Records by keyword
```
Find ADRs about reversals
```

### find_impact_builders
Find Impact Builder implementations
```
Show me Impact Builders for trades
```

### get_schema_info
Get Oracle GL schema table information
```
What's the schema for GL_INTERFACE?
```

### read_file
Read specific files from the repository
```
Read the file api/README.md
```

### search_code
Search code patterns in the repository
```
Search for "processActivity" in Kotlin files
```

---

## Troubleshooting

### MCP Server Not Connecting

**Check 1: Is the path correct?**
```bash
# Verify your oracle-gl-publisher path
ls /path/to/your/oracle-gl-publisher
```

**Check 2: Can Python run the server?**
```bash
cd ~/ledger-bot-app/mcp-server
python -m gl_publisher_mcp.server
# Should start without errors (Ctrl+C to stop)
```

**Check 3: Check Claude Desktop logs**
- Mac: `~/Library/Logs/Claude/`
- Look for errors mentioning "gl-publisher"

### Tools Not Working

**Check 1: Is the server connected?**
- Look for 🔌 icon in Claude Desktop
- Should show "gl-publisher" as connected

**Check 2: Is the shared library installed?**
```bash
python -c "import gl_publisher_knowledge; print('OK')"
# Should print "OK"
```

**Check 3: Restart Claude Desktop**
- Quit completely
- Reopen

### Permission Errors

**On Mac:**
```bash
# Make sure Python has disk access
# System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add your Python interpreter
```

---

## How to Use It

### Natural Language

Claude decides when to use tools automatically. Just ask naturally:

```
"What ADRs mention idempotency?"
Claude will: search_adrs("idempotency")

"Show me the schema for GL_INTERFACE"
Claude will: get_schema_info("GL_INTERFACE")

"Find Impact Builders for cash deposits"
Claude will: find_impact_builders("cash deposit")
```

### Explicit Tool Requests

You can also explicitly ask Claude to use a tool:

```
"Use search_adrs to find reversals"
"Use read_file to show me api/README.md"
"Use search_code to find processActivity"
```

### While Coding

The real power is when Claude uses tools autonomously:

```
You: "Help me implement a reversal feature"

Claude: [searches ADR 0010, reads relevant code, finds Impact Builder examples]
        "Based on ADR 0010 and the ReversalImpactBuilder pattern..."
```

---

## Comparison: MCP Server vs Slack Bot

| Aspect | MCP Server | Slack Bot |
|--------|------------|-----------|
| **Runs where** | Your machine | Company server |
| **Accessible from** | Your Claude Desktop only | Anyone in Slack |
| **Use case** | Personal coding assistant | Team onboarding/questions |
| **Integration** | Deep (IDE-like) | Shallow (Q&A) |
| **Setup** | Each person installs | One shared instance |

**Use both!** They complement each other:
- Slack bot for quick questions
- MCP server for deep coding work

---

## Updating

When the MCP server is updated:

```bash
cd ~/ledger-bot-app
git pull
pip install -e .  # Update shared library
cd mcp-server
pip install -e .  # Update MCP server
# Restart Claude Desktop
```

---

## Getting Help

**Issues with installation:**
- Ask in #bor-write-eng
- DM Kayla

**Feature requests:**
- Create issue in repo
- Suggest in #bor-write-eng

**General MCP questions:**
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop docs](https://claude.ai/docs)

---

## Privacy & Security

**What stays local:**
- ✅ MCP server runs on YOUR machine
- ✅ Your oracle-gl-publisher repo never leaves your machine
- ✅ Claude Desktop connects via stdio (local process)

**What goes to Claude:**
- ⚠️ Tool results (ADR content, file contents, etc.)
- ⚠️ Your questions and Claude's responses

**Best practices:**
- Don't search for passwords/secrets with the tool
- Be aware tool results are sent to Claude API
- This is the same as pasting code into Claude manually

---

## What's Next?

This is **Phase 1** - static documentation tools.

**Phase 2** (coming soon):
- GraphQL API integration (query live activity status)
- Database access (check actual ledger state)
- Kafka monitoring (see what's in topics)

---

## Questions?

Reach out to:
- **Kayla** - Creator/maintainer
- **#bor-write-eng** - General questions
- **GitHub Issues** - Bug reports/feature requests
