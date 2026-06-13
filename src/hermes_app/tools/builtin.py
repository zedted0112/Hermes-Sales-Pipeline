"""Built-in tools available to the default agent."""

from __future__ import annotations

import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from hermes_app.tools.base import ToolResult

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = PROJECT_ROOT / "Report.json"


def ping(message: str = "pong") -> ToolResult:
    """Health-check tool — confirms the tool loop is alive."""
    return ToolResult(ok=True, output={"message": message, "ts": datetime.now(timezone.utc).isoformat()})


def read_report() -> ToolResult:
    """Read and parse the live Report.json status file."""
    if not REPORT_PATH.exists():
        return ToolResult(ok=False, output=None, error=f"Report not found: {REPORT_PATH}")
    try:
        data = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        return ToolResult(ok=True, output=data)
    except json.JSONDecodeError as exc:
        return ToolResult(ok=False, output=None, error=str(exc))


def file_info(path: str) -> ToolResult:
    """Return metadata for a file or directory under the project root."""
    target = (PROJECT_ROOT / path).resolve()
    if not str(target).startswith(str(PROJECT_ROOT.resolve())):
        return ToolResult(ok=False, output=None, error="Path must stay inside project root")
    if not target.exists():
        return ToolResult(ok=False, output=None, error=f"Not found: {path}")
    stat = target.stat()
    return ToolResult(
        ok=True,
        output={
            "path": str(target.relative_to(PROJECT_ROOT)),
            "type": "dir" if target.is_dir() else "file",
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        },
    )


def list_tools_dir(subdir: str = "tools/custom") -> ToolResult:
    """List files in a project subdirectory (default: tools/custom)."""
    folder = PROJECT_ROOT / subdir
    if not folder.is_dir():
        return ToolResult(ok=False, output=None, error=f"Not a directory: {subdir}")
    entries = sorted(p.name + ("/" if p.is_dir() else "") for p in folder.iterdir())
    return ToolResult(ok=True, output={"directory": subdir, "entries": entries})


def system_info() -> ToolResult:
    """Return basic runtime info for debugging agent sessions."""
    return ToolResult(
        ok=True,
        output={
            "python": platform.python_version(),
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "project_root": str(PROJECT_ROOT),
        },
    )


def send_telegram(message: str) -> ToolResult:
    """Send a short message via Hermes CLI (requires hermes in PATH)."""
    if not message.strip():
        return ToolResult(ok=False, output=None, error="Message cannot be empty")
    try:
        proc = subprocess.run(
            ["hermes", "send", "--to", "telegram", message[:4000]],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0:
            return ToolResult(ok=False, output=proc.stderr.strip(), error="hermes send failed")
        return ToolResult(ok=True, output=proc.stdout.strip() or "sent")
    except FileNotFoundError:
        return ToolResult(ok=False, output=None, error="hermes CLI not found in PATH")
    except subprocess.TimeoutExpired:
        return ToolResult(ok=False, output=None, error="hermes send timed out")
