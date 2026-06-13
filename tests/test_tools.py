"""Smoke tests for the tool registry."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hermes_app.tools import create_default_registry


def test_default_tools_registered():
    registry = create_default_registry()
    names = {s.name for s in registry.list_specs()}
    assert "ping" in names
    assert "read_report" in names
    assert "send_telegram" in names


def test_ping_tool():
    registry = create_default_registry()
    result = registry.call("ping", message="hello")
    assert result.ok
    assert result.output["message"] == "hello"
