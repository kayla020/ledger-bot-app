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
