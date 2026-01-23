from pathlib import Path
from typing import Optional, List, Dict
import re

def find_impact_builders(query: Optional[str], gl_publisher_path: Path) -> List[Dict[str, str]]:
    """
    Find Impact Builder implementations in the repository.

    Args:
        query: Optional search term to filter builders
        gl_publisher_path: Path to oracle-gl-publisher repository

    Returns:
        List of dicts with builder information
    """
    ib_dir = gl_publisher_path / "queue-processor" / "src" / "main" / "kotlin" / "com" / "wealthsimple" / "oracleglpublisher" / "queueprocessor" / "glrecordbuilders"

    if not ib_dir.exists():
        return []

    results = []

    # Find all ImpactBuilder files recursively
    for kt_file in ib_dir.rglob("*ImpactBuilder.kt"):
        content = kt_file.read_text()

        # Extract class name
        class_match = re.search(r'class\s+(\w+ImpactBuilder)', content)
        if not class_match:
            continue

        class_name = class_match.group(1)

        # Extract acceptedType
        accepted_type_match = re.search(r'acceptedType.*?=\s*(\w+)::class', content, re.DOTALL)
        accepted_type = accepted_type_match.group(1) if accepted_type_match else "Unknown"

        # Filter by query if provided
        if query:
            query_lower = query.lower()
            if not (query_lower in class_name.lower() or query_lower in content.lower()):
                continue

        results.append({
            "name": class_name,
            "file": str(kt_file.relative_to(gl_publisher_path)),
            "accepted_type": accepted_type,
        })

    return sorted(results, key=lambda x: x["name"])
