from __future__ import annotations

import pytest

from tools.fetch_url_tool import make_fetch_url_tool

pytestmark = pytest.mark.network


def test_fetch_valid_url(base_dir):
    tool = make_fetch_url_tool(base_dir)
    result = tool.run("https://httpbin.org/get")
    assert "fetch_url error" not in result
    assert len(result) > 0


def test_fetch_invalid_url(base_dir):
    tool = make_fetch_url_tool(base_dir)
    # Connect to a localhost port that is almost certainly not listening;
    # this triggers a ConnectionRefusedError before any DNS lookup.
    result = tool.run("http://127.0.0.1:19999")
    assert "fetch_url error" in result


def test_truncation(base_dir):
    """Response should be truncated to at most 5000 characters."""
    tool = make_fetch_url_tool(base_dir)
    # httpbin.org/stream/100 returns a streamed response with many lines
    result = tool.run("https://www.gutenberg.org/files/1342/1342-0.txt")
    assert len(result) <= 5000
