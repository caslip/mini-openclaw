from __future__ import annotations

import json
import logging
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from evolution.base import EvolutionBase, EvolutionResult, EvolutionStatus, EvolutionType

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """工作流步骤"""

    tool: str
    input: str
    output: str | None = None
    success: bool = True
    duration_ms: float = 0
    error: str | None = None


@dataclass
class WorkflowExecution:
    """工作流执行记录"""

    task_id: str
    task: str
    steps: list[WorkflowStep] = field(default_factory=list)
    result: str | None = None
    success: bool = True
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    duration_ms: float = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task": self.task,
            "steps": [
                {
                    "tool": s.tool,
                    "input": s.input,
                    "output": s.output,
                    "success": s.success,
                    "duration_ms": s.duration_ms,
                    "error": s.error,
                }
                for s in self.steps
            ],
            "result": self.result,
            "success": self.success,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowExecution":
        return cls(
            task_id=data.get("task_id", ""),
            task=data.get("task", ""),
            steps=[
                WorkflowStep(
                    tool=s.get("tool", ""),
                    input=s.get("input", ""),
                    output=s.get("output"),
                    success=s.get("success", True),
                    duration_ms=s.get("duration_ms", 0),
                    error=s.get("error"),
                )
                for s in data.get("steps", [])
            ],
            result=data.get("result"),
            success=data.get("success", True),
            start_time=data.get("start_time", time.time()),
            end_time=data.get("end_time"),
            duration_ms=data.get("duration_ms", 0),
        )


class WorkflowLogger(EvolutionBase):
    """工作流执行记录器"""

    def __init__(self, base_dir: Path, storage_path: Path | None = None):
        super().__init__(base_dir, storage_path)
        self.workflows_dir = self.storage_path / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        self._current_execution: WorkflowExecution | None = None

    def run(self) -> EvolutionResult:
        """执行工作流分析"""
        start_time = time.time()
        try:
            patterns = self.analyze_patterns()
            suggestions = self.suggest_improvements()

            duration_ms = (time.time() - start_time) * 1000

            result = EvolutionResult(
                type=EvolutionType.WORKFLOW,
                status=EvolutionStatus.COMPLETED,
                data={
                    "patterns": patterns,
                    "suggestions": suggestions,
                },
                duration_ms=duration_ms,
            )

            self.save_result(result)
            logger.info("工作流分析完成")
            return result

        except Exception as e:
            logger.error(f"工作流分析失败: {e}")
            result = EvolutionResult(
                type=EvolutionType.WORKFLOW,
                status=EvolutionStatus.FAILED,
                error=str(e),
            )
            self.save_result(result)
            return result

    def start_execution(self, task_id: str, task: str) -> None:
        """开始记录任务执行"""
        self._current_execution = WorkflowExecution(
            task_id=task_id,
            task=task,
            start_time=time.time(),
        )

    def add_step(self, tool: str, input: str, output: str | None = None, success: bool = True, duration_ms: float = 0, error: str | None = None) -> None:
        """记录执行步骤"""
        if self._current_execution:
            self._current_execution.steps.append(
                WorkflowStep(
                    tool=tool,
                    input=input,
                    output=output,
                    success=success,
                    duration_ms=duration_ms,
                    error=error,
                )
            )

    def end_execution(self, result: str | None = None, success: bool = True) -> None:
        """结束记录任务执行"""
        if self._current_execution:
            self._current_execution.end_time = time.time()
            self._current_execution.duration_ms = (self._current_execution.end_time - self._current_execution.start_time) * 1000
            self._current_execution.result = result
            self._current_execution.success = success
            self._save_execution(self._current_execution)
            self._current_execution = None

    def _save_execution(self, execution: WorkflowExecution) -> None:
        """保存执行记录"""
        if not execution.task_id:
            return

        execution_file = self.workflows_dir / f"{execution.task_id}.json"
        try:
            execution_file.write_text(
                json.dumps(execution.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"保存执行记录失败: {e}")

    def get_execution(self, task_id: str) -> WorkflowExecution | None:
        """获取执行记录"""
        execution_file = self.workflows_dir / f"{task_id}.json"
        if not execution_file.exists():
            return None

        try:
            data = json.loads(execution_file.read_text(encoding="utf-8"))
            return WorkflowExecution.from_dict(data)
        except Exception as e:
            logger.error(f"读取执行记录失败: {e}")
            return None

    def list_executions(self, limit: int = 50) -> list[dict[str, Any]]:
        """列出最近的执行记录"""
        if not self.workflows_dir.exists():
            return []

        executions = []
        for execution_file in sorted(self.workflows_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                data = json.loads(execution_file.read_text(encoding="utf-8"))
                executions.append({
                    "task_id": data.get("task_id"),
                    "task": data.get("task"),
                    "success": data.get("success"),
                    "step_count": len(data.get("steps", [])),
                    "duration_ms": data.get("duration_ms"),
                    "start_time": data.get("start_time"),
                })
            except Exception as e:
                logger.error(f"读取执行记录失败 {execution_file}: {e}")

        return executions

    def analyze_patterns(self) -> list[dict[str, Any]]:
        """分析工作流模式，提取最佳实践"""
        executions = self.list_executions(limit=100)
        if not executions:
            return []

        patterns = []

        tool_counter = Counter()
        total_steps = 0
        successful_runs = 0

        for exec_data in executions:
            total_steps += exec_data.get("step_count", 0)
            if exec_data.get("success"):
                successful_runs += 1

        for exec_data in executions:
            execution_file = self.workflows_dir / f"{exec_data['task_id']}.json"
            try:
                data = json.loads(execution_file.read_text(encoding="utf-8"))
                for step in data.get("steps", []):
                    tool_counter[step.get("tool", "unknown")] += 1
            except Exception:
                pass

        most_used_tools = tool_counter.most_common(10)
        if most_used_tools:
            patterns.append({
                "type": "most_used_tools",
                "description": "最常用的工具",
                "data": [{"tool": tool, "count": count} for tool, count in most_used_tools],
            })

        if executions:
            avg_steps = total_steps / len(executions)
            patterns.append({
                "type": "avg_steps",
                "description": "平均任务步骤数",
                "data": {"value": round(avg_steps, 2)},
            })

            success_rate = successful_runs / len(executions) * 100
            patterns.append({
                "type": "success_rate",
                "description": "任务成功率",
                "data": {"value": round(success_rate, 2)},
            })

        return patterns

    def suggest_improvements(self) -> list[str]:
        """基于历史提出改进建议"""
        suggestions = []

        executions = self.list_executions(limit=50)
        if not executions:
            suggestions.append("暂无工作流数据，建议积累更多执行记录后再进行分析")
            return suggestions

        success_executions = [e for e in executions if e.get("success")]
        if success_executions:
            avg_duration = sum(e.get("duration_ms", 0) for e in success_executions) / len(success_executions)
            slow_tasks = [e for e in success_executions if e.get("duration_ms", 0) > avg_duration * 2]
            if slow_tasks:
                suggestions.append(f"有{len(slow_tasks)}个任务执行时间过长，建议进行性能优化")

        failed_executions = [e for e in executions if not e.get("success")]
        if failed_executions:
            failure_rate = len(failed_executions) / len(executions) * 100
            if failure_rate > 20:
                suggestions.append(f"任务失败率较高({failure_rate:.1f}%)，建议检查错误模式并改进")

        tool_counter = Counter()
        for exec_data in executions:
            execution_file = self.workflows_dir / f"{exec_data['task_id']}.json"
            try:
                data = json.loads(execution_file.read_text(encoding="utf-8"))
                for step in data.get("steps", []):
                    if not step.get("success", True):
                        tool_counter[step.get("tool", "unknown")] += 1
            except Exception:
                pass

        frequent_failures = tool_counter.most_common(5)
        if frequent_failures:
            for tool, count in frequent_failures:
                suggestions.append(f"工具'{tool}'失败{count}次，建议改进错误处理或增加重试机制")

        if not suggestions:
            suggestions.append("当前工作流运行良好，未发现明显改进点")

        return suggestions

    def get_workflow_summary(self) -> dict[str, Any]:
        """获取工作流摘要"""
        patterns = self.analyze_patterns()
        suggestions = self.suggest_improvements()
        executions = self.list_executions(limit=10)
        last_result = self.get_last_result(EvolutionType.WORKFLOW)

        return {
            "recent_executions": len(executions),
            "patterns": patterns,
            "suggestions": suggestions,
            "last_analysis": last_result.timestamp if last_result else None,
        }
