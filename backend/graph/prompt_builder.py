from __future__ import annotations

from datetime import datetime
from pathlib import Path

MAX_COMPONENT_CHARS = 20_000


def _read_limited(path: Path) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8")
    if len(content) > MAX_COMPONENT_CHARS:
        return content[:MAX_COMPONENT_CHARS] + "\n...[truncated]"
    return content


def build_system_prompt(base_dir: Path, rag_mode: bool = False) -> str:
    components: list[tuple[str, Path]] = [
        ("Skills Snapshot", base_dir / "SKILLS_SNAPSHOT.md"),
        ("Soul", base_dir / "workspace" / "SOUL.md"),
        ("Identity", base_dir / "workspace" / "IDENTITY.md"),
        ("User Profile", base_dir / "workspace" / "USER.md"),
        ("Agents Guide", base_dir / "workspace" / "AGENTS.md"),
    ]

    if not rag_mode:
        components.append(("Long-term Memory", base_dir / "memory" / "MEMORY.md"))

    now = datetime.now()
    date_block = f"<!-- System Info -->\n当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}（UTC+8）"

    blocks = [date_block]
    blocks += [f"<!-- {name} -->\n{_read_limited(path)}" for name, path in components]
    if rag_mode:
        blocks.append(
            "<!-- Long-term Memory -->\n"
            "当前为 RAG 模式：长期记忆会通过检索结果在请求时动态注入，而非直接拼接 MEMORY.md 全文。"
        )
    return "\n\n".join(blocks).strip()
