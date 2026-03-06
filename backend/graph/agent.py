from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Generator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from config import get_rag_mode
from tools import get_all_tools

from .prompt_builder import build_system_prompt
from .session_manager import SessionManager


class AgentManager:
    def __init__(self) -> None:
        self.base_dir: Path | None = None
        self.llm: ChatOllama | None = None
        self.tools: list = []
        self.session_manager: SessionManager | None = None
        self._current_session_id: str = ""

    def initialize(self, base_dir: Path, memory_indexer=None) -> None:
        self.base_dir = base_dir
        self.llm = ChatOllama(
            model="qwen3.5:9b",
            base_url="http://122.224.127.38:11434",
            api_key="ollama",
            temperature=0.7,
        )
        self.tools = get_all_tools(
            base_dir,
            memory_indexer=memory_indexer,
            get_session_id=lambda: self._current_session_id,
        )
        self.session_manager = SessionManager(base_dir)

    def _build_messages(self, message: str, history: list[dict[str, Any]]) -> list[Any]:
        if self.base_dir is None:
            raise RuntimeError("AgentManager is not initialized.")

        system_prompt = build_system_prompt(self.base_dir, rag_mode=get_rag_mode())
        built: list[Any] = [SystemMessage(content=system_prompt)]
        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                built.append(HumanMessage(content=content))
            elif role == "assistant":
                built.append(AIMessage(content=content))
        built.append(HumanMessage(content=message))
        return built

    def astream(
        self,
        message: str,
        history: list[dict[str, Any]],
        session_id: str = "",
    ) -> Generator[dict[str, Any], None, None]:
        if self.llm is None:
            raise RuntimeError("AgentManager is not initialized.")

        self._current_session_id = session_id or str(uuid.uuid4())
        built_messages = self._build_messages(message, history)

        agent = create_react_agent(self.llm, self.tools)

        final_text = ""

        for event in agent.stream(
            {"messages": built_messages},
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                messages = node_output.get("messages", [])
                for msg in messages:
                    if node_name == "tools":
                        tool_name = getattr(msg, "name", "tool")
                        tool_content = getattr(msg, "content", "")
                        yield {
                            "type": "tool_end",
                            "tool": tool_name,
                            "content": str(tool_content)[:500],
                        }

                    elif node_name == "agent":
                        tool_calls = getattr(msg, "tool_calls", [])
                        for tc in tool_calls:
                            yield {
                                "type": "tool_start",
                                "tool": tc.get("name", ""),
                                "args": tc.get("args", {}),
                            }

                        text_content = getattr(msg, "content", "")
                        if text_content and not tool_calls:
                            final_text = text_content
                            for token in text_content.split():
                                yield {"type": "token", "content": token + " "}

        yield {
            "type": "done",
            "content": final_text,
            "session_id": self._current_session_id,
        }


agent_manager = AgentManager()
