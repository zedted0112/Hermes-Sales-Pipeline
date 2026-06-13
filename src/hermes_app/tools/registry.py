"""Tool registry — register, list, and invoke agent tools."""

from __future__ import annotations

from typing import Any, Callable

from hermes_app.tools.base import ToolResult, ToolSpec

ToolFn = Callable[..., ToolResult]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {}
        self._specs: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec, fn: ToolFn) -> None:
        self._tools[spec.name] = fn
        self._specs[spec.name] = spec

    def get(self, name: str) -> ToolFn | None:
        return self._tools.get(name)

    def list_specs(self) -> list[ToolSpec]:
        return list(self._specs.values())

    def schemas(self) -> list[dict[str, Any]]:
        return [s.to_openai_schema() for s in self._specs.values()]

    def call(self, name: str, **kwargs: Any) -> ToolResult:
        fn = self._tools.get(name)
        if fn is None:
            return ToolResult(ok=False, output=None, error=f"Unknown tool: {name}")
        try:
            return fn(**kwargs)
        except TypeError as exc:
            return ToolResult(ok=False, output=None, error=f"Bad arguments for {name}: {exc}")
        except Exception as exc:  # noqa: BLE001 — tool boundary
            return ToolResult(ok=False, output=None, error=f"{name} failed: {exc}")
