# GL Publisher MCP Server - Phase 1: Documentation & Knowledge

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an MCP server that provides Claude with tools to search, read, and query GL Publisher documentation, ADRs, schemas, and code examples.

**Architecture:** Python-based MCP server using the official Anthropic MCP SDK. Provides tools (callable functions) and resources (static content) that expose GL Publisher knowledge. Server runs locally and connects to Claude via stdio transport.

**Tech Stack:** Python 3.9+, MCP SDK (@modelcontextprotocol/sdk), oracle-gl-publisher repository access

---

## Phase 1 Scope

**Tools to implement:**
1. `search_adrs` - Search Architecture Decision Records by keyword
2. `read_file` - Read specific files from oracle-gl-publisher repo
3. `find_impact_builders` - List and search Impact Builder implementations
4. `get_schema_info` - Get Oracle GL schema table information
5. `search_code` - Search code patterns in the repository

**Resources to expose:**
1. List of all ADRs with summaries
2. README files from each module
3. Schema reference documentation

**Phase 2 (Future):**
- Live GraphQL API queries
- Database connections
- Kafka topic monitoring

---

## Prerequisites

- Python 3.9+ installed
- oracle-gl-publisher repository cloned at `~/IdeaProjects/oracle-gl-publisher`
- MCP SDK installed

---

## Task 1: Project Setup

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/pyproject.toml`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/README.md`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/__init__.py`

**Step 1: Create project structure**

```bash
cd /Users/kayla.lu/ledger-bot-app
mkdir -p mcp-server/src/gl_publisher_mcp
mkdir -p mcp-server/tests
touch mcp-server/src/gl_publisher_mcp/__init__.py
touch mcp-server/src/gl_publisher_mcp/server.py
touch mcp-server/tests/__init__.py
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "gl-publisher-mcp-server"
version = "0.1.0"
description = "MCP server for GL Publisher documentation and knowledge"
requires-python = ">=3.9"
dependencies = [
    "mcp>=0.9.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project.scripts]
gl-publisher-mcp = "gl_publisher_mcp.server:main"
```

**Step 3: Create README.md**

```markdown
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
```

**Step 4: Commit setup**

```bash
git add mcp-server/
git commit -m "chore: initialize MCP server project structure"
```

---

## Task 2: Basic MCP Server Scaffold

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/server.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_server.py`

**Step 1: Write test for server initialization**

```python
# tests/test_server.py
import pytest
from gl_publisher_mcp.server import GLPublisherMCPServer

def test_server_initialization():
    """Test that server initializes with correct name"""
    server = GLPublisherMCPServer()
    assert server.name == "gl-publisher"

@pytest.mark.asyncio
async def test_server_has_tools():
    """Test that server exposes expected tools"""
    server = GLPublisherMCPServer()
    tools = await server.list_tools()

    tool_names = [tool.name for tool in tools]
    assert "search_adrs" in tool_names
    assert "read_file" in tool_names
    assert "find_impact_builders" in tool_names
    assert "get_schema_info" in tool_names
    assert "search_code" in tool_names
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/kayla.lu/ledger-bot-app/mcp-server
pip install -e ".[dev]"
pytest tests/test_server.py -v
```

Expected: FAIL - module not found

**Step 3: Implement basic server scaffold**

```python
# src/gl_publisher_mcp/server.py
import os
from pathlib import Path
from typing import Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

class GLPublisherMCPServer:
    def __init__(self, gl_publisher_path: Optional[str] = None):
        self.name = "gl-publisher"
        self.gl_publisher_path = Path(
            gl_publisher_path or os.environ.get(
                "GL_PUBLISHER_PATH",
                str(Path.home() / "IdeaProjects" / "oracle-gl-publisher")
            )
        )
        self.server = Server(self.name)
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="search_adrs",
                    description="Search Architecture Decision Records by keyword",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="read_file",
                    description="Read a specific file from oracle-gl-publisher repo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Relative path from repo root"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                types.Tool(
                    name="find_impact_builders",
                    description="Find Impact Builder implementations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Optional search term"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_schema_info",
                    description="Get Oracle GL schema table information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "description": "Table name (GL_INTERFACE, GL_JE_BATCHES, etc.)"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="search_code",
                    description="Search code patterns in repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Search pattern or keyword"
                            },
                            "file_pattern": {
                                "type": "string",
                                "description": "Optional file pattern (e.g., '*.kt')"
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
            ]

    async def list_tools(self):
        """Wrapper to expose tools for testing"""
        handlers = self.server._request_handlers.get("tools/list", [])
        if handlers:
            return await handlers[0]()
        return []

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

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_server.py -v
```

Expected: PASS (both tests)

**Step 5: Commit**

```bash
git add src/ tests/
git commit -m "feat: add basic MCP server scaffold with tool definitions"
```

---

## Task 3: Implement search_adrs Tool

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/tools/adr_search.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_adr_search.py`

**Step 1: Write test for ADR search**

```python
# tests/test_adr_search.py
import pytest
from pathlib import Path
from gl_publisher_mcp.tools.adr_search import search_adrs

@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock GL Publisher directory structure"""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    # Create sample ADRs
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
    assert "Idempotency" in results[0]["title"]

def test_search_adrs_returns_all_when_no_query(mock_gl_publisher_path):
    """Test listing all ADRs when no query provided"""
    results = search_adrs(None, mock_gl_publisher_path)

    assert len(results) == 2

def test_search_adrs_case_insensitive(mock_gl_publisher_path):
    """Test search is case insensitive"""
    results = search_adrs("REVERSAL", mock_gl_publisher_path)

    assert len(results) == 1
    assert "0010" in results[0]["file"]
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_adr_search.py -v
```

Expected: FAIL - module not found

**Step 3: Implement ADR search functionality**

```python
# src/gl_publisher_mcp/tools/adr_search.py
from pathlib import Path
from typing import Optional, List, Dict
import re

def search_adrs(query: Optional[str], gl_publisher_path: Path) -> List[Dict[str, str]]:
    """
    Search Architecture Decision Records by keyword.

    Args:
        query: Search query (case insensitive). If None, returns all ADRs.
        gl_publisher_path: Path to oracle-gl-publisher repository

    Returns:
        List of dicts with 'file', 'title', and 'excerpt' keys
    """
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

        excerpt = ' '.join(excerpt_lines)[:200] + "..."

        results.append({
            "file": adr_file.name,
            "title": title,
            "excerpt": excerpt,
            "path": str(adr_file.relative_to(gl_publisher_path))
        })

    return results
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_adr_search.py -v
```

Expected: PASS (all 3 tests)

**Step 5: Integrate with MCP server**

Update `src/gl_publisher_mcp/server.py`:

```python
# Add import at top
from gl_publisher_mcp.tools.adr_search import search_adrs

# Add in _register_handlers method after list_tools:
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            if name == "search_adrs":
                query = arguments.get("query")
                results = search_adrs(query, self.gl_publisher_path)

                if not results:
                    return [types.TextContent(
                        type="text",
                        text="No ADRs found matching your query."
                    )]

                # Format results
                output = f"Found {len(results)} ADR(s):\n\n"
                for result in results:
                    output += f"**{result['file']}**: {result['title']}\n"
                    output += f"{result['excerpt']}\n"
                    output += f"Path: `{result['path']}`\n\n"

                return [types.TextContent(type="text", text=output)]

            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
```

**Step 6: Test end-to-end**

```bash
# Run the server
python -m gl_publisher_mcp.server
```

**Step 7: Commit**

```bash
git add src/ tests/
git commit -m "feat: implement search_adrs tool"
```

---

## Task 4: Implement read_file Tool

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/tools/file_reader.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_file_reader.py`

**Step 1: Write test for file reading**

```python
# tests/test_file_reader.py
import pytest
from pathlib import Path
from gl_publisher_mcp.tools.file_reader import read_file, FileReadError

@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock GL Publisher directory"""
    (tmp_path / "README.md").write_text("# Oracle GL Publisher\nMain readme")
    (tmp_path / "api" / "README.md").write_text("# API Module\nAPI docs")
    (tmp_path / "api").mkdir(exist_ok=True)
    return tmp_path

def test_read_file_success(mock_gl_publisher_path):
    """Test reading an existing file"""
    content = read_file("README.md", mock_gl_publisher_path)
    assert "Oracle GL Publisher" in content

def test_read_file_in_subdirectory(mock_gl_publisher_path):
    """Test reading file in subdirectory"""
    content = read_file("api/README.md", mock_gl_publisher_path)
    assert "API Module" in content

def test_read_file_not_found(mock_gl_publisher_path):
    """Test error when file doesn't exist"""
    with pytest.raises(FileReadError, match="File not found"):
        read_file("nonexistent.md", mock_gl_publisher_path)

def test_read_file_path_traversal_blocked(mock_gl_publisher_path):
    """Test that path traversal is blocked"""
    with pytest.raises(FileReadError, match="Invalid path"):
        read_file("../../etc/passwd", mock_gl_publisher_path)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_file_reader.py -v
```

Expected: FAIL - module not found

**Step 3: Implement file reader**

```python
# src/gl_publisher_mcp/tools/file_reader.py
from pathlib import Path
from typing import Union

class FileReadError(Exception):
    """Error reading file"""
    pass

def read_file(relative_path: str, gl_publisher_path: Path) -> str:
    """
    Read a file from the oracle-gl-publisher repository.

    Args:
        relative_path: Path relative to repository root
        gl_publisher_path: Path to oracle-gl-publisher repository

    Returns:
        File contents as string

    Raises:
        FileReadError: If file not found or path is invalid
    """
    # Resolve path and check it's within repo
    try:
        target_path = (gl_publisher_path / relative_path).resolve()

        # Security: ensure path is within repo
        if not str(target_path).startswith(str(gl_publisher_path.resolve())):
            raise FileReadError(f"Invalid path: {relative_path}")

        if not target_path.exists():
            raise FileReadError(f"File not found: {relative_path}")

        if not target_path.is_file():
            raise FileReadError(f"Path is not a file: {relative_path}")

        return target_path.read_text()

    except (ValueError, OSError) as e:
        raise FileReadError(f"Error reading file: {str(e)}")
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_file_reader.py -v
```

Expected: PASS (all 4 tests)

**Step 5: Integrate with MCP server**

Update the `call_tool` handler in `server.py`:

```python
# Add import
from gl_publisher_mcp.tools.file_reader import read_file, FileReadError

# Add to call_tool handler
            elif name == "read_file":
                path = arguments.get("path")
                try:
                    content = read_file(path, self.gl_publisher_path)
                    return [types.TextContent(
                        type="text",
                        text=f"# {path}\n\n```\n{content}\n```"
                    )]
                except FileReadError as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
                    )]
```

**Step 6: Commit**

```bash
git add src/ tests/
git commit -m "feat: implement read_file tool with security checks"
```

---

## Task 5: Implement find_impact_builders Tool

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/tools/impact_builder_finder.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_impact_builder_finder.py`

**Step 1: Write test for finding Impact Builders**

```python
# tests/test_impact_builder_finder.py
import pytest
from pathlib import Path
from gl_publisher_mcp.tools.impact_builder_finder import find_impact_builders

@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock Impact Builder structure"""
    ib_dir = tmp_path / "queue-processor" / "src" / "main" / "kotlin" / "com" / "wealthsimple" / "oracleglpublisher" / "queueprocessor" / "glrecordbuilders"
    ib_dir.mkdir(parents=True)

    # Create sample Impact Builders
    (ib_dir / "TradeBuyImpactBuilder.kt").write_text("""
package com.wealthsimple.oracleglpublisher.queueprocessor.glrecordbuilders

class TradeBuyImpactBuilder : ImpactBuilder {
    override fun acceptedType() = TradeBuy::class
    override fun invoke(activity: Activity): List<GlImpact> { ... }
}
""")

    (ib_dir / "CashDepositImpactBuilder.kt").write_text("""
package com.wealthsimple.oracleglpublisher.queueprocessor.glrecordbuilders

class CashDepositImpactBuilder : ImpactBuilder {
    override fun acceptedType() = CashDeposit::class
}
""")

    return tmp_path

def test_find_all_impact_builders(mock_gl_publisher_path):
    """Test finding all Impact Builders"""
    results = find_impact_builders(None, mock_gl_publisher_path)
    assert len(results) == 2

def test_find_impact_builders_by_query(mock_gl_publisher_path):
    """Test searching Impact Builders by keyword"""
    results = find_impact_builders("trade", mock_gl_publisher_path)
    assert len(results) == 1
    assert "TradeBuy" in results[0]["name"]

def test_impact_builder_includes_accepted_type(mock_gl_publisher_path):
    """Test that results include acceptedType info"""
    results = find_impact_builders("TradeBuy", mock_gl_publisher_path)
    assert results[0]["accepted_type"] == "TradeBuy"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_impact_builder_finder.py -v
```

Expected: FAIL

**Step 3: Implement Impact Builder finder**

```python
# src/gl_publisher_mcp/tools/impact_builder_finder.py
from pathlib import Path
from typing import Optional, List, Dict
import re

def find_impact_builders(query: Optional[str], gl_publisher_path: Path) -> List[Dict[str, str]]:
    """
    Find Impact Builder implementations in the repository.

    Args:
        query: Optional search term to filter builders
        gl_publisher_path: Path to oracle-gl-publisher repository

    Returns:
        List of dicts with builder information
    """
    ib_dir = gl_publisher_path / "queue-processor" / "src" / "main" / "kotlin" / "com" / "wealthsimple" / "oracleglpublisher" / "queueprocessor" / "glrecordbuilders"

    if not ib_dir.exists():
        return []

    results = []

    # Find all ImpactBuilder files recursively
    for kt_file in ib_dir.rglob("*ImpactBuilder.kt"):
        content = kt_file.read_text()

        # Extract class name
        class_match = re.search(r'class\s+(\w+ImpactBuilder)', content)
        if not class_match:
            continue

        class_name = class_match.group(1)

        # Extract acceptedType
        accepted_type_match = re.search(r'acceptedType.*?=\s*(\w+)::class', content, re.DOTALL)
        accepted_type = accepted_type_match.group(1) if accepted_type_match else "Unknown"

        # Filter by query if provided
        if query:
            query_lower = query.lower()
            if not (query_lower in class_name.lower() or query_lower in content.lower()):
                continue

        results.append({
            "name": class_name,
            "file": str(kt_file.relative_to(gl_publisher_path)),
            "accepted_type": accepted_type,
        })

    return sorted(results, key=lambda x: x["name"])
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_impact_builder_finder.py -v
```

Expected: PASS

**Step 5: Integrate with MCP server**

Update `call_tool` in `server.py`:

```python
# Add import
from gl_publisher_mcp.tools.impact_builder_finder import find_impact_builders

# Add to handler
            elif name == "find_impact_builders":
                query = arguments.get("query")
                results = find_impact_builders(query, self.gl_publisher_path)

                if not results:
                    return [types.TextContent(
                        type="text",
                        text="No Impact Builders found."
                    )]

                output = f"Found {len(results)} Impact Builder(s):\n\n"
                for result in results:
                    output += f"**{result['name']}**\n"
                    output += f"- Accepts: `{result['accepted_type']}`\n"
                    output += f"- File: `{result['file']}`\n\n"

                return [types.TextContent(type="text", text=output)]
```

**Step 6: Commit**

```bash
git add src/ tests/
git commit -m "feat: implement find_impact_builders tool"
```

---

## Task 6: Implement get_schema_info Tool

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/tools/schema_info.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_schema_info.py`

**Step 1: Write test for schema info**

```python
# tests/test_schema_info.py
import pytest
from pathlib import Path
from gl_publisher_mcp.tools.schema_info import get_schema_info

@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock schema reference doc"""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "oracle-gl-schema-reference.md").write_text("""
# Oracle GL Schema Reference

## GL_INTERFACE

The staging table for journal entries.

| Column | Type | Description |
|--------|------|-------------|
| group_id | INT | Group identifier |
| segment1 | VARCHAR | Company |

## GL_JE_BATCHES

Batch information.

| Column | Type | Description |
|--------|------|-------------|
| je_batch_id | BIGINT | Unique ID |
""")

    return tmp_path

def test_get_schema_info_for_table(mock_gl_publisher_path):
    """Test getting info for specific table"""
    info = get_schema_info("GL_INTERFACE", mock_gl_publisher_path)
    assert "staging table" in info.lower()
    assert "group_id" in info

def test_get_schema_info_case_insensitive(mock_gl_publisher_path):
    """Test table name is case insensitive"""
    info = get_schema_info("gl_interface", mock_gl_publisher_path)
    assert "staging table" in info.lower()

def test_get_schema_info_returns_all_if_no_table(mock_gl_publisher_path):
    """Test returns overview if no table specified"""
    info = get_schema_info(None, mock_gl_publisher_path)
    assert "GL_INTERFACE" in info
    assert "GL_JE_BATCHES" in info
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_schema_info.py -v
```

Expected: FAIL

**Step 3: Implement schema info tool**

```python
# src/gl_publisher_mcp/tools/schema_info.py
from pathlib import Path
from typing import Optional
import re

def get_schema_info(table: Optional[str], gl_publisher_path: Path) -> str:
    """
    Get Oracle GL schema information for a specific table.

    Args:
        table: Table name (GL_INTERFACE, GL_JE_BATCHES, etc.). If None, returns overview.
        gl_publisher_path: Path to oracle-gl-publisher repository

    Returns:
        Schema information as formatted text
    """
    schema_file = gl_publisher_path / "docs" / "oracle-gl-schema-reference.md"

    if not schema_file.exists():
        return "Schema reference documentation not found."

    content = schema_file.read_text()

    if not table:
        # Return overview with all table names
        table_matches = re.findall(r'^## (GL_\w+)', content, re.MULTILINE)
        overview = "# Oracle GL Schema Tables\n\n"
        overview += "Available tables:\n"
        for table_name in table_matches:
            overview += f"- {table_name}\n"
        overview += "\nUse get_schema_info with a specific table name for details."
        return overview

    # Find specific table section
    table_upper = table.upper()
    pattern = rf'^## {re.escape(table_upper)}.*?(?=^## |\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        return f"Table '{table}' not found in schema reference. Available tables: GL_INTERFACE, GL_JE_BATCHES, GL_JE_HEADERS, GL_JE_LINES, GL_CODE_COMBINATIONS"

    return match.group(0)
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_schema_info.py -v
```

Expected: PASS

**Step 5: Integrate with MCP server**

```python
# Add import
from gl_publisher_mcp.tools.schema_info import get_schema_info

# Add to handler
            elif name == "get_schema_info":
                table = arguments.get("table")
                info = get_schema_info(table, self.gl_publisher_path)
                return [types.TextContent(type="text", text=info)]
```

**Step 6: Commit**

```bash
git add src/ tests/
git commit -m "feat: implement get_schema_info tool"
```

---

## Task 7: Implement search_code Tool

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/tools/code_search.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_code_search.py`

**Step 1: Write test for code search**

```python
# tests/test_code_search.py
import pytest
from pathlib import Path
from gl_publisher_mcp.tools.code_search import search_code

@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock code structure"""
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "example.kt").write_text("""
class Example {
    fun processActivity(activity: Activity) {
        // Process the activity
    }
}
""")

    (src_dir / "another.kt").write_text("""
class Another {
    val data = "test data"
}
""")

    return tmp_path

def test_search_code_finds_matches(mock_gl_publisher_path):
    """Test searching for code pattern"""
    results = search_code("processActivity", mock_gl_publisher_path)
    assert len(results) > 0
    assert any("example.kt" in r["file"] for r in results)

def test_search_code_with_file_pattern(mock_gl_publisher_path):
    """Test filtering by file pattern"""
    results = search_code("class", mock_gl_publisher_path, file_pattern="*.kt")
    assert len(results) == 2

def test_search_code_shows_context(mock_gl_publisher_path):
    """Test that results include surrounding context"""
    results = search_code("processActivity", mock_gl_publisher_path)
    assert any("activity: Activity" in r["context"] for r in results)
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_code_search.py -v
```

Expected: FAIL

**Step 3: Implement code search**

```python
# src/gl_publisher_mcp/tools/code_search.py
from pathlib import Path
from typing import Optional, List, Dict
import re

def search_code(
    pattern: str,
    gl_publisher_path: Path,
    file_pattern: Optional[str] = None,
    max_results: int = 20
) -> List[Dict[str, str]]:
    """
    Search for code patterns in the repository.

    Args:
        pattern: Search pattern or keyword
        gl_publisher_path: Path to oracle-gl-publisher repository
        file_pattern: Optional file glob pattern (e.g., '*.kt')
        max_results: Maximum number of results to return

    Returns:
        List of matches with file, line number, and context
    """
    results = []

    # Determine which files to search
    if file_pattern:
        files = list(gl_publisher_path.rglob(file_pattern))
    else:
        # Default to common code files
        files = list(gl_publisher_path.rglob("*.kt"))
        files.extend(gl_publisher_path.rglob("*.java"))
        files.extend(gl_publisher_path.rglob("*.md"))

    # Filter out target directories and hidden files
    files = [f for f in files if '/target/' not in str(f) and '/.git/' not in str(f)]

    pattern_lower = pattern.lower()

    for file_path in files:
        if len(results) >= max_results:
            break

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                if pattern_lower in line.lower():
                    # Get surrounding context (2 lines before and after)
                    start = max(0, line_num - 3)
                    end = min(len(lines), line_num + 2)
                    context_lines = lines[start:end]

                    results.append({
                        "file": str(file_path.relative_to(gl_publisher_path)),
                        "line": line_num,
                        "match": line.strip(),
                        "context": '\n'.join(context_lines)
                    })

                    if len(results) >= max_results:
                        break
        except (UnicodeDecodeError, PermissionError):
            continue

    return results
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_code_search.py -v
```

Expected: PASS

**Step 5: Integrate with MCP server**

```python
# Add import
from gl_publisher_mcp.tools.code_search import search_code

# Add to handler
            elif name == "search_code":
                pattern = arguments.get("pattern")
                file_pattern = arguments.get("file_pattern")
                results = search_code(pattern, self.gl_publisher_path, file_pattern)

                if not results:
                    return [types.TextContent(
                        type="text",
                        text=f"No matches found for '{pattern}'."
                    )]

                output = f"Found {len(results)} match(es) for '{pattern}':\n\n"
                for result in results:
                    output += f"**{result['file']}:{result['line']}**\n"
                    output += f"```\n{result['context']}\n```\n\n"

                return [types.TextContent(type="text", text=output)]
```

**Step 6: Commit**

```bash
git add src/ tests/
git commit -m "feat: implement search_code tool"
```

---

## Task 8: Add Resources

**Files:**
- Modify: `/Users/kayla.lu/ledger-bot-app/mcp-server/src/gl_publisher_mcp/server.py`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_resources.py`

**Step 1: Write test for resources**

```python
# tests/test_resources.py
import pytest
from gl_publisher_mcp.server import GLPublisherMCPServer

@pytest.mark.asyncio
async def test_server_has_resources():
    """Test that server exposes resources"""
    server = GLPublisherMCPServer()
    resources = await server.list_resources()

    assert len(resources) > 0
    uris = [r.uri for r in resources]
    assert "adrs://list" in uris
    assert "docs://modules" in uris
    assert "schema://reference" in uris
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_resources.py -v
```

Expected: FAIL

**Step 3: Add resources to server**

Update `server.py` to add resources:

```python
# In _register_handlers method, add:

        @self.server.list_resources()
        async def list_resources() -> list[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="adrs://list",
                    name="Architecture Decision Records",
                    description="List of all ADRs in the repository",
                    mimeType="text/markdown"
                ),
                types.Resource(
                    uri="docs://modules",
                    name="Module Documentation",
                    description="README files from each module",
                    mimeType="text/markdown"
                ),
                types.Resource(
                    uri="schema://reference",
                    name="Schema Reference",
                    description="Oracle GL schema reference documentation",
                    mimeType="text/markdown"
                ),
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource"""
            if uri == "adrs://list":
                adr_dir = self.gl_publisher_path / "docs" / "adr"
                output = "# Architecture Decision Records\n\n"
                for adr_file in sorted(adr_dir.glob("*.md")):
                    if adr_file.name != "README.md":
                        output += f"- {adr_file.name}\n"
                return output

            elif uri == "docs://modules":
                modules = ["api", "queue-processor", "audit-status-processor", "db"]
                output = "# Module Documentation\n\n"
                for module in modules:
                    readme = self.gl_publisher_path / module / "README.md"
                    if readme.exists():
                        output += f"\n## {module}\n\n"
                        output += readme.read_text()
                        output += "\n---\n"
                return output

            elif uri == "schema://reference":
                schema_file = self.gl_publisher_path / "docs" / "oracle-gl-schema-reference.md"
                if schema_file.exists():
                    return schema_file.read_text()
                return "Schema reference not found."

            return f"Unknown resource: {uri}"

    async def list_resources(self):
        """Wrapper for testing"""
        handlers = self.server._request_handlers.get("resources/list", [])
        if handlers:
            return await handlers[0]()
        return []
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_resources.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/ tests/
git commit -m "feat: add MCP resources for ADRs, docs, and schema"
```

---

## Task 9: Integration Testing

**Files:**
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/tests/test_integration.py`

**Step 1: Write integration test**

```python
# tests/test_integration.py
import pytest
import asyncio
from pathlib import Path
from gl_publisher_mcp.server import GLPublisherMCPServer

@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow of using MCP server"""
    # Note: This requires actual oracle-gl-publisher repo
    gl_path = Path.home() / "IdeaProjects" / "oracle-gl-publisher"

    if not gl_path.exists():
        pytest.skip("oracle-gl-publisher repo not found")

    server = GLPublisherMCPServer(str(gl_path))

    # Test tools are available
    tools = await server.list_tools()
    assert len(tools) == 5

    # Test resources are available
    resources = await server.list_resources()
    assert len(resources) == 3

    print("✅ All tools and resources available")

@pytest.mark.asyncio
async def test_search_real_adrs():
    """Test searching actual ADRs"""
    gl_path = Path.home() / "IdeaProjects" / "oracle-gl-publisher"

    if not gl_path.exists():
        pytest.skip("oracle-gl-publisher repo not found")

    from gl_publisher_mcp.tools.adr_search import search_adrs
    results = search_adrs("idempotency", gl_path)

    assert len(results) > 0
    print(f"✅ Found {len(results)} ADRs about idempotency")
```

**Step 2: Run integration tests**

```bash
pytest tests/test_integration.py -v
```

Expected: PASS (if oracle-gl-publisher repo exists)

**Step 3: Commit**

```bash
git add tests/
git commit -m "test: add integration tests for MCP server"
```

---

## Task 10: Documentation & Claude Desktop Configuration

**Files:**
- Update: `/Users/kayla.lu/ledger-bot-app/mcp-server/README.md`
- Create: `/Users/kayla.lu/ledger-bot-app/mcp-server/docs/CLAUDE_DESKTOP_SETUP.md`

**Step 1: Create setup documentation**

```markdown
# Claude Desktop Setup for GL Publisher MCP Server

## Installation

1. Install the MCP server:

```bash
cd /Users/kayla.lu/ledger-bot-app/mcp-server
pip install -e .
```

2. Configure Claude Desktop:

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
- Verify Python and dependencies are installed
- Check Claude Desktop logs: `~/Library/Logs/Claude/`

**Tools not working:**
- Restart Claude Desktop
- Verify MCP server is installed: `python -m gl_publisher_mcp.server --help`
- Test server directly: `python -m gl_publisher_mcp.server`

**Performance issues:**
- Code search can be slow on large repos
- Use file_pattern to narrow searches
- Consider indexing for faster searches (Phase 2)
```

**Step 2: Update main README**

Update the README with complete usage examples and troubleshooting.

**Step 3: Commit**

```bash
git add README.md docs/
git commit -m "docs: add Claude Desktop setup guide"
```

---

## Task 11: Final Testing & Polish

**Step 1: Run all tests**

```bash
pytest tests/ -v --cov=gl_publisher_mcp
```

**Step 2: Test manually with Claude Desktop**

1. Configure Claude Desktop
2. Test each tool
3. Verify resources load correctly

**Step 3: Code formatting**

```bash
black src/ tests/
```

**Step 4: Final commit**

```bash
git add .
git commit -m "chore: code formatting and final polish"
```

---

## Success Criteria

✅ All tools implemented and tested
✅ All resources working
✅ Integration tests passing
✅ Documentation complete
✅ Working with Claude Desktop

## Next Steps (Phase 2)

After Phase 1 is complete and working:

1. **Live GraphQL Integration**
   - Add tool to query activity status
   - Reprocess failed activities
   - Check import status

2. **Performance Improvements**
   - Add caching for file reads
   - Index code for faster searches
   - Stream large responses

3. **Advanced Features**
   - Code analysis (find similar patterns)
   - Dependency graph visualization
   - Custom report generation

---

## Plan Complete

**Plan saved to:** `docs/plans/2026-01-23-gl-publisher-mcp-server.md`

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
