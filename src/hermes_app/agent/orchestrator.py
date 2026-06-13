"""Agent orchestration — routes tasks and dispatches tool calls."""

from __future__ import annotations

from typing import Any

from hermes_app.tools.base import ToolResult
from hermes_app.tools.registry import ToolRegistry
from hermes_app.tools import create_default_registry


class AgentOrchestrator:
    """Coordinates agent turns, tool calls, and handoffs."""

    def __init__(self, name: str = "default", registry: ToolRegistry | None = None) -> None:
        self.name = name
        self.registry = registry or create_default_registry()

    def list_tools(self) -> list[str]:
        return [s.name for s in self.registry.list_specs()]

    def call_tool(self, name: str, **kwargs: Any) -> ToolResult:
        return self.registry.call(name, **kwargs)

    def run(self, task: str) -> str:
        tools = ", ".join(self.list_tools()) or "none"
        return f"[{self.name}] task={task!r} | tools: {tools}"
