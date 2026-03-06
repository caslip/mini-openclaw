from __future__ import annotations

from tools.python_repl_tool import make_python_repl_tool


def test_expression_return(base_dir):
    tool = make_python_repl_tool(base_dir)
    result = tool.run("1 + 2")
    assert result == 3


def test_print_capture(base_dir):
    tool = make_python_repl_tool(base_dir)
    result = tool.run("print('hello')")
    assert "hello" in str(result)


def test_multi_statement(base_dir):
    tool = make_python_repl_tool(base_dir)
    result = tool.run("x = 5\nx")
    assert result == 5


def test_error_handling(base_dir):
    tool = make_python_repl_tool(base_dir)
    result = tool.run("1/0")
    assert "ZeroDivisionError" in str(result)


def test_sanitize_input(base_dir):
    """Backtick-wrapped code should be sanitized and executed correctly."""
    tool = make_python_repl_tool(base_dir)
    result = tool.run("```python\n1 + 1\n```")
    assert result == 2
