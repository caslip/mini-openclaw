from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Bootstrap: inject graph.memory_logger directly into sys.modules BEFORE any
# tool imports, to avoid triggering graph/__init__.py which pulls in agent.py
# (which requires langgraph / langchain_ollama to be installed).
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).parent.parent

if "graph" not in sys.modules:
    _graph_stub = types.ModuleType("graph")
    sys.modules["graph"] = _graph_stub

if "graph.memory_logger" not in sys.modules:
    _ml_spec = importlib.util.spec_from_file_location(
        "graph.memory_logger",
        _BACKEND_DIR / "graph" / "memory_logger.py",
    )
    _ml_mod = importlib.util.module_from_spec(_ml_spec)
    sys.modules["graph.memory_logger"] = _ml_mod
    _ml_spec.loader.exec_module(_ml_mod)
    # also expose it on the stub package object
    sys.modules["graph"].memory_logger = _ml_mod  # type: ignore[attr-defined]


@pytest.fixture
def base_dir(tmp_path):
    """Create a minimal project directory structure for tool testing."""
    for d in ["memory/logs", "workspace", "skills", "knowledge"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "memory" / "MEMORY.md").write_text("# 长期记忆\n", encoding="utf-8")
    return tmp_path
