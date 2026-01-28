from pathlib import Path
from typing import Optional, List, Dict
import re


def search_code(
    pattern: str,
    gl_publisher_path: Path,
    file_pattern: Optional[str] = None,
    max_results: int = 20,
) -> List[Dict[str, str]]:
    """
    Search for code patterns in the repository.

    Args:
        pattern: Search pattern or keyword
        gl_publisher_path: Path to oracle-gl-publisher repository
        file_pattern: Optional file glob pattern (e.g., '*.kt')
        max_results: Maximum number of results to return

    Returns:
        List of matches with file, line number, and context
    """
    results = []

    # Determine which files to search
    if file_pattern:
        files = list(gl_publisher_path.rglob(file_pattern))
    else:
        # Default to common code files
        files = list(gl_publisher_path.rglob("*.kt"))
        files.extend(gl_publisher_path.rglob("*.java"))
        files.extend(gl_publisher_path.rglob("*.md"))

    # Filter out target directories and hidden files
    files = [f for f in files if "/target/" not in str(f) and "/.git/" not in str(f)]

    pattern_lower = pattern.lower()

    for file_path in files:
        if len(results) >= max_results:
            break

        try:
            content = file_path.read_text()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                if pattern_lower in line.lower():
                    # Get surrounding context (2 lines before and after)
                    start = max(0, line_num - 3)
                    end = min(len(lines), line_num + 2)
                    context_lines = lines[start:end]

                    results.append(
                        {
                            "file": str(file_path.relative_to(gl_publisher_path)),
                            "line": line_num,
                            "match": line.strip(),
                            "context": "\n".join(context_lines),
                        }
                    )

                    if len(results) >= max_results:
                        break
        except (UnicodeDecodeError, PermissionError):
            continue

    return results
