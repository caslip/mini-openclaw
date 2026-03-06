from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from graph import memory_indexer
from graph.memory_logger import log_memory_change

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
ALLOWED_PREFIXES = ("workspace/", "memory/", "skills/", "knowledge/")
ALLOWED_FILES = {"SKILLS_SNAPSHOT.md"}


class SaveFileRequest(BaseModel):
    path: str
    content: str


def _resolve_safe(path_str: str) -> Path:
    if ".." in path_str:
        raise HTTPException(status_code=400, detail="Path traversal is not allowed.")
    if path_str not in ALLOWED_FILES and not any(path_str.startswith(p) for p in ALLOWED_PREFIXES):
        raise HTTPException(status_code=400, detail="Path is not in whitelist.")
    target = (BASE_DIR / path_str).resolve()
    if not str(target).startswith(str(BASE_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Path escapes base directory.")
    return target


@router.get("/files")
def read_file(path: str = Query(...)) -> dict:
    target = _resolve_safe(path)
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return {"path": path, "content": target.read_text(encoding="utf-8")}


@router.post("/files")
def save_file(req: SaveFileRequest) -> dict:
    target = _resolve_safe(req.path)
    target.parent.mkdir(parents=True, exist_ok=True)

    if req.path == "memory/MEMORY.md":
        old_md5 = (
            hashlib.md5(target.read_bytes()).hexdigest() if target.exists() else ""
        )
        target.write_text(req.content, encoding="utf-8")
        new_md5 = hashlib.md5(target.read_bytes()).hexdigest()
        log_memory_change(BASE_DIR, old_md5, new_md5, req.content)
        if memory_indexer is not None:
            memory_indexer.rebuild_index()
    else:
        target.write_text(req.content, encoding="utf-8")

    return {"ok": True, "path": req.path}


@router.get("/skills")
def list_skills() -> dict:
    skills_dir = BASE_DIR / "skills"
    skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
    return {"skills": sorted(skills)}
