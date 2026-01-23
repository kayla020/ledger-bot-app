from pathlib import Path
from typing import Union

class FileReadError(Exception):
    """Error reading file"""
    pass

def read_file(relative_path: str, gl_publisher_path: Path) -> str:
    """
    Read a file from the oracle-gl-publisher repository.

    Args:
        relative_path: Path relative to repository root
        gl_publisher_path: Path to oracle-gl-publisher repository

    Returns:
        File contents as string

    Raises:
        FileReadError: If file not found or path is invalid
    """
    # Resolve path and check it's within repo
    try:
        target_path = (gl_publisher_path / relative_path).resolve()

        # Security: ensure path is within repo
        if not str(target_path).startswith(str(gl_publisher_path.resolve())):
            raise FileReadError(f"Invalid path: {relative_path}")

        if not target_path.exists():
            raise FileReadError(f"File not found: {relative_path}")

        if not target_path.is_file():
            raise FileReadError(f"Path is not a file: {relative_path}")

        return target_path.read_text()

    except (ValueError, OSError) as e:
        raise FileReadError(f"Error reading file: {str(e)}")
