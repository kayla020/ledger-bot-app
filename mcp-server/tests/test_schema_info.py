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
