from __future__ import annotations

import hashlib
from pathlib import Path


class MemoryIndexer:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.memory_path = base_dir / "memory" / "MEMORY.md"
        self.index_dir = base_dir / "storage" / "memory_index"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._last_md5 = ""

    def _calc_md5(self) -> str:
        if not self.memory_path.exists():
            return ""
        return hashlib.md5(self.memory_path.read_bytes()).hexdigest()

    def rebuild_index(self) -> None:
        self._last_md5 = self._calc_md5()
        (self.index_dir / "index.meta").write_text(self._last_md5, encoding="utf-8")

    def _maybe_rebuild(self) -> None:
        if self._calc_md5() != self._last_md5:
            self.rebuild_index()

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, str | float]]:
        self._maybe_rebuild()
        if not self.memory_path.exists():
            return []

        content = self.memory_path.read_text(encoding="utf-8")
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        matched = [c for c in chunks if query.lower() in c.lower()]
        selected = (matched or chunks)[:top_k]
        return [{"text": c, "score": 1.0, "source": str(self.memory_path)} for c in selected]


memory_indexer = MemoryIndexer(Path(__file__).resolve().parents[1])
