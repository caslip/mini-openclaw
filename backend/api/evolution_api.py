from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from evolution.evolution_engine import evolution_engine

router = APIRouter(prefix="/evolution", tags=["evolution"])


class SkillDiscoveryRequest(BaseModel):
    watch: bool = False


class PromptAnalyzeRequest(BaseModel):
    limit: int = 100


class WorkflowAnalyzeRequest(BaseModel):
    limit: int = 50


class AutoEvolveRequest(BaseModel):
    mode: str = "all"


class ScheduleConfigRequest(BaseModel):
    skill_discovery: dict | None = None
    prompt_evolution: dict | None = None
    workflow_evolution: dict | None = None


@router.post("/skills/discover")
async def discover_skills(request: SkillDiscoveryRequest):
    """触发技能发现"""
    try:
        if request.watch:
            evolution_engine.skill_discovery.watch_for_changes()
            return {"status": "ok", "message": "技能监听已启动"}

        result = evolution_engine.run_skill_discovery()
        return {"status": "ok", "result": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills/summary")
async def get_skills_summary():
    """获取技能摘要"""
    try:
        summary = evolution_engine.skill_discovery.get_skills_summary()
        return {"status": "ok", "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompt/analyze")
async def analyze_prompt(request: PromptAnalyzeRequest):
    """分析并优化Prompt"""
    try:
        result = evolution_engine.run_prompt_evolution()
        return {"status": "ok", "result": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt/summary")
async def get_prompt_summary():
    """获取Prompt优化摘要"""
    try:
        summary = evolution_engine.prompt_optimizer.get_optimization_summary()
        return {"status": "ok", "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/analyze")
async def analyze_workflow(request: WorkflowAnalyzeRequest):
    """分析工作流"""
    try:
        result = evolution_engine.run_workflow_evolution()
        return {"status": "ok", "result": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/summary")
async def get_workflow_summary():
    """获取工作流摘要"""
    try:
        summary = evolution_engine.workflow_logger.get_workflow_summary()
        return {"status": "ok", "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/executions")
async def list_workflow_executions(limit: int = 20):
    """列出工作流执行记录"""
    try:
        executions = evolution_engine.workflow_logger.list_executions(limit=limit)
        return {"status": "ok", "data": executions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto")
async def auto_evolve(request: AutoEvolveRequest):
    """执行完整进化"""
    try:
        results = evolution_engine.auto_evolve(mode=request.mode)
        return {"status": "ok", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """获取进化状态"""
    try:
        status = evolution_engine.get_status()
        return {"status": "ok", "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/start")
async def start_scheduler(config: ScheduleConfigRequest | None = None):
    """启动进化调度器"""
    try:
        schedule_config = config.model_dump(exclude_none=True) if config else None
        evolution_engine.start_scheduler(schedule_config)
        return {"status": "ok", "message": "进化调度器已启动"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/stop")
async def stop_scheduler():
    """停止进化调度器"""
    try:
        evolution_engine.stop_scheduler()
        return {"status": "ok", "message": "进化调度器已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/config")
async def get_schedule_config():
    """获取调度配置"""
    try:
        config = evolution_engine._schedule_config
        return {"status": "ok", "data": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/config")
async def update_schedule_config(config: ScheduleConfigRequest):
    """更新调度配置"""
    try:
        schedule_config = config.model_dump(exclude_none=True)
        updated = evolution_engine.update_schedule_config(schedule_config)
        return {"status": "ok", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
