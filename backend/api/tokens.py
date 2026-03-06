from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from graph import agent_manager
from graph.prompt_builder import build_system_prompt

router = APIRouter()


def _count_tokens(text: str) -> int:
    # Lightweight approximation for scaffold code.
    return max(1, len(text) // 4) if text else 0


class FilesTokenRequest(BaseModel):
    paths: list[str]


@router.get("/tokens/session/{session_id}")
def session_tokens(session_id: str) -> dict:
    if agent_manager.base_dir is None or agent_manager.session_manager is None:
        return {"system_tokens": 0, "message_tokens": 0, "total_tokens": 0}
    system = build_system_prompt(agent_manager.base_dir)
    history = agent_manager.session_manager.load_session(session_id)
    message_text = "\n".join(str(m.get("content", "")) for m in history)
    system_tokens = _count_tokens(system)
    message_tokens = _count_tokens(message_text)
    return {
        "system_tokens": system_tokens,
        "message_tokens": message_tokens,
        "total_tokens": system_tokens + message_tokens,
    }


@router.post("/tokens/files")
def file_tokens(body: FilesTokenRequest) -> dict:
    if agent_manager.base_dir is None:
        return {"counts": {}}
    counts = {}
    for rel in body.paths:
        path = (agent_manager.base_dir / rel).resolve()
        if path.exists() and path.is_file():
            counts[rel] = _count_tokens(path.read_text(encoding="utf-8", errors="ignore"))
    return {"counts": counts}
