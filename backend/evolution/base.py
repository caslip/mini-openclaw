from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class EvolutionType(str, Enum):
    """进化类型"""

    SKILL = "skill"
    PROMPT = "prompt"
    WORKFLOW = "workflow"


class EvolutionStatus(str, Enum):
    """进化状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class EvolutionResult:
    """进化结果"""

    type: EvolutionType
    status: EvolutionStatus
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


class EvolutionBase(ABC):
    """进化基类"""

    def __init__(self, base_dir: Path, storage_path: Path | None = None):
        self.base_dir = base_dir
        self.storage_path = storage_path or base_dir / "evolution_data"
        self.storage_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def run(self) -> EvolutionResult:
        """执行进化"""
        pass

    def get_last_result(self, evolution_type: EvolutionType) -> EvolutionResult | None:
        """获取上次进化结果"""
        result_file = self.storage_path / f"last_{evolution_type.value}.json"
        if not result_file.exists():
            return None

        try:
            import json

            data = json.loads(result_file.read_text(encoding="utf-8"))
            return EvolutionResult(
                type=EvolutionType(data.get("type", evolution_type.value)),
                status=EvolutionStatus(data.get("status", "completed")),
                timestamp=data.get("timestamp", 0),
                data=data.get("data", {}),
                error=data.get("error"),
                duration_ms=data.get("duration_ms", 0),
            )
        except Exception as e:
            logger.error(f"读取进化结果失败: {e}")
            return None

    def save_result(self, result: EvolutionResult) -> None:
        """保存进化结果"""
        result_file = self.storage_path / f"last_{result.type.value}.json"
        try:
            import json

            result_file.write_text(
                json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"保存进化结果失败: {e}")
