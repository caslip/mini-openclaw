from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from api import (
    chat_router,
    compress_router,
    config_router,
    files_router,
    sessions_router,
    tokens_router,
)
from graph import agent_manager, memory_indexer
from tools.skills_scanner import scan_skills


BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 1) 生成技能快照
    scan_skills(BASE_DIR)

    # 2) 初始化 AgentManager（LLM + tools + session manager）
    agent_manager.initialize(BASE_DIR, memory_indexer=memory_indexer)

    # 3) 构建 MEMORY 索引
    memory_indexer.rebuild_index()
    yield


app = FastAPI(title="Mini-OpenClaw Backend Scaffold", lifespan=lifespan)
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(sessions_router, prefix="/api", tags=["sessions"])
app.include_router(files_router, prefix="/api", tags=["files"])
app.include_router(tokens_router, prefix="/api", tags=["tokens"])
app.include_router(compress_router, prefix="/api", tags=["compress"])
app.include_router(config_router, prefix="/api", tags=["config"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
