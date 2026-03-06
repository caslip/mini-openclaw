from __future__ import annotations

from pathlib import Path
from typing import Any

from .fetch_url_tool import make_fetch_url_tool
from .list_data_files_tool import make_list_data_files_tool
from .python_repl_tool import make_python_repl_tool
from .read_file_tool import make_read_file_tool
from .search_knowledge_tool import make_search_knowledge_tool
from .terminal_tool import make_terminal_tool
from .write_file_tool import make_write_file_tool


def get_all_tools(
    base_dir: Path,
    memory_indexer: Any = None,
    get_session_id=None,
) -> list:
    return [
        make_terminal_tool(base_dir),
        make_python_repl_tool(base_dir),
        make_fetch_url_tool(base_dir),
        make_read_file_tool(base_dir),
        make_search_knowledge_tool(base_dir),
        make_write_file_tool(base_dir, memory_indexer, get_session_id),
        make_list_data_files_tool(base_dir),
    ]
