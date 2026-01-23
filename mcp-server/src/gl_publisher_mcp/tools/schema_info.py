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
