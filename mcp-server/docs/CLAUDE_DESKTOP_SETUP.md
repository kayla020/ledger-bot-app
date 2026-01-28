# Claude Desktop Setup for GL Publisher MCP Server

## Installation

1. Install the MCP server:

```bash
cd /Users/kayla.lu/ledger-bot-app/mcp-server
/opt/homebrew/bin/python3.11 -m pip install -e . --user
```

2. Configure Claude Desktop:

The config file is already created at `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gl-publisher": {
      "command": "/opt/homebrew/bin/python3.11",
      "args": ["-m", "gl_publisher_mcp.server"],
      "cwd": "/Users/kayla.lu/ledger-bot-app/mcp-server",
      "env": {
        "GL_PUBLISHER_PATH": "/Users/kayla.lu/IdeaProjects/oracle-gl-publisher"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. Verify connection:
   - Look for the 🔌 icon in Claude Desktop
   - You should see "gl-publisher" connected
   - Try: "Use the search_adrs tool to find ADRs about idempotency"

## Available Tools

### search_adrs
Search Architecture Decision Records by keyword.

**Example:** "Search ADRs for 'reversal'"

### read_file
Read specific files from the repository.

**Example:** "Read the file api/README.md"

### find_impact_builders
Find Impact Builder implementations.

**Example:** "Find all Impact Builders related to trades"

### get_schema_info
Get Oracle GL schema table information.

**Example:** "Show me the schema for GL_INTERFACE table"

### search_code
Search code patterns in the repository.

**Example:** "Search for 'processActivity' in Kotlin files"

## Available Resources

### adrs://list
List of all Architecture Decision Records

### docs://modules
Documentation from each module (api, queue-processor, etc.)

### schema://reference
Complete Oracle GL schema reference documentation

## Troubleshooting

**Server not connecting:**
- Check the path to oracle-gl-publisher is correct
- Verify Python 3.11 and dependencies are installed
- Check Claude Desktop logs: `~/Library/Logs/Claude/`

**Tools not working:**
- Restart Claude Desktop
- Verify MCP server is installed: `/opt/homebrew/bin/python3.11 -m gl_publisher_mcp.server --help`
- Test server directly: `/opt/homebrew/bin/python3.11 -m gl_publisher_mcp.server`

**Performance issues:**
- Code search can be slow on large repos
- Use file_pattern to narrow searches
- Consider indexing for faster searches (Phase 2)

## Running Tests

```bash
cd /Users/kayla.lu/ledger-bot-app/mcp-server
/opt/homebrew/bin/python3.11 -m pytest tests/ -v
```

All tests should pass:
- Unit tests for each tool
- Integration tests with actual oracle-gl-publisher repo
- Server initialization tests
