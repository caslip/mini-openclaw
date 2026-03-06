from __future__ import annotations

from tools.search_knowledge_tool import make_search_knowledge_tool


def test_match_found(base_dir):
    (base_dir / "knowledge" / "python_guide.md").write_text(
        "Python is a great language.", encoding="utf-8"
    )
    tool = make_search_knowledge_tool(base_dir)
    result = tool.run("Python")
    assert "python_guide.md" in result
    assert "Python" in result


def test_no_match(base_dir):
    (base_dir / "knowledge" / "doc.md").write_text("Hello world.", encoding="utf-8")
    tool = make_search_knowledge_tool(base_dir)
    result = tool.run("不存在的关键词XYZ")
    assert "No relevant knowledge found" in result


def test_max_results(base_dir):
    for i in range(5):
        (base_dir / "knowledge" / f"file{i}.md").write_text(
            f"Python file {i}", encoding="utf-8"
        )
    tool = make_search_knowledge_tool(base_dir)
    result = tool.run("Python")
    # At most 3 results — count occurrences of ".md:" in result
    assert result.count(".md:") <= 3


def test_non_text_files_ignored(base_dir):
    (base_dir / "knowledge" / "binary.pdf").write_bytes(b"Python PDF content fake")
    (base_dir / "knowledge" / "real.md").write_text("no match here", encoding="utf-8")
    tool = make_search_knowledge_tool(base_dir)
    result = tool.run("Python")
    assert "binary.pdf" not in result


def test_knowledge_dir_not_found(tmp_path):
    """If knowledge/ doesn't exist, return helpful error."""
    tool = make_search_knowledge_tool(tmp_path)
    result = tool.run("anything")
    assert "knowledge directory not found" in result
