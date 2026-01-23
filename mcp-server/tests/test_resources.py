import pytest
from gl_publisher_mcp.server import GLPublisherMCPServer


@pytest.mark.asyncio
async def test_server_has_resources():
    """Test that server exposes resources"""
    server = GLPublisherMCPServer()
    resources = await server.list_resources()

    assert len(resources) > 0
    uris = [str(r.uri) for r in resources]
    assert "adrs://list" in uris
    assert "docs://modules" in uris
    assert "schema://reference" in uris
