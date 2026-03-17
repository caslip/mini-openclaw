from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ChannelAdapter(ABC):
    """消息通道适配器基类"""

    @abstractmethod
    def send_message(self, target: str, message: str) -> bool:
        """发送消息到目标渠道

        Args:
            target: 目标地址，不同渠道格式不同
                   - 飞书: Webhook URL
                   - Telegram: Chat ID
            message: 消息内容

        Returns:
            bool: 发送是否成功
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取渠道名称"""
        pass

    @abstractmethod
    def test_connection(self, target: str) -> dict[str, Any]:
        """测试通道连接

        Args:
            target: 目标地址

        Returns:
            dict: 包含 success 字段和可选的 error 信息
        """
        pass
