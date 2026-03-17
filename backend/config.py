from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
DEFAULT_CONFIG: dict[str, Any] = {
    "rag_mode": False,
    "heartbeat": {
        "enabled": True,
        "every": "30m",
        "diagnostic_interval": 30,
        "target": "none",
        "active_hours": None,
    },
    "cron": {
        "enabled": True,
        "storage_path": None,
    },
    "channels": {
        "telegram": {
            "bot_token": None,
        },
        "feishu": {
            "default_webhook": None,
        },
    },
    "evolution": {
        "enabled": True,
        "skill_discovery": {
            "enabled": True,
            "interval": "1h"
        },
        "prompt_evolution": {
            "enabled": True,
            "interval": "24h"
        },
        "workflow_evolution": {
            "enabled": True,
            "interval": "168h"
        }
    }
}


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_rag_mode() -> bool:
    return bool(load_config().get("rag_mode", False))


def set_rag_mode(enabled: bool) -> dict[str, Any]:
    config = load_config()
    config["rag_mode"] = bool(enabled)
    save_config(config)
    return config


def get_heartbeat_config() -> dict[str, Any]:
    config = load_config()
    return config.get("heartbeat", DEFAULT_CONFIG["heartbeat"])


def set_heartbeat_config(heartbeat_config: dict[str, Any]) -> dict[str, Any]:
    config = load_config()
    config["heartbeat"] = {**DEFAULT_CONFIG["heartbeat"], **heartbeat_config}
    save_config(config)
    return config["heartbeat"]


def get_cron_config() -> dict[str, Any]:
    config = load_config()
    return config.get("cron", DEFAULT_CONFIG["cron"])


def set_cron_config(cron_config: dict[str, Any]) -> dict[str, Any]:
    config = load_config()
    config["cron"] = {**DEFAULT_CONFIG["cron"], **cron_config}
    save_config(config)
    return config["cron"]


def get_channels_config() -> dict[str, Any]:
    config = load_config()
    return config.get("channels", DEFAULT_CONFIG["channels"])


def set_channels_config(channels_config: dict[str, Any]) -> dict[str, Any]:
    config = load_config()
    config["channels"] = {**DEFAULT_CONFIG["channels"], **channels_config}
    save_config(config)
    return config["channels"]


def get_evolution_config() -> dict[str, Any]:
    config = load_config()
    return config.get("evolution", DEFAULT_CONFIG["evolution"])


def set_evolution_config(evolution_config: dict[str, Any]) -> dict[str, Any]:
    config = load_config()
    config["evolution"] = {**DEFAULT_CONFIG["evolution"], **evolution_config}
    save_config(config)
    return config["evolution"]
