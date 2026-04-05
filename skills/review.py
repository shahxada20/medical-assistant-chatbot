"""
Module for file system operations used by the Code Review Agent.
"""
import os
from typing import Optional


def get_file_content(file_path: str) -> Optional[str]:
    """
    Reads the content of a project file for analysis.

    Args:
        file_path (str): Relative path to the file.

    Returns:
        Optional[str]: Content of the file or error message if not found.
    """
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"System Error: {str(e)}"