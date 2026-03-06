from __future__ import annotations

from fastapi import APIRouter, HTTPException

from graph import agent_manager

router = APIRouter()


@router.post("/sessions/{session_id}/compress")
def compress_history(session_id: str) -> dict:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager is not initialized.")

    messages = agent_manager.session_manager.load_session(session_id)
    if len(messages) < 4:
        raise HTTPException(status_code=400, detail="At least 4 messages are required.")

    n = max(4, len(messages) // 2)
    source = messages[:n]
    joined = "\n".join(f"{m.get('role')}: {m.get('content', '')}" for m in source)
    summary = joined[:500] if joined else "无可压缩内容。"
    return agent_manager.session_manager.compress_history(session_id, summary, n)
