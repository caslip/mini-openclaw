from __future__ import annotations

import logging
from typing import Any

import requests

from .base import ChannelAdapter

logger = logging.getLogger(__name__)


class TelegramAdapter(ChannelAdapter):
    """Telegram消息通道适配器

    使用Telegram Bot API发送消息
    """

    def __init__(self, bot_token: str | None = None):
        """初始化Telegram适配器

        Args:
            bot_token: Telegram Bot Token，从配置中获取
        """
        self._bot_token = bot_token

    def get_name(self) -> str:
        return "telegram"

    def send_message(self, target: str, message: str) -> bool:
        """发送消息到Telegram

        Args:
            target: Telegram Chat ID
            message: 消息内容，支持Markdown格式

        Returns:
            bool: 是否发送成功
        """
        if not self._bot_token:
            logger.error("Telegram Bot Token未配置")
            return False

        try:
            url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
            payload = {
                "chat_id": target,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(f"Telegram消息发送成功: chat_id={target}")
                    return True
                else:
                    logger.error(f"Telegram API错误: {result.get('description')}")
                    return False
            else:
                logger.error(f"Telegram请求失败: HTTP {response.status_code}")
                return False

        except requests.RequestException as e:
            logger.error(f"Telegram消息发送失败: {e}")
            return False

    def test_connection(self, target: str) -> dict[str, Any]:
        """测试Telegram连接

        Args:
            target: Telegram Chat ID

        Returns:
            dict: 测试结果
        """
        if not self._bot_token:
            return {"success": False, "error": "Bot Token未配置"}

        try:
            url = f"https://api.telegram.org/bot{self._bot_token}/getMe"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    return {
                        "success": True,
                        "message": f"Bot @{result.get('result', {}).get('username')} 连接成功",
                    }
                else:
                    return {"success": False, "error": "Bot Token无效"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def set_bot_token(self, bot_token: str) -> None:
        """设置Bot Token"""
        self._bot_token = bot_token
