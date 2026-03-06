from __future__ import annotations

from pathlib import Path

import requests
from langchain_core.tools import tool


def make_fetch_url_tool(base_dir: Path):
    @tool
    def fetch_url(url: str) -> str:
        """Fetch the content of a URL and return it as text. HTML is returned as plain text."""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            ctype = response.headers.get("content-type", "")
            if "application/json" in ctype:
                return response.text[:5000]
            text = response.text.replace("\r\n", "\n")
            return text[:5000]
        except Exception as exc:
            return f"fetch_url error: {exc}"

    return fetch_url
