from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import get_rag_mode
from graph import agent_manager, memory_indexer

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = True


def _format_sse(event_type: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/chat")
def chat(req: ChatRequest) -> StreamingResponse:
    if agent_manager.session_manager is None:
        raise HTTPException(status_code=500, detail="Agent manager not initialized.")

    history = agent_manager.session_manager.load_session_for_agent(req.session_id)

    def event_generator():
        if get_rag_mode() and memory_indexer is not None:
            retrievals = memory_indexer.retrieve(req.message, top_k=3)
            yield _format_sse("retrieval", {"query": req.message, "results": retrievals})

        chunks: list[str] = []
        for event in agent_manager.astream(req.message, history, session_id=req.session_id):
            etype = event.get("type", "token")

            if etype == "token":
                chunks.append(event.get("content", ""))
                yield _format_sse("token", {"content": event.get("content", "")})

            elif etype == "tool_start":
                yield _format_sse("tool_start", {
                    "tool": event.get("tool", ""),
                    "args": event.get("args", {}),
                })

            elif etype == "tool_end":
                yield _format_sse("tool_end", {
                    "tool": event.get("tool", ""),
                    "content": event.get("content", ""),
                })

            elif etype == "done":
                full_content = "".join(chunks).strip() or event.get("content", "")
                agent_manager.session_manager.save_message(req.session_id, "user", req.message)
                agent_manager.session_manager.save_message(req.session_id, "assistant", full_content)
                yield _format_sse("done", {"content": full_content, "session_id": req.session_id})

            else:
                yield _format_sse(etype, event)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
