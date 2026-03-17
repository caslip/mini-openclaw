from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from channels import channel_manager
from config import get_channels_config, set_channels_config

router = APIRouter()


@router.get("/channels/status")
def get_channels_status() -> dict[str, Any]:
    """获取通道状态"""
    config = get_channels_config()
    channels = channel_manager.list_channels()

    return {
        "channels": channels,
        "config": {
            "telegram": {
                "bot_token_configured": bool(config.get("telegram", {}).get("bot_token")),
            },
            "feishu": {
                "default_webhook_configured": bool(
                    config.get("feishu", {}).get("default_webhook")
                ),
            },
        },
    }


@router.post("/channels/test")
def test_channel(data: dict[str, Any]) -> dict[str, Any]:
    """测试通道连接

    Request body:
        - target: 目标地址，格式为 "scheme:address"
    """
    target = data.get("target")
    if not target:
        raise HTTPException(status_code=400, detail="缺少target参数")

    result = channel_manager.test_connection(target)
    return result


@router.post("/channels/send")
def send_message(data: dict[str, Any]) -> dict[str, Any]:
    """手动发送消息

    Request body:
        - target: 目标地址
        - message: 消息内容
    """
    target = data.get("target")
    message = data.get("message", "")

    if not target:
        raise HTTPException(status_code=400, detail="缺少target参数")
    if not message:
        raise HTTPException(status_code=400, detail="缺少message参数")

    success = channel_manager.send_message(target, message)
    if success:
        return {"status": "ok", "message": "消息发送成功"}
    else:
        raise HTTPException(status_code=500, detail="消息发送失败")


@router.get("/channels/list")
def list_channels() -> dict[str, Any]:
    """列出所有已注册的通道"""
    channels = channel_manager.list_channels()
    return {"channels": channels}


@router.post("/channels/config/telegram")
def config_telegram(data: dict[str, Any]) -> dict[str, Any]:
    """配置Telegram Bot Token"""
    bot_token = data.get("bot_token")
    if not bot_token:
        raise HTTPException(status_code=400, detail="缺少bot_token参数")

    channel_manager.set_telegram_token(bot_token)

    config = get_channels_config()
    config.setdefault("telegram", {})["bot_token"] = bot_token
    set_channels_config(config)

    return {"status": "ok", "message": "Telegram Bot Token已配置"}


@router.post("/channels/config/feishu")
def config_feishu(data: dict[str, Any]) -> dict[str, Any]:
    """配置飞书默认Webhook"""
    webhook_url = data.get("webhook_url")
    if not webhook_url:
        raise HTTPException(status_code=400, detail="缺少webhook_url参数")

    config = get_channels_config()
    config.setdefault("feishu", {})["default_webhook"] = webhook_url
    set_channels_config(config)

    return {"status": "ok", "message": "飞书Webhook已配置"}
