from __future__ import annotations

from tools.read_file_tool import make_read_file_tool


def test_read_existing(base_dir):
    (base_dir / "workspace" / "hello.txt").write_text("hello world", encoding="utf-8")
    tool = make_read_file_tool(base_dir)
    result = tool.run("workspace/hello.txt")
    assert result == "hello world"


def test_file_not_found(base_dir):
    tool = make_read_file_tool(base_dir)
    result = tool.run("workspace/nonexistent.txt")
    assert "file not found" in result


def test_path_traversal(base_dir):
    tool = make_read_file_tool(base_dir)
    result = tool.run("../../etc/passwd")
    assert "path traversal blocked" in result


def test_truncation(base_dir):
    long_content = "a" * 20000
    (base_dir / "workspace" / "big.txt").write_text(long_content, encoding="utf-8")
    tool = make_read_file_tool(base_dir)
    result = tool.run("workspace/big.txt")
    assert len(result) == 10000
