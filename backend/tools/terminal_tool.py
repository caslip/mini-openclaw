from __future__ import annotations

from pathlib import Path
from subprocess import PIPE, STDOUT, run as _run

from langchain_core.tools import tool

_BLOCKED = ("rm -rf /", "mkfs", "shutdown")


def make_terminal_tool(base_dir: Path):
    @tool
    def terminal(command: str) -> str:
        """Execute a shell command in the project sandbox. Blocked commands: rm -rf /, mkfs, shutdown."""
        if any(b in command for b in _BLOCKED):
            return "Blocked command by safety policy."
        try:
            proc = _run(
                command,
                shell=True,
                cwd=base_dir,
                stdout=PIPE,
                stderr=STDOUT,
                text=True,
                timeout=30,
            )
            return (proc.stdout or "")[:5000]
        except Exception as exc:
            return f"terminal error: {exc}"

    return terminal
