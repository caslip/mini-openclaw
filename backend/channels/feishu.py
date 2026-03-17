from __future__ import annotations

import logging
from typing import Any

import requests

from .base import ChannelAdapter

logger = logging.getLogger(__name__)


class FeishuAdapter(ChannelAdapter):
    """飞书消息通道适配器

    使用飞书自定义机器人 Webhook 发送消息
    """

    def get_name(self) -> str:
        return "feishu"

    def send_message(self, target: str, message: str) -> bool:
        """发送消息到飞书

        Args:
            target: 飞书 Webhook URL
            message: 消息内容

        Returns:
            bool: 是否发送成功
        """
        try:
            payload = self._build_message(message)
            response = requests.post(
                target,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.info(f"飞书消息发送成功: {target[:50]}...")
                    return True
                else:
                    logger.error(f"飞书API错误: {result.get('msg')}")
                    return False
            else:
                logger.error(f"飞书请求失败: HTTP {response.status_code}")
                return False

        except requests.RequestException as e:
            logger.error(f"飞书消息发送失败: {e}")
            return False

    def test_connection(self, target: str) -> dict[str, Any]:
        """测试飞书连接

        Args:
            target: 飞书 Webhook URL

        Returns:
            dict: 测试结果
        """
        try:
            payload = self._build_message("🔔 连接测试消息")
            response = requests.post(
                target,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return {"success": True, "message": "连接成功"}
                else:
                    return {"success": False, "error": result.get("msg", "未知错误")}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def _build_message(self, message: str) -> dict[str, Any]:
        """构建飞书消息格式

        使用富文本消息卡片格式
        """
        return {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🤖 Agent 提醒",
                    },
                    "template": "blue",
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": message,
                    }
                ],
            },
        }
