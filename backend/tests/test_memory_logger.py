from __future__ import annotations

from datetime import datetime

from graph.memory_logger import log_memory_change


def _today_log(base_dir) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = base_dir / "memory" / "logs" / f"{today}.md"
    return log_path.read_text(encoding="utf-8") if log_path.exists() else ""


def test_log_create(base_dir):
    log_memory_change(base_dir, old_md5="", new_md5="abc123", new_content="# new file")
    content = _today_log(base_dir)
    assert "create" in content


def test_log_update(base_dir):
    log_memory_change(base_dir, old_md5="prev456", new_md5="next789", new_content="# updated")
    content = _today_log(base_dir)
    assert "update" in content


def test_log_append(base_dir):
    log_memory_change(base_dir, old_md5="", new_md5="first", new_content="first write")
    log_memory_change(base_dir, old_md5="first", new_md5="second", new_content="second write")
    content = _today_log(base_dir)
    assert content.count("###") >= 2


def test_session_id_recorded(base_dir):
    session = "test-session-abc"
    log_memory_change(
        base_dir,
        old_md5="x",
        new_md5="y",
        new_content="content with session",
        session_id=session,
    )
    content = _today_log(base_dir)
    assert session in content


def test_log_contains_md5(base_dir):
    log_memory_change(
        base_dir, old_md5="old_hash_123", new_md5="new_hash_456", new_content="some content"
    )
    content = _today_log(base_dir)
    assert "old_hash_123" in content
    assert "new_hash_456" in content
