from __future__ import annotations

import sys

from tools.terminal_tool import make_terminal_tool


def test_echo(base_dir):
    tool = make_terminal_tool(base_dir)
    result = tool.run("echo hello")
    assert "hello" in result


def test_blocked_command(base_dir):
    tool = make_terminal_tool(base_dir)
    result = tool.run("rm -rf /")
    assert "Blocked" in result


def test_blocked_mkfs(base_dir):
    tool = make_terminal_tool(base_dir)
    result = tool.run("mkfs /dev/sda")
    assert "Blocked" in result


def test_nonexistent_command(base_dir):
    tool = make_terminal_tool(base_dir)
    result = tool.run("nonexistent_command_xyz_123")
    # On error the tool returns stdout/stderr (which may include "not found") or empty
    assert isinstance(result, str)


def test_cwd_is_base_dir(base_dir):
    tool = make_terminal_tool(base_dir)
    if sys.platform == "win32":
        result = tool.run("cd")
    else:
        result = tool.run("pwd")
    assert str(base_dir).lower() in result.lower()
