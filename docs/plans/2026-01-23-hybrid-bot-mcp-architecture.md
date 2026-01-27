# Hybrid Slack Bot + MCP Server Architecture

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the Ledger Bot to have a shared knowledge layer that powers both the Slack bot (for teams) and an MCP server (for Claude Desktop personal use).

**Architecture:** Extract GL Publisher knowledge tools into a shared Python library. The Slack bot imports these tools and uses them with LiteLLM to answer questions. The MCP server exposes these same tools to Claude Desktop for use during coding.

**Tech Stack:** Python 3.9+, shared `gl_publisher_knowledge` library, Slack Bolt, MCP SDK, LiteLLM

---

## New Structure

```
ledger-bot-app/
├── gl_publisher_knowledge/          # NEW: Shared library
│   ├── __init__.py
│   ├── adr_search.py
│   ├── file_reader.py
│   ├── impact_builder_finder.py
│   ├── schema_info.py
│   └── code_search.py
├── slack-bot/                        # REFACTORED: Uses shared lib
│   ├── app.py
│   ├── requirements.txt
│   └── knowledge_base.txt            # Keep for additional context
├── mcp-server/                       # NEW: MCP interface
│   ├── src/gl_publisher_mcp/
│   │   └── server.py
│   ├── tests/
│   └── pyproject.toml
└── docs/
    └── plans/
```

---

## Task 1: Create Shared Knowledge Library

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/__init__.py`
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/config.py`
- Create: `/Users/kayla.lu/ledger-bot-app/setup.py`

**Step 1: Create library structure**

```bash
cd /Users/kayla.lu/ledger-bot-app
mkdir -p gl_publisher_knowledge
touch gl_publisher_knowledge/__init__.py
```

**Step 2: Create config.py**

```python
# gl_publisher_knowledge/config.py
import os
from pathlib import Path
from typing import Optional

def get_gl_publisher_path(path_override: Optional[str] = None) -> Path:
    """
    Get path to oracle-gl-publisher repository.

    Checks (in order):
    1. path_override parameter
    2. GL_PUBLISHER_PATH environment variable
    3. Default: ~/IdeaProjects/oracle-gl-publisher
    """
    if path_override:
        return Path(path_override)

    env_path = os.environ.get("GL_PUBLISHER_PATH")
    if env_path:
        return Path(env_path)

    return Path.home() / "IdeaProjects" / "oracle-gl-publisher"
```

**Step 3: Create setup.py for installable library**

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="gl-publisher-knowledge",
    version="0.1.0",
    description="Shared knowledge tools for GL Publisher documentation and code",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
)
```

**Step 4: Commit**

```bash
git add gl_publisher_knowledge/ setup.py
git commit -m "feat: create shared knowledge library structure"
```

---

## Task 2: Move ADR Search to Shared Library

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/adr_search.py`
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/tests/test_adr_search.py`

**Step 1: Copy and adapt adr_search implementation**

```python
# gl_publisher_knowledge/adr_search.py
from pathlib import Path
from typing import Optional, List, Dict
import re
from .config import get_gl_publisher_path

def search_adrs(
    query: Optional[str] = None,
    gl_publisher_path: Optional[Path] = None
) -> List[Dict[str, str]]:
    """
    Search Architecture Decision Records by keyword.

    Args:
        query: Search query (case insensitive). If None, returns all ADRs.
        gl_publisher_path: Optional path override

    Returns:
        List of dicts with 'file', 'title', 'excerpt', and 'path' keys
    """
    if gl_publisher_path is None:
        gl_publisher_path = get_gl_publisher_path()

    adr_dir = gl_publisher_path / "docs" / "adr"

    if not adr_dir.exists():
        return []

    results = []

    for adr_file in sorted(adr_dir.glob("*.md")):
        if adr_file.name == "README.md":
            continue

        content = adr_file.read_text()

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else adr_file.stem

        # If query provided, check if it matches
        if query:
            query_lower = query.lower()
            if not (query_lower in title.lower() or query_lower in content.lower()):
                continue

        # Extract excerpt (first 200 chars after title)
        lines = content.split('\n')
        excerpt_lines = []
        skip_title = True

        for line in lines:
            if skip_title and line.startswith('#'):
                skip_title = False
                continue
            if not skip_title and line.strip():
                excerpt_lines.append(line.strip())
                if len(' '.join(excerpt_lines)) > 200:
                    break

        excerpt = ' '.join(excerpt_lines)[:200]
        if len(excerpt) == 200:
            excerpt += "..."

        results.append({
            "file": adr_file.name,
            "title": title,
            "excerpt": excerpt,
            "path": str(adr_file.relative_to(gl_publisher_path))
        })

    return results

def format_adr_results(results: List[Dict[str, str]]) -> str:
    """Format ADR search results as markdown text"""
    if not results:
        return "No ADRs found matching your query."

    output = f"Found {len(results)} ADR(s):\n\n"
    for result in results:
        output += f"**{result['file']}**: {result['title']}\n"
        output += f"{result['excerpt']}\n"
        output += f"Path: `{result['path']}`\n\n"

    return output
```

**Step 2: Create tests**

```python
# gl_publisher_knowledge/tests/test_adr_search.py
import pytest
from pathlib import Path
from gl_publisher_knowledge.adr_search import search_adrs, format_adr_results

@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock GL Publisher directory structure"""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    (adr_dir / "0007-idempotency-key-meaning.md").write_text("""
# Idempotency Key Meaning
Idempotency key ensures exactly-once processing.
""")

    (adr_dir / "0010-Reversals-in-GL-Publisher.md").write_text("""
# Reversals in GL Publisher
How to reverse transactions.
""")

    return tmp_path

def test_search_adrs_finds_matching_files(mock_gl_publisher_path):
    """Test searching ADRs by keyword"""
    results = search_adrs("idempotency", mock_gl_publisher_path)
    assert len(results) == 1
    assert "0007" in results[0]["file"]

def test_format_adr_results():
    """Test formatting results"""
    results = [{"file": "0007.md", "title": "Test", "excerpt": "...", "path": "docs/adr/0007.md"}]
    output = format_adr_results(results)
    assert "Found 1 ADR" in output
```

**Step 3: Install library in development mode**

```bash
pip install -e .
pytest gl_publisher_knowledge/tests/test_adr_search.py -v
```

**Step 4: Commit**

```bash
git add gl_publisher_knowledge/
git commit -m "feat: add adr_search to shared library"
```

---

## Task 3: Add All Other Tools to Shared Library

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/file_reader.py`
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/impact_builder_finder.py`
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/schema_info.py`
- Create: `/Users/kayla.lu/ledger-bot-app/gl_publisher_knowledge/code_search.py`

**Step 1: Copy all tool implementations from the original MCP plan**

Copy the implementations from the previous plan for:
- `file_reader.py` (with `FileReadError` exception)
- `impact_builder_finder.py`
- `schema_info.py`
- `code_search.py`

Each should:
- Import `get_gl_publisher_path` from `config`
- Accept optional `gl_publisher_path` parameter
- Include a `format_*_results()` helper function

**Step 2: Create tests for each**

**Step 3: Run tests**

```bash
pytest gl_publisher_knowledge/tests/ -v
```

**Step 4: Commit**

```bash
git add gl_publisher_knowledge/
git commit -m "feat: add all knowledge tools to shared library"
```

---

## Task 4: Refactor Slack Bot to Use Shared Library

**Files:**
- Modify: `/Users/kayla.lu/ledger-bot-app/app.py`
- Modify: `/Users/kayla.lu/ledger-bot-app/requirements.txt`

**Step 1: Update requirements.txt**

```txt
slack-bolt
openai
python-dotenv
-e ../  # Install gl-publisher-knowledge in editable mode
```

**Step 2: Refactor app.py to use tool-calling pattern**

```python
# app.py
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from dotenv import load_dotenv

# Import shared knowledge tools
from gl_publisher_knowledge import adr_search, file_reader, impact_builder_finder, schema_info, code_search

load_dotenv()

def load_knowledge_base():
    """Load the knowledge base content from file"""
    knowledge_base_path = os.path.join(os.path.dirname(__file__), "knowledge_base.txt")
    try:
        with open(knowledge_base_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are Ledger Bot, an AI assistant for GL Publisher."

# Initialize Slack app
slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize LiteLLM client
llm_client = OpenAI(
    api_key=os.environ["LITELLM_DEVELOPER_KEY"],
    base_url="https://llm.ws2.staging.w10e.com/api/v2",
    default_headers={"X-LiteLLM-Dev-Key": os.environ["LITELLM_DEVELOPER_KEY"]}
)

# Load knowledge base
KNOWLEDGE_BASE = load_knowledge_base()

# Define tools for Claude
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_adrs",
            "description": "Search Architecture Decision Records by keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for ADRs"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_impact_builders",
            "description": "Find Impact Builder implementations",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional search term for Impact Builders"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_schema_info",
            "description": "Get Oracle GL schema table information",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Table name (GL_INTERFACE, GL_JE_BATCHES, etc.)"
                    }
                }
            }
        }
    }
]

def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a knowledge tool and return results"""
    if tool_name == "search_adrs":
        results = adr_search.search_adrs(arguments.get("query"))
        return adr_search.format_adr_results(results)

    elif tool_name == "find_impact_builders":
        results = impact_builder_finder.find_impact_builders(arguments.get("query"))
        return impact_builder_finder.format_impact_builder_results(results)

    elif tool_name == "get_schema_info":
        return schema_info.get_schema_info(arguments.get("table"))

    return f"Unknown tool: {tool_name}"

def handle_question(user_question: str) -> str:
    """Handle a question with tool-calling support"""
    messages = [
        {"role": "system", "content": KNOWLEDGE_BASE},
        {"role": "user", "content": user_question}
    ]

    # First call - let Claude decide if it needs tools
    response = llm_client.chat.completions.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=messages,
        tools=TOOLS
    )

    # Check if Claude wants to use tools
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls

        # Execute tools and add results to conversation
        messages.append(response.choices[0].message)

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = eval(tool_call.function.arguments)
            tool_result = execute_tool(tool_name, tool_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

        # Call again with tool results
        response = llm_client.chat.completions.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=messages
        )

    return response.choices[0].message.content

# Handle mentions
@slack_app.event("app_mention")
def handle_mention(event, say, client):
    user_question = event["text"]
    channel = event["channel"]
    ts = event["ts"]

    # Send immediate acknowledgment
    thinking_msg = client.chat_postMessage(
        channel=channel,
        thread_ts=ts,
        text=":hourglass_flowing_sand: Thinking..."
    )

    # Get answer (may use tools)
    answer = handle_question(user_question)

    # Update with actual response
    client.chat_update(
        channel=channel,
        ts=thinking_msg["ts"],
        text=answer
    )

# Handle direct messages
@slack_app.event("message")
def handle_message(event, say, client):
    if event.get("bot_id"):
        return

    user_question = event["text"]
    channel = event["channel"]

    thinking_msg = client.chat_postMessage(
        channel=channel,
        text=":hourglass_flowing_sand: Thinking..."
    )

    answer = handle_question(user_question)

    client.chat_update(
        channel=channel,
        ts=thinking_msg["ts"],
        text=answer
    )

if __name__ == "__main__":
    handler = SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"])
    print("⚡️ Ledger Bot is running in Socket Mode!")
    handler.start()
```

**Step 3: Test the refactored bot**

```bash
cd /Users/kayla.lu/ledger-bot-app
pip install -r requirements.txt
python app.py
```

**Step 4: Test in Slack**

Ask: "Search ADRs for idempotency"

Claude should call the `search_adrs` tool automatically!

**Step 5: Commit**

```bash
git add app.py requirements.txt
git commit -m "refactor: use shared knowledge library with tool calling"
```

---

## Task 5: Build MCP Server Using Shared Library

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/server.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/pyproject.toml`

**Step 1: Create MCP server that wraps shared tools**

```python
# mcp-server/src/gl_publisher_mcp/server.py
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Import shared knowledge tools
from gl_publisher_knowledge import adr_search, file_reader, impact_builder_finder, schema_info, code_search

class GLPublisherMCPServer:
    def __init__(self):
        self.name = "gl-publisher"
        self.server = Server(self.name)
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="search_adrs",
                    description="Search Architecture Decision Records by keyword",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="find_impact_builders",
                    description="Find Impact Builder implementations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Optional search term"}
                        }
                    }
                ),
                types.Tool(
                    name="get_schema_info",
                    description="Get Oracle GL schema table information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table": {"type": "string", "description": "Table name"}
                        }
                    }
                ),
                types.Tool(
                    name="read_file",
                    description="Read a file from oracle-gl-publisher repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Relative file path"}
                        },
                        "required": ["path"]
                    }
                ),
                types.Tool(
                    name="search_code",
                    description="Search code patterns in repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string", "description": "Search pattern"},
                            "file_pattern": {"type": "string", "description": "File glob pattern"}
                        },
                        "required": ["pattern"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls by delegating to shared library"""

            if name == "search_adrs":
                results = adr_search.search_adrs(arguments.get("query"))
                output = adr_search.format_adr_results(results)
                return [types.TextContent(type="text", text=output)]

            elif name == "find_impact_builders":
                results = impact_builder_finder.find_impact_builders(arguments.get("query"))
                output = impact_builder_finder.format_impact_builder_results(results)
                return [types.TextContent(type="text", text=output)]

            elif name == "get_schema_info":
                output = schema_info.get_schema_info(arguments.get("table"))
                return [types.TextContent(type="text", text=output)]

            elif name == "read_file":
                try:
                    content = file_reader.read_file(arguments.get("path"))
                    return [types.TextContent(type="text", text=f"```\n{content}\n```")]
                except file_reader.FileReadError as e:
                    return [types.TextContent(type="text", text=f"Error: {str(e)}")]

            elif name == "search_code":
                results = code_search.search_code(
                    arguments.get("pattern"),
                    file_pattern=arguments.get("file_pattern")
                )
                output = code_search.format_code_results(results)
                return [types.TextContent(type="text", text=output)]

            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main entry point for MCP server"""
    server = GLPublisherMCPServer()

    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            server.server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "gl-publisher-mcp-server"
version = "0.1.0"
description = "MCP server for GL Publisher using shared knowledge library"
requires-python = ">=3.9"
dependencies = [
    "mcp>=0.9.0",
    "gl-publisher-knowledge",
]

[project.scripts]
gl-publisher-mcp = "gl_publisher_mcp.server:main"
```

**Step 3: Install and test**

```bash
cd mcp-server
pip install -e .
python -m gl_publisher_mcp.server
```

**Step 4: Configure Claude Desktop**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

**Step 5: Test in Claude Desktop**

Restart Claude Desktop and try: "Use search_adrs to find ADRs about idempotency"

**Step 6: Commit**

```bash
git add mcp-server/
git commit -m "feat: create MCP server using shared knowledge library"
```

---

## Task 6: Documentation

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/README.md`
- Create: `/Users/kayla.lu/ledger-bot-app/docs/ARCHITECTURE.md`

**Step 1: Create main README**

```markdown
# Ledger Bot - Hybrid Slack Bot + MCP Server

AI assistant for GL Publisher using shared knowledge tools.

## Architecture

```
Shared Knowledge Library (gl_publisher_knowledge/)
├── adr_search.py
├── file_reader.py
├── impact_builder_finder.py
├── schema_info.py
└── code_search.py

Two Interfaces:
1. Slack Bot → LiteLLM → Teams (Remote)
2. MCP Server → Claude Desktop → Personal (Local)
```

## Setup

### 1. Install Shared Library

```bash
pip install -e .
```

### 2. Slack Bot (For Teams)

```bash
cd /Users/kayla.lu/ledger-bot-app
cp .env.example .env  # Configure tokens
python app.py
```

### 3. MCP Server (For Claude Desktop)

```bash
cd mcp-server
pip install -e .
```

Configure `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gl-publisher": {
      "command": "python",
      "args": ["-m", "gl_publisher_mcp.server"]
    }
  }
}
```

Restart Claude Desktop.

## Usage

### Slack Bot
Ask questions in Slack:
- "@ledgerbot What ADRs mention reversals?"
- "@ledgerbot Find Impact Builders for trades"
- "@ledgerbot Explain the GL_INTERFACE table"

### Claude Desktop
Use tools naturally:
- "Search ADRs about idempotency"
- "Find Impact Builders related to cash"
- "Read the file api/README.md"

Both interfaces have access to the same knowledge!

## Development

### Run Tests
```bash
pytest gl_publisher_knowledge/tests/ -v
```

### Add New Tool
1. Add to `gl_publisher_knowledge/`
2. Add tests
3. Update Slack bot's TOOLS list
4. Update MCP server's list_tools()
```

**Step 2: Create architecture doc**

Explain the design decisions and how both interfaces work.

**Step 3: Commit**

```bash
git add README.md docs/
git commit -m "docs: add architecture and usage documentation"
```

---

## Success Criteria

✅ Shared knowledge library with all tools
✅ Slack bot using tool calling with shared library
✅ MCP server exposing same tools to Claude Desktop
✅ Both interfaces tested and working
✅ Documentation complete

## Benefits Achieved

1. **DRY** - Single source of truth for GL Publisher knowledge
2. **Team Use** - Slack bot accessible to everyone
3. **Personal Use** - MCP server for deep coding integration
4. **Maintainable** - Update tools once, both interfaces benefit
5. **Testable** - Shared library has comprehensive tests

## Next Steps (Phase 2)

- Add GraphQL API integration to shared library
- Add caching layer for performance
- Add more sophisticated code analysis tools
- Deploy Slack bot to production infrastructure
