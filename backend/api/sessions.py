from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from graph import agent_manager

router = APIRouter()


class RenamePayload(BaseModel):
    title: str


@router.get("/sessions")
def list_sessions() -> list[dict]:
    if agent_manager.session_manager is None:
        return []
    return agent_manager.session_manager.list_sessions()


@router.post("/sessions")
def create_session() -> dict:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager is not initialized.")
    session_id = str(uuid.uuid4())
    payload = agent_manager.session_manager.create_session(session_id)
    return {"session_id": session_id, **payload}


@router.put("/sessions/{session_id}")
def rename_session(session_id: str, body: RenamePayload) -> dict:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager is not initialized.")
    return agent_manager.session_manager.rename_session(session_id, body.title)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str) -> dict:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager is not initialized.")
    agent_manager.session_manager.delete_session(session_id)
    return {"ok": True}


@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str) -> dict:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager is not initialized.")
    return {"messages": agent_manager.session_manager.load_session(session_id)}


@router.get("/sessions/{session_id}/history")
def get_history(session_id: str) -> dict:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager is not initialized.")
    return {"history": agent_manager.session_manager.load_session_for_agent(session_id)}


@router.post("/sessions/{session_id}/generate-title")
def generate_title(session_id: str) -> dict:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager is not initialized.")
    history = agent_manager.session_manager.load_session(session_id)
    if not history:
        return {"title": "新会话"}
    title = str(history[0].get("content", "新会话"))[:10]
    agent_manager.session_manager.rename_session(session_id, title)
    return {"title": title}
