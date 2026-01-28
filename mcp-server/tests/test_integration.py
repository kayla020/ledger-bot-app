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
