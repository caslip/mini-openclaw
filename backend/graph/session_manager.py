from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class SessionManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.sessions_dir = base_dir / "sessions"
        self.archive_dir = self.sessions_dir / "archive"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def _read_file(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {
                "title": "新会话",
                "created_at": time.time(),
                "updated_at": time.time(),
                "messages": [],
            }

        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {
                "title": "已迁移会话",
                "created_at": time.time(),
                "updated_at": time.time(),
                "messages": data,
            }
        return data

    def _write_file(self, path: Path, data: dict[str, Any]) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_sessions(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for file in self.sessions_dir.glob("*.json"):
            data = self._read_file(file)
            results.append(
                {
                    "session_id": file.stem,
                    "title": data.get("title", file.stem),
                    "updated_at": data.get("updated_at", 0),
                    "created_at": data.get("created_at", 0),
                }
            )
        return sorted(results, key=lambda x: x["updated_at"], reverse=True)

    def load_session(self, session_id: str) -> list[dict[str, Any]]:
        return self._read_file(self._session_path(session_id)).get("messages", [])

    def load_session_for_agent(self, session_id: str) -> list[dict[str, Any]]:
        raw = self._read_file(self._session_path(session_id))
        messages = raw.get("messages", [])
        merged: list[dict[str, Any]] = []

        for msg in messages:
            if (
                merged
                and merged[-1].get("role") == "assistant"
                and msg.get("role") == "assistant"
            ):
                merged[-1]["content"] = (
                    f"{merged[-1].get('content', '')}\n\n{msg.get('content', '')}".strip()
                )
                if msg.get("tool_calls"):
                    merged[-1].setdefault("tool_calls", []).extend(msg["tool_calls"])
            else:
                merged.append(dict(msg))

        compressed = raw.get("compressed_context", "").strip()
        if compressed:
            merged.insert(
                0,
                {
                    "role": "assistant",
                    "content": f"[以下是之前对话的摘要]\n{compressed}",
                },
            )
        return merged

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> None:
        path = self._session_path(session_id)
        data = self._read_file(path)
        msg: dict[str, Any] = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        data.setdefault("messages", []).append(msg)
        data["updated_at"] = time.time()
        self._write_file(path, data)

    def create_session(self, session_id: str, title: str = "新会话") -> dict[str, Any]:
        now = time.time()
        payload = {
            "title": title,
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
        self._write_file(self._session_path(session_id), payload)
        return payload

    def rename_session(self, session_id: str, title: str) -> dict[str, Any]:
        path = self._session_path(session_id)
        data = self._read_file(path)
        data["title"] = title
        data["updated_at"] = time.time()
        self._write_file(path, data)
        return data

    def delete_session(self, session_id: str) -> None:
        path = self._session_path(session_id)
        if path.exists():
            path.unlink()

    def get_compressed_context(self, session_id: str) -> str:
        return str(self._read_file(self._session_path(session_id)).get("compressed_context", ""))

    def compress_history(self, session_id: str, summary: str, n: int) -> dict[str, Any]:
        path = self._session_path(session_id)
        data = self._read_file(path)
        messages = data.get("messages", [])
        archived = messages[:n]
        remaining = messages[n:]

        archive_name = f"{session_id}_{int(time.time())}.json"
        archive_path = self.archive_dir / archive_name
        archive_path.write_text(
            json.dumps({"messages": archived}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        previous = str(data.get("compressed_context", "")).strip()
        data["compressed_context"] = (
            f"{previous}\n\n---\n\n{summary}".strip() if previous else summary
        )
        data["messages"] = remaining
        data["updated_at"] = time.time()
        self._write_file(path, data)
        return {
            "archived_count": len(archived),
            "remaining_count": len(remaining),
            "archive_file": archive_name,
        }
