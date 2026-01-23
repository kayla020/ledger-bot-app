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
