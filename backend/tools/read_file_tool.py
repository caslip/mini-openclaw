from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool


def make_read_file_tool(base_dir: Path):
    resolved_base = base_dir.resolve()

    @tool
    def read_file(path: str) -> str:
        """Read the content of a file inside the project directory. Path must be relative to the project root."""
        target = (resolved_base / path).resolve()
        if not str(target).startswith(str(resolved_base)):
            return "read_file error: path traversal blocked."
        if not target.exists():
            return "read_file error: file not found."
        return target.read_text(encoding="utf-8")[:10000]

    return read_file
