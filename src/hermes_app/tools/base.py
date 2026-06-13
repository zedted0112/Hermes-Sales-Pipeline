"""Tool primitives — schema, context, and result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Outcome of a single tool invocation."""

    ok: bool
    output: Any
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "output": self.output, "error": self.error}


@dataclass
class ToolSpec:
    """Metadata describing a callable tool for the agent."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
