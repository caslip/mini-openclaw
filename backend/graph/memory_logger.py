from __future__ import annotations

from datetime import datetime
from pathlib import Path


def log_memory_change(
    base_dir: Path,
    old_md5: str,
    new_md5: str,
    new_content: str,
    session_id: str = "",
) -> None:
    """Append one record to memory/logs/YYYY-MM-DD.md for every MEMORY.md write."""
    logs_dir = base_dir / "memory" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    log_path = logs_dir / f"{now.strftime('%Y-%m-%d')}.md"

    operation = "create" if not old_md5 else "update"
    snippet = new_content.replace("\n", " ").strip()[:200]
    session_label = session_id if session_id else "—"

    entry = (
        f"\n### {now.strftime('%H:%M:%S')} | session: {session_label}\n"
        f"- **操作**: {operation}\n"
        f"- **变更摘要**: {snippet}\n"
        f"- **修改前 MD5**: {old_md5 or '（文件不存在）'}\n"
        f"- **修改后 MD5**: {new_md5}\n"
    )

    is_new_file = not log_path.exists() or log_path.stat().st_size == 0
    with log_path.open("a", encoding="utf-8") as f:
        if is_new_file:
            f.write(f"# Memory 变更日志 {now.strftime('%Y-%m-%d')}\n")
        f.write(entry)
