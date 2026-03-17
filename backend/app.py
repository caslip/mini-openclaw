from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import (
    chat_router,
    channels_router,
    compress_router,
    config_router,
    cron_router,
    evolution_router,
    files_router,
    heartbeat_router,
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

    # 4) 启动心跳机制
    from heartbeat import agent_heartbeat, diagnostic_heartbeat
    agent_heartbeat.start()
    diagnostic_heartbeat.start()

    # 5) 启动定时任务调度器
    from cron_scheduler import cron_scheduler
    from config import get_cron_config
    cron_config = get_cron_config()
    if cron_config.get("enabled", True):
        cron_scheduler.set_agent_callback(agent_manager.astream)
        # 设置会话投递回调，用于将提醒写入会话消息
        if agent_manager.session_manager:
            cron_scheduler.set_session_delivery_callback(
                lambda sid, msg: agent_manager.session_manager.save_message(sid, "assistant", msg)
            )
        cron_scheduler.start()

    # 6) 启动进化调度器
    from config import get_evolution_config
    from evolution.evolution_engine import evolution_engine
    evolution_config = get_evolution_config()
    if evolution_config.get("enabled", True):
        schedule_config = {
            "skill_discovery": {
                "enabled": evolution_config.get("skill_discovery", {}).get("enabled", True),
                "interval": 3600,
            },
            "prompt_evolution": {
                "enabled": evolution_config.get("prompt_evolution", {}).get("enabled", True),
                "interval": 86400,
            },
            "workflow_evolution": {
                "enabled": evolution_config.get("workflow_evolution", {}).get("enabled", True),
                "interval": 604800,
            },
        }
        evolution_engine.start_scheduler(schedule_config)

    yield

    # 6) 关闭心跳、定时任务和进化调度器
    agent_heartbeat.stop()
    diagnostic_heartbeat.stop()
    cron_scheduler.stop()
    evolution_engine.stop_scheduler()


app = FastAPI(title="Mini-OpenClaw Backend Scaffold", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(sessions_router, prefix="/api", tags=["sessions"])
app.include_router(files_router, prefix="/api", tags=["files"])
app.include_router(tokens_router, prefix="/api", tags=["tokens"])
app.include_router(compress_router, prefix="/api", tags=["compress"])
app.include_router(config_router, prefix="/api", tags=["config"])
app.include_router(heartbeat_router, prefix="/api", tags=["heartbeat"])
app.include_router(cron_router, prefix="/api", tags=["cron"])
app.include_router(channels_router, prefix="/api", tags=["channels"])
app.include_router(evolution_router, prefix="/api", tags=["evolution"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
