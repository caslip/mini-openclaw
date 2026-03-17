from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from evolution.base import EvolutionBase, EvolutionResult, EvolutionStatus, EvolutionType
from tools.skills_scanner import scan_skills

logger = logging.getLogger(__name__)


class SkillDiscovery(EvolutionBase):
    """技能自动发现器"""

    def __init__(self, base_dir: Path, storage_path: Path | None = None):
        super().__init__(base_dir, storage_path)
        self.skills_dir = base_dir / "skills"
        self._watcher_thread: threading.Thread | None = None
        self._running = False
        self._last_scan_time: float = 0

    def run(self) -> EvolutionResult:
        """执行技能发现"""
        start_time = time.time()
        try:
            skills = self.scan_skills_dir()
            registered = self._trigger_scan_skills()

            duration_ms = (time.time() - start_time) * 1000

            result = EvolutionResult(
                type=EvolutionType.SKILL,
                status=EvolutionStatus.COMPLETED,
                data={
                    "discovered_skills": skills,
                    "registered": registered,
                    "total_count": len(skills),
                },
                duration_ms=duration_ms,
            )

            self.save_result(result)
            logger.info(f"技能发现完成，发现 {len(skills)} 个技能")
            return result

        except Exception as e:
            logger.error(f"技能发现失败: {e}")
            result = EvolutionResult(
                type=EvolutionType.SKILL,
                status=EvolutionStatus.FAILED,
                error=str(e),
            )
            self.save_result(result)
            return result

    def scan_skills_dir(self) -> list[dict[str, Any]]:
        """扫描skills目录，发现新技能"""
        if not self.skills_dir.exists():
            logger.warning(f"Skills目录不存在: {self.skills_dir}")
            return []

        discovered = []
        known_skills = self._load_known_skills()

        for skill_md in sorted(self.skills_dir.glob("*/SKILL.md")):
            try:
                skill_info = self._parse_skill(skill_md)
                is_new = skill_info["path"] not in known_skills

                skill_info["is_new"] = is_new
                skill_info["last_modified"] = skill_md.stat().st_mtime

                discovered.append(skill_info)

                if is_new:
                    known_skills[skill_info["path"]] = {
                        "name": skill_info["name"],
                        "hash": skill_info["content_hash"],
                    }

            except Exception as e:
                logger.error(f"解析技能失败 {skill_md}: {e}")

        self._save_known_skills(known_skills)
        self._last_scan_time = time.time()

        return discovered

    def _parse_skill(self, skill_md: Path) -> dict[str, Any]:
        """解析SKILL.md文件"""
        content = skill_md.read_text(encoding="utf-8")

        meta = self._parse_frontmatter(content)
        name = meta.get("name", skill_md.parent.name)
        description = meta.get("description", "")

        content_hash = hashlib.md5(content.encode()).hexdigest()

        return {
            "name": name,
            "description": description,
            "path": str(skill_md.parent.relative_to(self.base_dir)),
            "location": f"./skills/{skill_md.parent.name}/SKILL.md",
            "content_hash": content_hash,
            "content_preview": content[:200] if content else "",
        }

    def _parse_frontmatter(self, content: str) -> dict[str, str]:
        """解析frontmatter"""
        if not content.startswith("---"):
            return {}

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}

        meta = {}
        for line in parts[1].splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()

        return meta

    def _load_known_skills(self) -> dict[str, Any]:
        """加载已知技能列表"""
        known_file = self.storage_path / "known_skills.json"
        if not known_file.exists():
            return {}

        try:
            return json.loads(known_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"加载已知技能失败: {e}")
            return {}

    def _save_known_skills(self, skills: dict[str, Any]) -> None:
        """保存已知技能列表"""
        known_file = self.storage_path / "known_skills.json"
        try:
            known_file.write_text(
                json.dumps(skills, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"保存已知技能失败: {e}")

    def _trigger_scan_skills(self) -> bool:
        """触发scan_skills重新生成快照"""
        try:
            scan_skills(self.base_dir)
            return True
        except Exception as e:
            logger.error(f"触发scan_skills失败: {e}")
            return False

    def watch_for_changes(self) -> None:
        """监听技能目录变化"""
        if self._running:
            logger.warning("文件监听已在运行中")
            return

        self._running = True
        self._watcher_thread = threading.Thread(
            target=self._watch_loop,
            daemon=True,
        )
        self._watcher_thread.start()
        logger.info("技能目录文件监听已启动")

    def stop_watching(self) -> None:
        """停止监听"""
        self._running = False
        if self._watcher_thread:
            self._watcher_thread.join(timeout=5)
        logger.info("技能目录文件监听已停止")

    def _watch_loop(self) -> None:
        """监听循环"""
        import time

        last_mtimes = self._get_file_mtimes()

        while self._running:
            time.sleep(5)

            current_mtimes = self._get_file_mtimes()

            changed = False
            for path, mtime in current_mtimes.items():
                if path not in last_mtimes or last_mtimes[path] != mtime:
                    changed = True
                    logger.info(f"检测到技能文件变化: {path}")

            for path in list(last_mtimes.keys()):
                if path not in current_mtimes:
                    changed = True
                    logger.info(f"检测到技能文件删除: {path}")

            if changed:
                self.scan_skills_dir()
                self._trigger_scan_skills()

            last_mtimes = current_mtimes

    def _get_file_mtimes(self) -> dict[str, float]:
        """获取所有技能文件的修改时间"""
        mtimes = {}
        if not self.skills_dir.exists():
            return mtimes

        for skill_md in self.skills_dir.glob("*/SKILL.md"):
            mtimes[str(skill_md)] = skill_md.stat().st_mtime

        return mtimes

    def get_skills_summary(self) -> dict[str, Any]:
        """获取技能摘要"""
        discovered = self.scan_skills_dir()
        last_result = self.get_last_result(EvolutionType.SKILL)

        return {
            "total_skills": len(discovered),
            "skills": discovered,
            "last_discovery": last_result.timestamp if last_result else None,
            "watcher_running": self._running,
        }
