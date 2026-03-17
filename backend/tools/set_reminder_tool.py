from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any, Callable

from langchain_core.tools import tool


def make_set_reminder_tool(get_session_id: Callable[[], str]):
    """创建定时提醒工具
    
    Args:
        get_session_id: 获取当前会话ID的回调函数
    """

    @tool
    def set_reminder(delay_seconds: int, message: str = "您设置的提醒时间到了") -> str:
        """设置一个定时提醒，在指定秒数后通过当前会话提醒用户。

        Args:
            delay_seconds: 多少秒后提醒（例如 60 表示 1 分钟后，1800 表示 30 分钟后）
            message: 提醒的具体内容（可选，默认值为"您设置的提醒时间到了"）
        """
        # 获取当前会话ID
        session_id = get_session_id()
        if not session_id:
            return "错误：无法确定当前会话，请在对话中重试。"

        # 避免循环导入：在工具内部导入
        from cron_scheduler import CronJob, ScheduleType, DeliveryType, cron_scheduler

        job_id = str(uuid.uuid4())[:8]
        job = CronJob(
            id=job_id,
            name=f"reminder-{job_id}",
            type=ScheduleType.AT,
            schedule=str(delay_seconds),
            content=f"\u23f0 提醒：{message}",
            session_target="main",
            delivery=DeliveryType.SESSION,
            target=session_id,
            enabled=True,
            timezone="local",
        )

        try:
            cron_scheduler.add_job(job)
            # 生成友好的时间描述
            if delay_seconds < 60:
                time_desc = f"{delay_seconds}秒"
            elif delay_seconds < 3600:
                minutes = delay_seconds // 60
                seconds = delay_seconds % 60
                if seconds > 0:
                    time_desc = f"{minutes}分{seconds}秒"
                else:
                    time_desc = f"{minutes}分钟"
            else:
                hours = delay_seconds // 3600
                minutes = (delay_seconds % 3600) // 60
                if minutes > 0:
                    time_desc = f"{hours}小时{minutes}分钟"
                else:
                    time_desc = f"{hours}小时"

            return f"\u2705 已设置 {time_desc} 后的提醒，届时会在本对话中显示提醒内容。"
        except Exception as e:
            return f"设置提醒失败：{str(e)}"

    return set_reminder
