from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool


def make_search_knowledge_tool(base_dir: Path):
    knowledge_dir = base_dir / "knowledge"

    @tool
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base for documents relevant to the query. Returns top matching excerpts."""
        if not knowledge_dir.exists():
            return "knowledge directory not found."

        matches: list[str] = []
        for file in knowledge_dir.rglob("*"):
            if file.is_file() and file.suffix.lower() in {".md", ".txt"}:
                text = file.read_text(encoding="utf-8", errors="ignore")
                if query.lower() in text.lower():
                    matches.append(f"{file.name}: {text[:300]}")
            if len(matches) >= 3:
                break
        return "\n\n".join(matches) if matches else "No relevant knowledge found."

    return search_knowledge_base
