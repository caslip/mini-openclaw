from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from graph.memory_logger import log_memory_change

_ALLOWED_PREFIXES = ("memory/", "workspace/", "skills/", "knowledge/")


def make_write_file_tool(base_dir: Path, memory_indexer: Any = None, get_session_id=None):
    resolved_base = base_dir.resolve()

    @tool
    def write_file(path: str, content: str) -> str:
        """Write content to a file inside the project directory.
        Allowed paths must start with: memory/, workspace/, skills/, or knowledge/.
        Use this to update MEMORY.md with learned user preferences and decisions.
        
        Args:
            path: Relative file path from project root (e.g. 'memory/MEMORY.md')
            content: Full new content to write to the file
        """
        if ".." in path:
            return "write_file error: path traversal blocked."
        if not any(path.startswith(prefix) for prefix in _ALLOWED_PREFIXES):
            return f"write_file error: path not in allowed directories {_ALLOWED_PREFIXES}."

        target = (resolved_base / path).resolve()
        if not str(target).startswith(str(resolved_base)):
            return "write_file error: path traversal blocked."

        target.parent.mkdir(parents=True, exist_ok=True)

        if path == "memory/MEMORY.md":
            old_md5 = (
                hashlib.md5(target.read_bytes()).hexdigest() if target.exists() else ""
            )
            target.write_text(content, encoding="utf-8")
            new_md5 = hashlib.md5(target.read_bytes()).hexdigest()
            session_id = get_session_id() if callable(get_session_id) else ""
            log_memory_change(resolved_base, old_md5, new_md5, content, session_id)
            if memory_indexer is not None:
                memory_indexer.rebuild_index()
            return f"write_file: memory/MEMORY.md updated and logged (md5: {new_md5[:8]}…)."

        target.write_text(content, encoding="utf-8")
        return f"write_file: {path} saved ({len(content)} chars)."

    return write_file
