from __future__ import annotations

import logging
from typing import Any

from .base import ChannelAdapter
from .feishu import FeishuAdapter
from .telegram import TelegramAdapter

logger = logging.getLogger(__name__)


class ChannelManager:
    """消息通道管理器

    统一管理所有通道适配器，根据target前缀自动选择适配器

    支持的通道前缀：
    - feishu:WEBHOOK_URL - 飞书
    - telegram:CHAT_ID - Telegram
    """

    def __init__(self):
        self._adapters: dict[str, ChannelAdapter] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        """注册默认适配器"""
        self.register_adapter("feishu", FeishuAdapter())
        self.register_adapter("telegram", TelegramAdapter())

    def register_adapter(self, scheme: str, adapter: ChannelAdapter) -> None:
        """注册通道适配器

        Args:
            scheme: 通道前缀（如 feishu, telegram）
            adapter: 适配器实例
        """
        self._adapters[scheme.lower()] = adapter
        logger.info(f"已注册通道适配器: {scheme} -> {adapter.get_name()}")

    def get_adapter(self, scheme: str) -> ChannelAdapter | None:
        """获取通道适配器

        Args:
            scheme: 通道前缀

        Returns:
            适配器实例，如果不存在返回None
        """
        return self._adapters.get(scheme.lower())

    def send_message(self, target: str, message: str) -> bool:
        """发送消息到目标渠道

        Args:
            target: 目标地址，格式为 "scheme:address"
                   例如: "feishu:https://..." 或 "telegram:123456"
            message: 消息内容

        Returns:
            bool: 是否发送成功
        """
        if ":" not in target:
            logger.error(f"无效的目标地址格式: {target}，应为 scheme:address")
            return False

        scheme, address = target.split(":", 1)
        adapter = self.get_adapter(scheme)

        if not adapter:
            logger.error(f"未知的通道类型: {scheme}")
            return False

        return adapter.send_message(address, message)

    def test_connection(self, target: str) -> dict[str, Any]:
        """测试通道连接

        Args:
            target: 目标地址

        Returns:
            dict: 测试结果
        """
        if ":" not in target:
            return {"success": False, "error": "无效的目标地址格式"}

        scheme, address = target.split(":", 1)
        adapter = self.get_adapter(scheme)

        if not adapter:
            return {"success": False, "error": f"未知的通道类型: {scheme}"}

        return adapter.test_connection(address)

    def list_channels(self) -> list[dict[str, Any]]:
        """列出所有已注册的通道

        Returns:
            list: 通道信息列表
        """
        return [
            {"scheme": scheme, "name": adapter.get_name()}
            for scheme, adapter in self._adapters.items()
        ]

    def set_telegram_token(self, token: str) -> None:
        """设置Telegram Bot Token

        Args:
            token: Telegram Bot Token
        """
        adapter = self.get_adapter("telegram")
        if adapter and isinstance(adapter, TelegramAdapter):
            adapter.set_bot_token(token)


channel_manager = ChannelManager()
