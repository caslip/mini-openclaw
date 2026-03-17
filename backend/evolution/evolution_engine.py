from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Any

from evolution.base import EvolutionResult, EvolutionStatus, EvolutionType
from evolution.skill_discovery import SkillDiscovery
from evolution.prompt_optimizer import PromptOptimizer
from evolution.workflow_logger import WorkflowLogger

logger = logging.getLogger(__name__)


class EvolutionEngine:
    """进化引擎，协调各子系统"""

    def __init__(self, base_dir: Path, storage_path: Path | None = None):
        self.base_dir = base_dir
        self.storage_path = storage_path or base_dir / "evolution_data"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.skill_discovery = SkillDiscovery(base_dir, storage_path)
        self.prompt_optimizer = PromptOptimizer(base_dir, storage_path)
        self.workflow_logger = WorkflowLogger(base_dir, storage_path)

        self._scheduler_thread: threading.Thread | None = None
        self._running = False
        self._schedule_config: dict[str, Any] = {
            "skill_discovery": {"enabled": True, "interval": 3600},
            "prompt_evolution": {"enabled": True, "interval": 86400},
            "workflow_evolution": {"enabled": True, "interval": 604800},
        }
        self._last_runs: dict[str, float] = {}

    def run_skill_discovery(self) -> EvolutionResult:
        """执行技能发现"""
        logger.info("执行技能发现...")
        result = self.skill_discovery.run()
        self._last_runs["skill_discovery"] = time.time()
        return result

    def run_prompt_evolution(self) -> EvolutionResult:
        """执行Prompt进化"""
        logger.info("执行Prompt进化...")
        result = self.prompt_optimizer.run()
        self._last_runs["prompt_evolution"] = time.time()
        return result

    def run_workflow_evolution(self) -> EvolutionResult:
        """执行工作流进化"""
        logger.info("执行工作流进化...")
        result = self.workflow_logger.run()
        self._last_runs["workflow_evolution"] = time.time()
        return result

    def auto_evolve(self, mode: str = "all") -> dict[str, Any]:
        """自动执行进化"""
        results = {}

        if mode in ("all", "skill"):
            try:
                results["skill_discovery"] = self.run_skill_discovery().to_dict()
            except Exception as e:
                logger.error(f"技能发现失败: {e}")
                results["skill_discovery"] = {"error": str(e)}

        if mode in ("all", "prompt"):
            try:
                results["prompt_evolution"] = self.run_prompt_evolution().to_dict()
            except Exception as e:
                logger.error(f"Prompt进化失败: {e}")
                results["prompt_evolution"] = {"error": str(e)}

        if mode in ("all", "workflow"):
            try:
                results["workflow_evolution"] = self.run_workflow_evolution().to_dict()
            except Exception as e:
                logger.error(f"工作流进化失败: {e}")
                results["workflow_evolution"] = {"error": str(e)}

        return results

    def start_scheduler(self, config: dict[str, Any] | None = None) -> None:
        """启动定时调度"""
        if config:
            self._schedule_config.update(config)

        self._running = True
        self._scheduler_thread = threading.Thread(target=self._schedule_loop, daemon=True)
        self._scheduler_thread.start()
        logger.info("进化调度器已启动")

    def stop_scheduler(self) -> None:
        """停止定时调度"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        self.skill_discovery.stop_watching()
        logger.info("进化调度器已停止")

    def _schedule_loop(self) -> None:
        """调度循环"""
        while self._running:
            try:
                self._check_and_run()
            except Exception as e:
                logger.error(f"进化调度错误: {e}")
            time.sleep(60)

    def _check_and_run(self) -> None:
        """检查并执行到期的进化任务"""
        now = time.time()

        for task_name, task_config in self._schedule_config.items():
            if not task_config.get("enabled", True):
                continue

            interval = task_config.get("interval", 3600)
            last_run = self._last_runs.get(task_name, 0)

            if now - last_run >= interval:
                if task_name == "skill_discovery":
                    self.run_skill_discovery()
                elif task_name == "prompt_evolution":
                    self.run_prompt_evolution()
                elif task_name == "workflow_evolution":
                    self.run_workflow_evolution()

    def get_status(self) -> dict[str, Any]:
        """获取进化状态"""
        last_skill = self.skill_discovery.get_last_result(EvolutionType.SKILL)
        last_prompt = self.prompt_optimizer.get_last_result(EvolutionType.PROMPT)
        last_workflow = self.workflow_logger.get_last_result(EvolutionType.WORKFLOW)

        return {
            "running": self._running,
            "schedule_config": self._schedule_config,
            "last_runs": self._last_runs,
            "last_results": {
                "skill_discovery": last_skill.to_dict() if last_skill else None,
                "prompt_evolution": last_prompt.to_dict() if last_prompt else None,
                "workflow_evolution": last_workflow.to_dict() if last_workflow else None,
            },
            "summaries": {
                "skills": self.skill_discovery.get_skills_summary(),
                "prompt": self.prompt_optimizer.get_optimization_summary(),
                "workflow": self.workflow_logger.get_workflow_summary(),
            },
        }

    def update_schedule_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """更新调度配置"""
        self._schedule_config.update(config)
        return self._schedule_config


evolution_engine = EvolutionEngine(Path(__file__).resolve().parent.parent)
