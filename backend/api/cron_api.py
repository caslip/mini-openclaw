from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from cron_scheduler import (
    CronJob,
    CronScheduler,
    DeliveryType,
    ScheduleType,
    SessionTarget,
    cron_scheduler,
)

router = APIRouter()


@router.get("/cron/jobs")
def list_cron_jobs(
    category: str | None = None,
    tag: str | None = None,
) -> dict[str, Any]:
    """列出所有定时任务，支持按category和tag筛选"""
    jobs = cron_scheduler.list_jobs()

    # Apply filters
    if category:
        jobs = [j for j in jobs if j.category == category]
    if tag:
        jobs = [j for j in jobs if tag in j.tags]

    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": len(jobs),
    }


@router.get("/cron/templates")
def list_cron_templates() -> dict[str, Any]:
    """获取任务模板列表"""
    templates = cron_scheduler.list_templates()
    return {
        "templates": templates,
        "total": len(templates),
    }


@router.get("/cron/templates/{template_id}")
def get_cron_template(template_id: str) -> dict[str, Any]:
    """获取指定模板详情"""
    template = cron_scheduler.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"template": template}


@router.post("/cron/jobs/from-template")
def create_job_from_template(request: dict[str, Any]) -> dict[str, Any]:
    """基于模板创建任务"""
    template_id = request.get("template_id")
    if not template_id:
        raise HTTPException(status_code=400, detail="template_id 不能为空")

    template = cron_scheduler.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # Build job data from template
    job_data = {
        "name": request.get("name", template["name"]),
        "type": request.get("type", "cron"),
        "schedule": request.get("schedule", template.get("default_schedule", "")),
        "content": request.get("content", ""),
        "session_target": request.get("session_target", "main"),
        "delivery": request.get("delivery", "none"),
        "target": request.get("target", ""),
        "webhook_url": request.get("webhook_url", ""),
        "wake_mode": request.get("wake_mode", "now"),
        "enabled": request.get("enabled", True),
        "timezone": request.get("timezone", "local"),
        "category": request.get("category", template.get("category", "custom")),
        "tags": request.get("tags", []),
        "template_id": template_id,
        "template_params": request.get("template_params", {}),
        "depends_on": request.get("depends_on", []),
        "on_success": request.get("on_success", []),
        "on_failure": request.get("on_failure", []),
        "conditions": request.get("conditions", {}),
        "timeout_s": request.get("timeout_s"),
        "alert": request.get("alert", {}),
    }

    try:
        job = CronJob(
            name=job_data["name"],
            type=ScheduleType(job_data["type"]),
            schedule=job_data["schedule"],
            content=job_data["content"],
            session_target=SessionTarget(job_data["session_target"]),
            delivery=DeliveryType(job_data["delivery"]),
            target=job_data["target"],
            webhook_url=job_data["webhook_url"],
            wake_mode=job_data["wake_mode"],
            enabled=job_data["enabled"],
            timezone=job_data["timezone"],
            category=job_data["category"],
            tags=job_data["tags"],
            template_id=job_data["template_id"],
            template_params=job_data["template_params"],
            depends_on=job_data["depends_on"],
            on_success=job_data["on_success"],
            on_failure=job_data["on_failure"],
            conditions=job_data["conditions"],
            timeout_s=job_data["timeout_s"],
            alert=job_data["alert"],
        )

        created_job = cron_scheduler.add_job(job)
        return {"status": "ok", "job": created_job.to_dict()}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cron/jobs")
def create_cron_job(job_data: dict[str, Any]) -> dict[str, Any]:
    """创建新的定时任务（支持所有扩展字段）"""
    try:
        job = CronJob(
            name=job_data.get("name", ""),
            type=ScheduleType(job_data.get("type", "cron")),
            schedule=job_data.get("schedule", ""),
            content=job_data.get("content", ""),
            session_target=SessionTarget(job_data.get("session_target", "main")),
            delivery=DeliveryType(job_data.get("delivery", "none")),
            target=job_data.get("target", ""),
            webhook_url=job_data.get("webhook_url", ""),
            wake_mode=job_data.get("wake_mode", "now"),
            enabled=job_data.get("enabled", True),
            timezone=job_data.get("timezone", "local"),
            # Extended fields
            category=job_data.get("category", "custom"),
            tags=job_data.get("tags", []),
            template_id=job_data.get("template_id"),
            template_params=job_data.get("template_params", {}),
            depends_on=job_data.get("depends_on", []),
            on_success=job_data.get("on_success", []),
            on_failure=job_data.get("on_failure", []),
            conditions=job_data.get("conditions", {}),
            timeout_s=job_data.get("timeout_s"),
            alert=job_data.get("alert", {}),
        )

        created_job = cron_scheduler.add_job(job)
        return {"status": "ok", "job": created_job.to_dict()}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cron/jobs/{job_id}")
def get_cron_job(job_id: str) -> dict[str, Any]:
    """获取指定任务详情"""
    job = cron_scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"job": job.to_dict()}


@router.put("/cron/jobs/{job_id}")
def update_cron_job(job_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """更新指定任务"""
    job = cron_scheduler.update_job(job_id, updates)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"status": "ok", "job": job.to_dict()}


@router.delete("/cron/jobs/{job_id}")
def delete_cron_job(job_id: str) -> dict[str, Any]:
    """删除指定任务"""
    success = cron_scheduler.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"status": "ok", "message": "任务已删除"}


@router.post("/cron/jobs/{job_id}/trigger")
def trigger_cron_job(job_id: str) -> dict[str, Any]:
    """手动触发指定任务"""
    result = cron_scheduler.trigger_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return result


@router.get("/cron/jobs/{job_id}/history")
def get_cron_job_history(job_id: str, limit: int = 20) -> dict[str, Any]:
    """获取任务执行历史"""
    job = cron_scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")

    history = cron_scheduler.get_job_history(job_id, limit)
    return {
        "job_id": job_id,
        "job_name": job.name,
        "history": history,
        "total": len(history),
    }


@router.get("/cron/status")
def get_cron_status() -> dict[str, Any]:
    """获取调度器状态"""
    jobs = cron_scheduler.list_jobs()
    active_jobs = [j for j in jobs if j.enabled]
    return {
        "running": True,
        "total_jobs": len(jobs),
        "active_jobs": len(active_jobs),
        "storage_path": str(cron_scheduler._storage_path),
    }


@router.get("/cron/export")
def export_cron_jobs() -> dict[str, Any]:
    """导出所有任务配置"""
    return cron_scheduler.export_jobs()


@router.post("/cron/import")
def import_cron_jobs(request: dict[str, Any]) -> dict[str, Any]:
    """导入任务配置

    Request body:
        data: 导出的任务配置数据
        strategy: 导入策略 "merge" (合并，默认) 或 "overwrite" (覆盖)
    """
    data = request.get("data", {})
    strategy = request.get("strategy", "merge")

    if strategy not in ("merge", "overwrite"):
        raise HTTPException(status_code=400, detail="strategy 必须是 'merge' 或 'overwrite'")

    result = cron_scheduler.import_jobs(data, strategy)
    return {"status": "ok", **result}


@router.get("/cron/metrics")
def get_cron_metrics() -> dict[str, Any]:
    """获取任务运行统计"""
    return cron_scheduler.get_metrics()
