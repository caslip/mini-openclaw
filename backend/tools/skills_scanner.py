from __future__ import annotations

from pathlib import Path


def _parse_frontmatter(content: str) -> dict[str, str]:
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


def scan_skills(base_dir: Path) -> str:
    skills_dir = base_dir / "skills"
    entries: list[str] = ["<available_skills>"]

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        meta = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = meta.get("name", skill_md.parent.name)
        desc = meta.get("description", "")
        rel = f"./skills/{skill_md.parent.name}/SKILL.md"
        entries.extend(
            [
                "  <skill>",
                f"    <name>{name}</name>",
                f"    <description>{desc}</description>",
                f"    <location>{rel}</location>",
                "  </skill>",
            ]
        )

    entries.append("</available_skills>")
    snapshot = "\n".join(entries)
    (base_dir / "SKILLS_SNAPSHOT.md").write_text(snapshot, encoding="utf-8")
    return snapshot
