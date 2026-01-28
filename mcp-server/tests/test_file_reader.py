import pytest
from pathlib import Path
from gl_publisher_mcp.tools.file_reader import read_file, FileReadError


@pytest.fixture
def mock_gl_publisher_path(tmp_path):
    """Create mock GL Publisher directory"""
    (tmp_path / "README.md").write_text("# Oracle GL Publisher\nMain readme")
    api_dir = tmp_path / "api"
    api_dir.mkdir()
    (api_dir / "README.md").write_text("# API Module\nAPI docs")
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
