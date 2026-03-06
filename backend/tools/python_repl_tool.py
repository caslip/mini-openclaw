from __future__ import annotations

from pathlib import Path

from langchain_experimental.tools.python.tool import PythonAstREPLTool


def make_python_repl_tool(base_dir: Path) -> PythonAstREPLTool:
    return PythonAstREPLTool(
        globals={"__builtins__": __builtins__},
        locals={},
        sanitize_input=True,
    )
