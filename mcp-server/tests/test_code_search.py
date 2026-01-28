import pytest
from pathlib import Path
from gl_publisher_mcp.tools.code_search import search_code


@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock code structure"""
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "example.kt").write_text(
        """
class Example {
    fun processActivity(activity: Activity) {
        // Process the activity
    }
}
"""
    )

    (src_dir / "another.kt").write_text(
        """
class Another {
    val data = "test data"
}
"""
    )

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
