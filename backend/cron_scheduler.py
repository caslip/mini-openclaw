from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    AT = "at"
    EVERY = "every"
    CRON = "cron"


class SessionTarget(str, Enum):
    MAIN = "main"
    ISOLATED = "isolated"


class DeliveryType(str, Enum):
    ANNOUNCE = "announce"
    WEBHOOK = "webhook"
    SESSION = "session"
    NONE = "none"


class JobStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


# Built-in task templates
TASK_TEMPLATES: dict[str, dict[str, Any]] = {
    "daily_report": {
        "id": "daily_report",
        "name": "每日报告",
        "description": "生成每日业务报告并发送到指定通道",
        "category": "system",
        "params": [
            {"name": "report_type", "type": "select", "options": ["sales", "inventory", "analytics"], "default": "sales"},
            {"name": "channels", "type": "text", "description": "投递通道，逗号分隔"},
            {"name": "period", "type": "select", "options": ["yesterday", "today", "last_week"], "default": "yesterday"},
        ],
        "default_schedule": "0 8 * * *",
        "default_content": "请生成一份{report_type}报告，时间范围：{period}。",
    },
    "data_sync": {
        "id": "data_sync",
        "name": "数据同步",
        "description": "从外部数据源同步最新数据",
        "category": "system",
        "params": [
            {"name": "source", "type": "select", "options": ["api", "database", "file"], "default": "api"},
            {"name": "target", "type": "text", "description": "目标存储位置"},
        ],
        "default_schedule": "0 */4 * * *",
        "default_content": "请从{source}同步数据到{target}。",
    },
    "health_check": {
        "id": "health_check",
        "name": "健康检查",
        "description": "检查系统和服务健康状态",
        "category": "system",
        "params": [
            {"name": "checks", "type": "text", "description": "检查项，逗号分隔", "default": "api,database,storage"},
        ],
        "default_schedule": "*/15 * * * *",
        "default_content": "请执行健康检查，检查项：{checks}。",
    },
    "cleanup": {
        "id": "cleanup",
        "name": "清理任务",
        "description": "清理临时文件和过期数据",
        "category": "maintenance",
        "params": [
            {"name": "target", "type": "select", "options": ["temp", "logs", "cache", "all"], "default": "temp"},
            {"name": "older_than_days", "type": "number", "default": 7},
        ],
        "default_schedule": "0 2 * * *",
        "default_content": "请清理{target}目录，删除{older_than_days}天前的文件。",
    },
    "backup": {
        "id": "backup",
        "name": "数据备份",
        "description": "执行数据备份任务",
        "category": "maintenance",
        "params": [
            {"name": "target", "type": "text", "description": "备份目标位置"},
            {"name": "compression", "type": "select", "options": ["none", "zip", "gzip"], "default": "gzip"},
        ],
        "default_schedule": "0 3 * * *",
        "default_content": "请执行数据备份，保存到{target}，使用{compression}压缩。",
    },
    "custom": {
        "id": "custom",
        "name": "自定义任务",
        "description": "完全自定义的任务内容",
        "category": "custom",
        "params": [
            {"name": "content", "type": "textarea", "description": "任务指令内容"},
        ],
        "default_schedule": "",
        "default_content": "",
    },
}


@dataclass
class CronJob:
    """定时任务配置"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: ScheduleType = ScheduleType.CRON
    schedule: str = ""
    content: str = ""
    session_target: SessionTarget = SessionTarget.MAIN
    delivery: DeliveryType = DeliveryType.NONE
    target: str = ""
    webhook_url: str = ""
    wake_mode: str = "now"
    enabled: bool = True
    timezone: str = "local"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    last_run: float | None = None
    next_run: float | None = None

    # Extended fields for enhanced features
    category: str = "custom"
    tags: list[str] = field(default_factory=list)
    template_id: str | None = None
    template_params: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    on_success: list[str] = field(default_factory=list)
    on_failure: list[str] = field(default_factory=list)
    conditions: dict[str, Any] = field(default_factory=dict)
    timeout_s: int | None = None
    alert: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "schedule": self.schedule,
            "content": self.content,
            "session_target": self.session_target.value,
            "delivery": self.delivery.value,
            "target": self.target,
            "webhook_url": self.webhook_url,
            "wake_mode": self.wake_mode,
            "enabled": self.enabled,
            "timezone": self.timezone,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_run": self.last_run,
            "next_run": self.next_run,
            # Extended fields
            "category": self.category,
            "tags": self.tags,
            "template_id": self.template_id,
            "template_params": self.template_params,
            "depends_on": self.depends_on,
            "on_success": self.on_success,
            "on_failure": self.on_failure,
            "conditions": self.conditions,
            "timeout_s": self.timeout_s,
            "alert": self.alert,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CronJob:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            type=ScheduleType(data.get("type", "cron")),
            schedule=data.get("schedule", ""),
            content=data.get("content", ""),
            session_target=SessionTarget(data.get("session_target", "main")),
            delivery=DeliveryType(data.get("delivery", "none")),
            target=data.get("target", ""),
            webhook_url=data.get("webhook_url", ""),
            wake_mode=data.get("wake_mode", "now"),
            enabled=data.get("enabled", True),
            timezone=data.get("timezone", "local"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            last_run=data.get("last_run"),
            next_run=data.get("next_run"),
            # Extended fields with defaults for backward compatibility
            category=data.get("category", "custom"),
            tags=data.get("tags", []),
            template_id=data.get("template_id"),
            template_params=data.get("template_params", {}),
            depends_on=data.get("depends_on", []),
            on_success=data.get("on_success", []),
            on_failure=data.get("on_failure", []),
            conditions=data.get("conditions", {}),
            timeout_s=data.get("timeout_s"),
            alert=data.get("alert", {}),
            schema_version=data.get("schema_version", "1.0"),
        )


@dataclass
class JobRun:
    """任务执行记录"""

    job_id: str
    run_id: str
    start_time: float
    end_time: float | None = None
    status: str = "running"
    result: str | None = None
    error: str | None = None
    retry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "run_id": self.run_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
        }


class CronScheduler:
    """定时任务调度器"""

    def __init__(self, storage_path: Path | None = None):
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._jobs: dict[str, CronJob] = {}
        self._retry_delays = [30, 60, 300]
        self._check_interval = 10

        if storage_path:
            self._storage_path = storage_path
        else:
            self._storage_path = Path.home() / ".openclaw" / "cron"
        self._jobs_file = self._storage_path / "jobs.json"
        self._runs_dir = self._storage_path / "runs"

        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._runs_dir.mkdir(parents=True, exist_ok=True)

        self._agent_callback: Callable | None = None
        self._session_delivery_callback: Callable[[str, str], None] | None = None

    def set_agent_callback(self, callback: Callable) -> None:
        """设置Agent执行回调"""
        self._agent_callback = callback

    def set_session_delivery_callback(self, callback: Callable[[str, str], None]) -> None:
        """设置会话投递回调，用于将提醒内容写入会话消息"""
        self._session_delivery_callback = callback

    def start(self) -> None:
        """启动调度器"""
        self._load_jobs()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"Cron调度器已启动，共加载 {len(self._jobs)} 个任务")

    def stop(self) -> None:
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._save_jobs()
        logger.info("Cron调度器已停止")

    def _run(self) -> None:
        """调度器主循环"""
        while self._running:
            try:
                self._check_and_execute()
            except Exception as e:
                logger.error(f"Cron调度器执行错误: {e}")
            time.sleep(self._check_interval)

    def _check_conditions(self, job: CronJob) -> tuple[bool, str]:
        """检查任务执行条件"""
        if not job.conditions:
            return True, ""

        conditions = job.conditions

        # Check file_exists condition
        if "file_exists" in conditions:
            import os
            file_path = conditions["file_exists"].get("path", "")
            if not file_path:
                return False, "file_exists: path not specified"
            if not os.path.exists(file_path):
                return False, f"file_exists: file not found: {file_path}"

        # Check last_result_contains condition
        if "last_result_contains" in conditions:
            last_runs = self.get_job_history(job.id, limit=1)
            if last_runs:
                last_result = last_runs[0].get("result", "")
                text = conditions["last_result_contains"].get("text", "")
                if text and text not in last_result:
                    return False, f"last_result_contains: '{text}' not found in last result"
            else:
                return False, "last_result_contains: no previous run found"

        # Check expr condition (safe evaluation)
        if "expr" in conditions:
            expr = conditions["expr"]
            try:
                # Safe evaluation with limited globals
                allowed_names = {
                    "now": time.time(),
                    "job": {"id": job.id, "name": job.name, "last_run": job.last_run},
                    "last_run": job.last_run,
                }
                result = eval(expr, {"__builtins__": {}}, allowed_names)
                if not result:
                    return False, f"expr condition failed: {expr}"
            except Exception as e:
                return False, f"expr evaluation error: {e}"

        return True, ""

    def _check_dependencies(self, job: CronJob) -> tuple[bool, str]:
        """检查任务依赖是否满足"""
        if not job.depends_on:
            return True, ""

        for dep_id in job.depends_on:
            dep_job = self._jobs.get(dep_id)
            if not dep_job:
                return False, f"dependency job not found: {dep_id}"

            # Check if dependency has ever run successfully
            dep_runs = self.get_job_history(dep_id, limit=5)
            if not dep_runs:
                return False, f"dependency has never run: {dep_id}"

            # Check if the most recent run was successful
            latest_run = dep_runs[0]
            if latest_run.get("status") != "completed":
                return False, f"dependency last run failed: {dep_id}"

        return True, ""

    def _trigger_downstream(
        self, job: CronJob, status: str, visited: set | None = None
    ) -> None:
        """触发下游任务（链式触发）"""
        if visited is None:
            visited = set()

        # Prevent infinite loops
        if job.id in visited:
            return
        visited.add(job.id)

        downstream_ids = []
        if status == "completed" and job.on_success:
            downstream_ids = job.on_success
        elif status == "failed" and job.on_failure:
            downstream_ids = job.on_failure

        for downstream_id in downstream_ids:
            downstream_job = self._jobs.get(downstream_id)
            if not downstream_job:
                logger.warning(f"下游任务不存在: {downstream_id}")
                continue

            if downstream_id in visited:
                logger.warning(f"避免循环依赖，跳过: {downstream_id}")
                continue

            # Check if conditions and dependencies are met
            cond_ok, cond_msg = self._check_conditions(downstream_job)
            if not cond_ok:
                logger.info(f"下游任务条件不满足，跳过: {downstream_id}, reason: {cond_msg}")
                continue

            dep_ok, dep_msg = self._check_dependencies(downstream_job)
            if not dep_ok:
                logger.info(f"下游任务依赖不满足，跳过: {downstream_id}, reason: {dep_msg}")
                continue

            # Execute downstream job immediately
            logger.info(f"链式触发下游任务: {downstream_job.name} (ID: {downstream_id})")
            try:
                self._execute_job(downstream_job)
            except Exception as e:
                logger.error(f"执行下游任务失败: {downstream_id}, error: {e}")

    def _check_and_execute(self) -> None:
        """检查并执行到期任务"""
        now = time.time()
        with self._lock:
            for job in list(self._jobs.values()):
                if not job.enabled:
                    continue

                if job.next_run and now >= job.next_run:
                    self._execute_job(job)

    def _execute_job(self, job: CronJob, skip_conditions: bool = False) -> None:
        """执行单个任务"""
        # Check conditions if not already skipped
        if not skip_conditions:
            cond_ok, cond_msg = self._check_conditions(job)
            if not cond_ok:
                logger.info(f"任务条件不满足，跳过执行: {job.name}, reason: {cond_msg}")
                job.last_run = time.time()
                run_id = str(uuid.uuid4())
                run_record = JobRun(
                    job_id=job.id,
                    run_id=run_id,
                    start_time=time.time(),
                    status="skipped",
                    error=cond_msg,
                    end_time=time.time(),
                )
                self._save_run_record(run_record)
                self._update_next_run(job)
                return

            # Check dependencies
            dep_ok, dep_msg = self._check_dependencies(job)
            if not dep_ok:
                logger.info(f"任务依赖不满足，跳过执行: {job.name}, reason: {dep_msg}")
                job.last_run = time.time()
                run_id = str(uuid.uuid4())
                run_record = JobRun(
                    job_id=job.id,
                    run_id=run_id,
                    start_time=time.time(),
                    status="skipped",
                    error=dep_msg,
                    end_time=time.time(),
                )
                self._save_run_record(run_record)
                self._update_next_run(job)
                return

        job.last_run = time.time()
        run_id = str(uuid.uuid4())
        run_record = JobRun(
            job_id=job.id,
            run_id=run_id,
            start_time=time.time(),
        )

        logger.info(f"执行定时任务: {job.name} (ID: {job.id})")

        try:
            # Handle SESSION delivery type - write directly to session without running agent
            if job.delivery == DeliveryType.SESSION and job.content:
                result = job.content
                if self._session_delivery_callback and job.target:
                    try:
                        self._session_delivery_callback(job.target, result)
                        logger.info(f"提醒已投递到会话: {job.target}")
                    except Exception as e:
                        logger.error(f"会话投递失败: {e}")
                else:
                    logger.warning(f"SESSION 投递但未设置回调或 target 为空")

                run_record.status = "completed"
                run_record.result = result
                run_record.end_time = time.time()
            else:
                # Execute with timeout if specified
                if job.timeout_s:
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self._run_agent, job)
                        try:
                            result = future.result(timeout=job.timeout_s)
                        except concurrent.futures.TimeoutError:
                            raise TimeoutError(f"Task timed out after {job.timeout_s}s")
                else:
                    result = self._run_agent(job)

                run_record.status = "completed"
                run_record.result = result
                run_record.end_time = time.time()

                if job.delivery == DeliveryType.ANNOUNCE and job.target:
                    self._deliver_to_channel(job, result)
                elif job.delivery == DeliveryType.WEBHOOK and job.webhook_url:
                    self._deliver_to_webhook(job, result)

                if job.wake_mode == "now":
                    self._trigger_agent_heartbeat()

                # Trigger downstream on success
                self._trigger_downstream(job, "completed")

                # Check alert thresholds
                self._check_alert(job, "completed")

        except TimeoutError as e:
            logger.error(f"任务执行超时: {e}")
            run_record.status = "failed"
            run_record.error = str(e)
            run_record.end_time = time.time()
            self._handle_retry(job, run_record)
            # Trigger downstream on failure
            self._trigger_downstream(job, "failed")
            # Check alert thresholds
            self._check_alert(job, "failed")

        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            run_record.status = "failed"
            run_record.error = str(e)
            run_record.end_time = time.time()
            self._handle_retry(job, run_record)
            # Trigger downstream on failure
            self._trigger_downstream(job, "failed")
            # Check alert thresholds
            self._check_alert(job, "failed")

        self._save_run_record(run_record)
        self._update_next_run(job)

    def _check_alert(self, job: CronJob, status: str) -> None:
        """检查并触发告警"""
        if not job.alert or not job.alert.get("enabled"):
            return

        failures = job.alert.get("failures", 3)
        window = job.alert.get("window", 3600)  # default 1 hour

        # Get recent runs within the window
        now = time.time()
        recent_runs = self.get_job_history(job.id, limit=100)
        recent_failures = [
            r for r in recent_runs
            if r.get("status") == "failed" and (now - r.get("start_time", 0)) <= window
        ]

        if len(recent_failures) >= failures:
            logger.warning(f"任务 {job.name} 触发告警: {len(recent_failures)} 次失败在 {window}s 内")
            # Send alert notification
            alert_message = f"告警: 任务 {job.name} 在最近 {window}s 内失败 {len(recent_failures)} 次"
            if job.delivery == DeliveryType.ANNOUNCE and job.target:
                self._deliver_to_channel(job, alert_message)
            elif job.delivery == DeliveryType.WEBHOOK and job.webhook_url:
                self._deliver_to_webhook(job, alert_message)

    def _render_template(self, job: CronJob) -> str:
        """渲染任务模板，生成最终content"""
        if not job.template_id or job.template_id == "custom":
            return job.content

        template = TASK_TEMPLATES.get(job.template_id)
        if not template:
            logger.warning(f"未找到模板: {job.template_id}，使用原始content")
            return job.content

        content = template.get("default_content", "")
        params = job.template_params or {}

        try:
            return content.format(**params)
        except KeyError as e:
            logger.error(f"模板参数缺失: {e}")
            return content

    def _run_agent(self, job: CronJob) -> str:
        """运行Agent执行任务"""
        if self._agent_callback is None:
            raise RuntimeError("Agent回调未设置")

        # Render template if template_id is set
        content = self._render_template(job)

        if job.session_target == SessionTarget.ISOLATED:
            session_id = f"cron:{job.id}"
        else:
            session_id = "main"

        response_text = ""
        for event in self._agent_callback(
            message=content,
            history=[],
            session_id=session_id,
        ):
            if event.get("type") == "token":
                response_text += event.get("content", "")
            elif event.get("type") == "done":
                response_text = event.get("content", response_text)

        return response_text

    def _handle_retry(self, job: CronJob, run_record: JobRun) -> None:
        """处理任务重试"""
        if run_record.retry_count < len(self._retry_delays):
            delay = self._retry_delays[run_record.retry_count]
            run_record.retry_count += 1
            job.next_run = time.time() + delay
            logger.info(f"任务 {job.name} 将在 {delay} 秒后重试")
        else:
            job.enabled = False
            logger.warning(f"任务 {job.name} 已禁用，原因：达到最大重试次数")

    def _deliver_to_channel(self, job: CronJob, result: str) -> None:
        """投递结果到通道"""
        from channels import channel_manager

        if not job.target:
            logger.warning(f"任务 {job.name} 未配置投递目标")
            return

        logger.info(f"投递任务结果到通道: {job.target}")

        success = channel_manager.send_message(job.target, result)
        if success:
            logger.info(f"任务结果投递成功: {job.name}")
        else:
            logger.error(f"任务结果投递失败: {job.name}")

    def _deliver_to_webhook(self, job: CronJob, result: str) -> None:
        """投递结果到Webhook"""
        import requests

        logger.info(f"投递任务结果到Webhook: {job.webhook_url}")

        try:
            response = requests.post(
                job.webhook_url,
                json={"job_id": job.id, "job_name": job.name, "result": result},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code < 400:
                logger.info(f"Webhook投递成功: {job.webhook_url[:50]}...")
            else:
                logger.error(f"Webhook投递失败: HTTP {response.status_code}")

        except requests.RequestException as e:
            logger.error(f"Webhook投递失败: {e}")

    def _trigger_agent_heartbeat(self) -> None:
        """触发Agent心跳"""
        logger.info("触发Agent心跳处理任务结果")

    def _update_next_run(self, job: CronJob) -> None:
        """更新任务下次执行时间"""
        if job.type == ScheduleType.AT:
            job.next_run = None
        elif job.type == ScheduleType.EVERY:
            interval = self._parse_interval(job.schedule)
            job.next_run = time.time() + interval
        elif job.type == ScheduleType.CRON:
            job.next_run = self._get_next_cron_time(job.schedule)

    def _parse_interval(self, interval_str: str) -> int:
        """解析间隔字符串"""
        interval_str = interval_str.strip().lower()
        if interval_str.endswith("m"):
            return int(interval_str[:-1]) * 60
        elif interval_str.endswith("h"):
            return int(interval_str[:-1]) * 3600
        elif interval_str.endswith("s"):
            return int(interval_str[:-1])
        else:
            return int(interval_str) * 60

    def _get_next_cron_time(self, cron_expr: str) -> float | None:
        """计算下次cron执行时间"""
        try:
            from croniter import croniter

            if croniter.is_valid(cron_expr):
                now = datetime.now()
                cron = croniter(cron_expr, now)
                next_time = cron.get_next(datetime)
                return next_time.timestamp()
        except ImportError:
            logger.warning("croniter库未安装，使用简单解析")
        except Exception as e:
            logger.error(f"解析cron表达式失败: {e}")

        return None

    def _load_jobs(self) -> None:
        """从文件加载任务"""
        if not self._jobs_file.exists():
            return

        try:
            data = json.loads(self._jobs_file.read_text(encoding="utf-8"))
            for job_data in data.get("jobs", []):
                job = CronJob.from_dict(job_data)
                self._jobs[job.id] = job

                if job.type != ScheduleType.AT and job.next_run is None:
                    self._update_next_run(job)

        except Exception as e:
            logger.error(f"加载任务失败: {e}")

    def _save_jobs(self) -> None:
        """保存任务到文件"""
        with self._lock:
            data = {"jobs": [job.to_dict() for job in self._jobs.values()]}
            self._jobs_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def _save_run_record(self, run: JobRun) -> None:
        """保存执行记录"""
        run_file = self._runs_dir / f"{run.job_id}.jsonl"
        try:
            with open(run_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(run.to_dict(), ensure_ascii=False) + "\n")

            self._trim_run_history(run.job_id)
        except Exception as e:
            logger.error(f"保存执行记录失败: {e}")

    def _trim_run_history(self, job_id: str, max_records: int = 100) -> None:
        """裁剪执行历史"""
        run_file = self._runs_dir / f"{job_id}.jsonl"
        if not run_file.exists():
            return

        try:
            lines = run_file.read_text(encoding="utf-8").strip().split("\n")
            if len(lines) > max_records:
                lines = lines[-max_records:]
                run_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception as e:
            logger.error(f"裁剪执行历史失败: {e}")

    def add_job(self, job: CronJob) -> CronJob:
        """添加新任务"""
        with self._lock:
            if job.type == ScheduleType.AT:
                # AT 类型：解析 schedule 作为相对秒数或绝对时间戳
                if job.schedule:
                    try:
                        # 尝试解析为相对秒数
                        delay_seconds = int(job.schedule)
                        job.next_run = time.time() + delay_seconds
                    except ValueError:
                        # 尝试解析为 Unix 时间戳（浮点数）
                        try:
                            job.next_run = float(job.schedule)
                        except ValueError:
                            logger.warning(f"无法解析 AT schedule: {job.schedule}，设置为立即执行")
                            job.next_run = time.time()
            else:
                self._update_next_run(job)
            self._jobs[job.id] = job
            self._save_jobs()
        logger.info(f"添加定时任务: {job.name} (ID: {job.id}), 下次执行: {job.next_run}")
        return job

    def update_job(self, job_id: str, updates: dict[str, Any]) -> CronJob | None:
        """更新任务"""
        with self._lock:
            if job_id not in self._jobs:
                return None

            job = self._jobs[job_id]
            for key, value in updates.items():
                if hasattr(job, key):
                    setattr(job, key, value)

            job.updated_at = time.time()
            if job.type != ScheduleType.AT:
                self._update_next_run(job)

            self._save_jobs()
        logger.info(f"更新定时任务: {job.name} (ID: {job.id})")
        return job

    def delete_job(self, job_id: str) -> bool:
        """删除任务"""
        with self._lock:
            if job_id not in self._jobs:
                return False

            job = self._jobs.pop(job_id)
            self._save_jobs()

            run_file = self._runs_dir / f"{job_id}.jsonl"
            if run_file.exists():
                run_file.unlink()

        logger.info(f"删除定时任务: {job.name} (ID: {job.id})")
        return True

    def get_job(self, job_id: str) -> CronJob | None:
        """获取任务详情"""
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[CronJob]:
        """列出所有任务"""
        return list(self._jobs.values())

    def trigger_job(self, job_id: str) -> dict[str, Any] | None:
        """手动触发任务"""
        job = self._jobs.get(job_id)
        if not job:
            return None

        if not job.enabled:
            return {"status": "error", "message": "任务已禁用"}

        try:
            result = self._run_agent(job)
            return {"status": "ok", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_job_history(self, job_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """获取任务执行历史"""
        run_file = self._runs_dir / f"{job_id}.jsonl"
        if not run_file.exists():
            return []

        try:
            lines = run_file.read_text(encoding="utf-8").strip().split("\n")
            records = []
            for line in reversed(lines):
                if line.strip():
                    records.append(json.loads(line))
                    if len(records) >= limit:
                        break
            return records
        except Exception as e:
            logger.error(f"读取执行历史失败: {e}")
            return []

    def export_jobs(self) -> dict[str, Any]:
        """导出所有任务配置"""
        jobs = [job.to_dict() for job in self._jobs.values()]
        return {
            "schema_version": "1.0",
            "exported_at": time.time(),
            "jobs": jobs,
        }

    def import_jobs(self, data: dict[str, Any], strategy: str = "merge") -> dict[str, Any]:
        """导入任务配置

        Args:
            data: 导出的任务配置数据
            strategy: 导入策略 "merge" (合并) 或 "overwrite" (覆盖)
        """
        imported_jobs = data.get("jobs", [])
        imported_count = 0
        skipped_count = 0

        for job_data in imported_jobs:
            job_id = job_data.get("id")
            existing_job = self._jobs.get(job_id)

            if strategy == "overwrite" or not existing_job:
                job = CronJob.from_dict(job_data)
                self._jobs[job.id] = job
                imported_count += 1
            elif strategy == "merge" and existing_job:
                # Skip existing jobs in merge mode
                skipped_count += 1
                continue

        self._save_jobs()

        return {
            "imported": imported_count,
            "skipped": skipped_count,
            "strategy": strategy,
        }

    def get_metrics(self) -> dict[str, Any]:
        """获取任务运行统计"""
        jobs = list(self._jobs.values())
        total_jobs = len(jobs)
        active_jobs = sum(1 for j in jobs if j.enabled)

        # Collect run statistics
        total_runs = 0
        completed_runs = 0
        failed_runs = 0
        skipped_runs = 0
        total_duration = 0.0
        recent_failures: list[dict[str, Any]] = []

        # Get all runs from the past 7 days
        week_ago = time.time() - 7 * 24 * 3600

        for job in jobs:
            runs = self.get_job_history(job.id, limit=100)
            for run in runs:
                total_runs += 1
                start_time = run.get("start_time", 0)
                if start_time < week_ago:
                    continue

                status = run.get("status", "")
                if status == "completed":
                    completed_runs += 1
                    end_time = run.get("end_time", 0)
                    if end_time and start_time:
                        total_duration += (end_time - start_time)
                elif status == "failed":
                    failed_runs += 1
                    recent_failures.append({
                        "job_id": job.id,
                        "job_name": job.name,
                        "run_id": run.get("run_id"),
                        "error": run.get("error"),
                        "start_time": start_time,
                    })
                elif status == "skipped":
                    skipped_runs += 1

        # Limit recent failures
        recent_failures.sort(key=lambda x: x.get("start_time", 0), reverse=True)
        recent_failures = recent_failures[:10]

        # Group by category
        category_stats: dict[str, dict[str, int]] = {}
        tag_stats: dict[str, int] = {}
        for job in jobs:
            cat = job.category or "uncategorized"
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "active": 0}
            category_stats[cat]["total"] += 1
            if job.enabled:
                category_stats[cat]["active"] += 1

            for tag in job.tags:
                tag_stats[tag] = tag_stats.get(tag, 0) + 1

        success_rate = (completed_runs / total_runs * 100) if total_runs > 0 else 0
        avg_duration = total_duration / completed_runs if completed_runs > 0 else 0

        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "failed_runs": failed_runs,
            "skipped_runs": skipped_runs,
            "success_rate": round(success_rate, 2),
            "avg_duration_s": round(avg_duration, 2),
            "recent_failures": recent_failures,
            "category_stats": category_stats,
            "tag_stats": tag_stats,
        }

    def list_templates(self) -> list[dict[str, Any]]:
        """获取任务模板列表"""
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "description": t["description"],
                "category": t["category"],
                "params": t["params"],
                "default_schedule": t["default_schedule"],
            }
            for t in TASK_TEMPLATES.values()
        ]

    def get_template(self, template_id: str) -> dict[str, Any] | None:
        """获取模板详情"""
        template = TASK_TEMPLATES.get(template_id)
        if not template:
            return None
        return {
            "id": template["id"],
            "name": template["name"],
            "description": template["description"],
            "category": template["category"],
            "params": template["params"],
            "default_schedule": template["default_schedule"],
            "default_content": template["default_content"],
        }


cron_scheduler = CronScheduler()
