from __future__ import annotations

import json
import logging
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from evolution.base import EvolutionBase, EvolutionResult, EvolutionStatus, EvolutionType

logger = logging.getLogger(__name__)


class PromptOptimizer(EvolutionBase):
    """Prompt优化器"""

    def __init__(self, base_dir: Path, storage_path: Path | None = None):
        super().__init__(base_dir, storage_path)
        self.sessions_dir = base_dir / "sessions"

    def run(self) -> EvolutionResult:
        """执行Prompt分析"""
        start_time = time.time()
        try:
            sessions = self.analyze_sessions()
            patterns = self.extract_patterns(sessions)
            suggestions = self.generate_prompt_updates(patterns)

            duration_ms = (time.time() - start_time) * 1000

            result = EvolutionResult(
                type=EvolutionType.PROMPT,
                status=EvolutionStatus.COMPLETED,
                data={
                    "sessions_analyzed": len(sessions),
                    "patterns": patterns,
                    "suggestions": suggestions,
                },
                duration_ms=duration_ms,
            )

            self.save_result(result)
            logger.info(f"Prompt分析完成，分析了 {len(sessions)} 个会话")
            return result

        except Exception as e:
            logger.error(f"Prompt分析失败: {e}")
            result = EvolutionResult(
                type=EvolutionType.PROMPT,
                status=EvolutionStatus.FAILED,
                error=str(e),
            )
            self.save_result(result)
            return result

    def analyze_sessions(self, limit: int = 100) -> list[dict]:
        """分析历史会话，找出常见问题和改进点"""
        if not self.sessions_dir.exists():
            logger.warning(f"Sessions目录不存在: {self.sessions_dir}")
            return []

        sessions = []
        session_files = sorted(
            self.sessions_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]

        for session_file in session_files:
            try:
                session_data = json.loads(session_file.read_text(encoding="utf-8"))
                session_analysis = self._analyze_session(session_data)
                if session_analysis:
                    sessions.append(session_analysis)
            except Exception as e:
                logger.error(f"分析会话失败 {session_file}: {e}")

        return sessions

    def _analyze_session(self, session_data: dict[str, Any]) -> dict[str, Any] | None:
        """分析单个会话"""
        if not isinstance(session_data, dict):
            return None

        messages = session_data.get("messages", [])
        if not messages:
            return None

        user_messages = [m for m in messages if m.get("role") == "user"]
        assistant_messages = [m for m in messages if m.get("role") == "assistant"]

        return {
            "session_id": session_data.get("id", "unknown"),
            "message_count": len(messages),
            "user_message_count": len(user_messages),
            "assistant_message_count": len(assistant_messages),
            "first_message": user_messages[0].get("content", "")[:100] if user_messages else "",
            "last_message_time": session_data.get("updated_at"),
        }

    def extract_patterns(self, sessions: list[dict]) -> list[dict[str, Any]]:
        """提取成功的任务执行模式"""
        if not sessions:
            return []

        patterns = []

        topic_counter = Counter()
        for session in sessions:
            first_msg = session.get("first_message", "")
            if first_msg:
                topic = self._classify_topic(first_msg)
                topic_counter[topic] += 1

        common_topics = topic_counter.most_common(10)
        if common_topics:
            patterns.append({
                "type": "common_topics",
                "description": "最常见的用户话题",
                "data": common_topics,
            })

        avg_messages = sum(s.get("message_count", 0) for s in sessions) / len(sessions)
        patterns.append({
            "type": "avg_messages",
            "description": "平均会话消息数",
            "data": {"value": round(avg_messages, 2)},
        })

        long_sessions = [s for s in sessions if s.get("message_count", 0) > 10]
        if long_sessions:
            patterns.append({
                "type": "long_sessions",
                "description": "长会话特征",
                "data": {"count": len(long_sessions), "percentage": round(len(long_sessions) / len(sessions) * 100, 2)},
            })

        return patterns

    def _classify_topic(self, message: str) -> str:
        """简单的话题分类"""
        message_lower = message.lower()

        topic_keywords = {
            "代码开发": ["代码", "写", "function", "class", "def ", "implement"],
            "数据分析": ["分析", "数据", "chart", "图", "统计"],
            "文件操作": ["文件", "读取", "写入", "read", "write", "file"],
            "搜索查询": ["搜索", "查找", "search", "query", "找"],
            "知识问答": ["什么是", "如何", "why", "how", "解释"],
            "调试修复": ["bug", "错误", "修复", "fix", "error", "问题"],
            "文档生成": ["文档", "readme", "生成", "文档化"],
            "日常对话": ["你好", "hello", "hi", "天气"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in message_lower for kw in keywords):
                return topic

        return "其他"

    def generate_prompt_updates(self, analysis: dict | list) -> list[str]:
        """生成Prompt改进建议"""
        suggestions = []

        if isinstance(analysis, dict):
            patterns = analysis.get("patterns", [])
        else:
            patterns = analysis

        topic_counts = {}
        for pattern in patterns:
            if pattern.get("type") == "common_topics":
                common_topics = pattern.get("data", [])
                if common_topics:
                    top_topic = common_topics[0]
                    suggestions.append(
                        f"建议针对'{top_topic[0]}'场景优化系统Prompt，增加相关示例和指导"
                    )

        for pattern in patterns:
            if pattern.get("type") == "long_sessions":
                data = pattern.get("data", {})
                if data.get("percentage", 0) > 30:
                    suggestions.append(
                        "长会话较多，建议在系统Prompt中增加上下文管理指引"
                    )

        for pattern in patterns:
            if pattern.get("type") == "avg_messages":
                avg = pattern.get("data", {}).get("value", 0)
                if avg < 3:
                    suggestions.append(
                        "平均消息数较低，建议优化系统Prompt使其更主动引导用户"
                    )

        if not suggestions:
            suggestions.append("当前会话数据量不足，建议积累更多数据后再进行Prompt优化")

        return suggestions

    def get_optimization_summary(self) -> dict[str, Any]:
        """获取优化摘要"""
        sessions = self.analyze_sessions()
        patterns = self.extract_patterns(sessions)
        suggestions = self.generate_prompt_updates(patterns)
        last_result = self.get_last_result(EvolutionType.PROMPT)

        return {
            "sessions_analyzed": len(sessions),
            "patterns": patterns,
            "suggestions": suggestions,
            "last_analysis": last_result.timestamp if last_result else None,
        }
