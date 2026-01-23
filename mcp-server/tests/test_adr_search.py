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
