from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable

from config import get_heartbeat_config
from graph import agent_manager

logger = logging.getLogger(__name__)


def parse_interval(interval_str: str) -> int:
    """Parse interval string like '30m', '1h' to seconds."""
    interval_str = interval_str.strip().lower()
    if interval_str.endswith("m"):
        return int(interval_str[:-1]) * 60
    elif interval_str.endswith("h"):
        return int(interval_str[:-1]) * 3600
    elif interval_str.endswith("s"):
        return int(interval_str[:-1])
    else:
        return int(interval_str) * 60


class DiagnosticHeartbeat:
    """诊断心跳 - 每30秒触发一次，收集系统指标用于监控"""

    def __init__(self):
        self._running = False
        self._thread: threading.Thread | None = None
        self._interval = 30
        self._callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._last_metrics: dict[str, Any] = {}
        self._start_time = time.time()

    def start(self) -> None:
        """启动诊断心跳"""
        config = get_heartbeat_config()
        if not config.get("enabled", True):
            logger.info("诊断心跳已禁用")
            return

        self._interval = config.get("diagnostic_interval", 30)
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"诊断心跳已启动，间隔 {self._interval} 秒")

    def stop(self) -> None:
        """停止诊断心跳"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("诊断心跳已停止")

    def _run(self) -> None:
        """诊断心跳主循环"""
        while self._running:
            try:
                self._collect_and_notify()
            except Exception as e:
                logger.error(f"诊断心跳执行错误: {e}")
            time.sleep(self._interval)

    def _collect_and_notify(self) -> None:
        """收集指标并通知订阅者"""
        metrics = self._collect_metrics()
        self._last_metrics = metrics
        for callback in self._callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"诊断心跳回调错误: {e}")

    def _collect_metrics(self) -> dict[str, Any]:
        """收集系统指标"""
        session_manager = agent_manager.session_manager
        sessions = session_manager.list_sessions() if session_manager else []

        active_sessions = [
            s for s in sessions
            if time.time() - s.get("updated_at", 0) < 300
        ]

        return {
            "type": "diagnostic.heartbeat",
            "timestamp": time.time(),
            "uptime": time.time() - self._start_time,
            "total_sessions": len(sessions),
            "active_sessions": len(active_sessions),
            "heartbeat": {
                "agent_enabled": get_heartbeat_config().get("enabled", True),
                "diagnostic_interval": self._interval,
            },
        }

    def subscribe(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """订阅诊断心跳事件"""
        self._callbacks.append(callback)

    def get_last_metrics(self) -> dict[str, Any]:
        """获取上次收集的指标"""
        return self._last_metrics

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running


class AgentHeartbeat:
    """Agent心跳 - 让AI主动检查数据文件更新并提醒用户"""

    def __init__(self):
        self._running = False
        self._thread: threading.Thread | None = None
        self._interval = 30 * 60
        self._target = "none"
        self._active_hours: tuple[int, int] | None = None
        self._last_run: float = 0

    def start(self) -> None:
        """启动Agent心跳"""
        config = get_heartbeat_config()
        if not config.get("enabled", True):
            logger.info("Agent心跳已禁用")
            return

        self._interval = parse_interval(config.get("every", "30m"))
        self._target = config.get("target", "none")
        active_hours = config.get("active_hours")
        if active_hours and isinstance(active_hours, dict):
            self._active_hours = (active_hours.get("start", 0), active_hours.get("end", 23))

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(f"Agent心跳已启动，间隔 {self._interval} 秒")

    def stop(self) -> None:
        """停止Agent心跳"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Agent心跳已停止")

    def _run(self) -> None:
        """Agent心跳主循环"""
        while self._running:
            try:
                if self._should_run():
                    self._execute_heartbeat()
            except Exception as e:
                logger.error(f"Agent心跳执行错误: {e}")
            time.sleep(60)

    def _should_run(self) -> bool:
        """检查是否应该运行心跳"""
        now = time.time()
        if now - self._last_run < self._interval:
            return False

        if self._active_hours:
            import datetime
            current_hour = datetime.datetime.now().hour
            start, end = self._active_hours
            if start <= end:
                if not (start <= current_hour < end):
                    return False
            else:
                if not (current_hour >= start or current_hour < end):
                    return False

        return True

    def _execute_heartbeat(self) -> dict[str, Any] | None:
        """执行Agent心跳检查"""
        self._last_run = time.time()
        logger.info("执行Agent心跳检查...")

        heartbeat_file = Path("HEARTBEAT.md")
        if not heartbeat_file.exists():
            heartbeat_file = Path(__file__).parent.parent / "HEARTBEAT.md"

        if not heartbeat_file.exists():
            logger.warning("HEARTBEAT.md 文件不存在，跳过心跳")
            return None

        heartbeat_prompt = heartbeat_file.read_text(encoding="utf-8")

        result = {"status": "ok", "message": "无需要提醒的事项", "alert_sent": False}

        try:
            response_text = ""
            for event in agent_manager.astream(
                message=heartbeat_prompt,
                history=[],
                session_id="heartbeat",
            ):
                if event.get("type") == "token":
                    response_text += event.get("content", "")
                elif event.get("type") == "done":
                    response_text = event.get("content", response_text)

            if response_text.strip() and "HEARTBEAT_OK" not in response_text.upper():
                result = {
                    "status": "alert",
                    "message": response_text,
                    "alert_sent": True,
                }
                logger.info(f"Agent心跳发现需要提醒的事项: {response_text[:100]}...")

                # 发送到目标通道
                if self._target and self._target != "none":
                    self._send_alert(response_text)
            else:
                logger.info("Agent心跳检查完成，无需提醒")

        except Exception as e:
            logger.error(f"Agent心跳执行失败: {e}")
            result = {"status": "error", "message": str(e), "alert_sent": False}

        return result

    def _send_alert(self, message: str) -> None:
        """发送告警到目标通道"""
        from channels import channel_manager

        logger.info(f"发送心跳告警到: {self._target}")
        success = channel_manager.send_message(self._target, message)
        if success:
            logger.info("心跳告警发送成功")
        else:
            logger.error("心跳告警发送失败")

    def trigger(self) -> dict[str, Any] | None:
        """手动触发Agent心跳"""
        if not self._running:
            logger.warning("Agent心跳未启动")
            return None
        return self._execute_heartbeat()

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    def get_last_run_time(self) -> float:
        """获取上次运行时间"""
        return self._last_run


agent_heartbeat = AgentHeartbeat()
diagnostic_heartbeat = DiagnosticHeartbeat()
