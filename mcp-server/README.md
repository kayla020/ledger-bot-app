# GL Publisher MCP Server

Model Context Protocol server for GL Publisher documentation and knowledge.

## Installation

```bash
pip install -e .
```

## Usage

### As MCP Server

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gl-publisher": {
      "command": "python",
      "args": ["-m", "gl_publisher_mcp.server"],
      "env": {
        "GL_PUBLISHER_PATH": "/Users/kayla.lu/IdeaProjects/oracle-gl-publisher"
      }
    }
  }
}
```

### Testing

```bash
pytest tests/
```

## Tools

- `search_adrs` - Search Architecture Decision Records
- `read_file` - Read files from oracle-gl-publisher repo
- `find_impact_builders` - Find Impact Builder implementations
- `get_schema_info` - Get Oracle GL schema information
- `search_code` - Search code patterns

## Resources

- `adrs://list` - List all ADRs
- `docs://modules` - Module documentation
- `schema://reference` - Schema reference docs
