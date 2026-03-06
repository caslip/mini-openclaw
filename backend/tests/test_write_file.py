from __future__ import annotations

from tools.write_file_tool import make_write_file_tool


def test_write_allowed_path(base_dir):
    tool = make_write_file_tool(base_dir)
    result = tool.run({"path": "workspace/test.md", "content": "# Test"})
    assert "saved" in result
    assert (base_dir / "workspace" / "test.md").read_text(encoding="utf-8") == "# Test"


def test_write_blocked_path(base_dir):
    tool = make_write_file_tool(base_dir)
    result = tool.run({"path": "src/main.py", "content": "evil"})
    assert "not in allowed" in result


def test_path_traversal_dotdot(base_dir):
    tool = make_write_file_tool(base_dir)
    result = tool.run({"path": "memory/../../etc/evil", "content": "evil"})
    assert "blocked" in result


def test_memory_md_triggers_logging(base_dir):
    tool = make_write_file_tool(base_dir)
    result = tool.run({"path": "memory/MEMORY.md", "content": "# 长期记忆\n- 测试偏好"})
    assert "updated and logged" in result

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = base_dir / "memory" / "logs" / f"{today}.md"
    assert log_file.exists(), f"Log file {log_file} was not created"
    log_content = log_file.read_text(encoding="utf-8")
    assert "MD5" in log_content or "修改" in log_content


def test_mkdir_parents(base_dir):
    tool = make_write_file_tool(base_dir)
    result = tool.run({"path": "knowledge/sub/deep/file.md", "content": "deep content"})
    assert "saved" in result
    assert (base_dir / "knowledge" / "sub" / "deep" / "file.md").exists()
