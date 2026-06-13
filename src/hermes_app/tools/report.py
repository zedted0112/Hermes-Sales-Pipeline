"""Update Report.json — triggers the Hermes file watcher → Telegram."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hermes_app.tools.base import ToolResult

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = PROJECT_ROOT / "Report.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def update_report(
    summary: str,
    change_note: str,
    change_type: str = "chat",
) -> ToolResult:
    """Append a change note and refresh summary/timestamps in Report.json."""
    if not summary.strip():
        return ToolResult(ok=False, output=None, error="summary cannot be empty")
    if not change_note.strip():
        return ToolResult(ok=False, output=None, error="change_note cannot be empty")

    if not REPORT_PATH.exists():
        return ToolResult(ok=False, output=None, error=f"Report not found: {REPORT_PATH}")

    try:
        report: dict[str, Any] = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ToolResult(ok=False, output=None, error=str(exc))

    ts = _now_iso()
    report.setdefault("project", {})["updated_at"] = ts
    report["summary"] = summary.strip()

    changes = report.setdefault("changes", {})
    changes["change_type"] = change_type
    changes["last_change_at"] = ts
    changes["changed_by"] = "hermes-app-agent"

    since: list[str] = list(changes.get("since_last_report") or [])
    since.append(change_note.strip())
    changes["since_last_report"] = since[-10:]

    chat_log = report.setdefault("chat_log", {})
    entries: list[dict[str, str]] = list(chat_log.get("entries") or [])
    entries.append({"at": ts, "note": change_note.strip()})
    chat_log["entries"] = entries[-20:]
    chat_log["last_interaction_at"] = ts

    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return ToolResult(
        ok=True,
        output={
            "updated": True,
            "summary": summary.strip(),
            "change_note": change_note.strip(),
            "watcher": "Report.json saved — Telegram alert within ~1 min via Hermes cron",
        },
    )
