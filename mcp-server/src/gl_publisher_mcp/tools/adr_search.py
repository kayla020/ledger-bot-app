from pathlib import Path
from typing import Optional, List, Dict
import re

def search_adrs(query: Optional[str], gl_publisher_path: Path) -> List[Dict[str, str]]:
    """
    Search Architecture Decision Records by keyword.

    Args:
        query: Search query (case insensitive). If None, returns all ADRs.
        gl_publisher_path: Path to oracle-gl-publisher repository

    Returns:
        List of dicts with 'file', 'title', and 'excerpt' keys
    """
    adr_dir = gl_publisher_path / "docs" / "adr"

    if not adr_dir.exists():
        return []

    results = []

    for adr_file in sorted(adr_dir.glob("*.md")):
        if adr_file.name == "README.md":
            continue

        content = adr_file.read_text()

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else adr_file.stem

        # If query provided, check if it matches
        if query:
            query_lower = query.lower()
            if not (query_lower in title.lower() or query_lower in content.lower()):
                continue

        # Extract excerpt (first 200 chars after title)
        lines = content.split('\n')
        excerpt_lines = []
        skip_title = True

        for line in lines:
            if skip_title and line.startswith('#'):
                skip_title = False
                continue
            if not skip_title and line.strip():
                excerpt_lines.append(line.strip())
                if len(' '.join(excerpt_lines)) > 200:
                    break

        excerpt = ' '.join(excerpt_lines)[:200] + "..."

        results.append({
            "file": adr_file.name,
            "title": title,
            "excerpt": excerpt,
            "path": str(adr_file.relative_to(gl_publisher_path))
        })

    return results
