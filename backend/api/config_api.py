from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from config import get_rag_mode, set_rag_mode

router = APIRouter()


class RagModePayload(BaseModel):
    enabled: bool


@router.get("/config/rag-mode")
def read_rag_mode() -> dict:
    return {"enabled": get_rag_mode()}


@router.put("/config/rag-mode")
def update_rag_mode(body: RagModePayload) -> dict:
    set_rag_mode(body.enabled)
    return {"enabled": body.enabled}
