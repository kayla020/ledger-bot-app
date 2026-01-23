import os
from pathlib import Path
from typing import Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from gl_publisher_mcp.tools.adr_search import search_adrs
from gl_publisher_mcp.tools.file_reader import read_file, FileReadError

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
        async def list_tools_handler() -> list[types.Tool]:
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

        # Store handler for testing
        self._list_tools_handler = list_tools_handler

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

            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    async def list_tools(self):
        """Wrapper to expose tools for testing"""
        return await self._list_tools_handler()

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
