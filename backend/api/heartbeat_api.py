from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from config import get_heartbeat_config, set_heartbeat_config
from heartbeat import agent_heartbeat, diagnostic_heartbeat

router = APIRouter()


@router.get("/heartbeat/status")
def get_heartbeat_status() -> dict[str, Any]:
    """获取心跳状态"""
    return {
        "agent_heartbeat": {
            "running": agent_heartbeat.is_running(),
            "last_run": agent_heartbeat.get_last_run_time(),
            "interval": agent_heartbeat._interval,
        },
        "diagnostic_heartbeat": {
            "running": diagnostic_heartbeat.is_running(),
            "last_metrics": diagnostic_heartbeat.get_last_metrics(),
        },
        "config": get_heartbeat_config(),
    }


@router.post("/heartbeat/trigger")
def trigger_heartbeat() -> dict[str, Any]:
    """手动触发Agent心跳"""
    result = agent_heartbeat.trigger()
    if result is None:
        raise HTTPException(status_code=400, detail="Agent心跳未启动")
    return result


@router.post("/heartbeat/config")
def update_heartbeat_config(config: dict[str, Any]) -> dict[str, Any]:
    """更新心跳配置"""
    new_config = set_heartbeat_config(config)
    return {"status": "ok", "config": new_config}


@router.get("/heartbeat/metrics")
def get_heartbeat_metrics() -> dict[str, Any]:
    """获取最新的诊断指标"""
    return diagnostic_heartbeat.get_last_metrics()
