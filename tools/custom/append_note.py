"""Example custom tool — append a note to data/notes.log."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from hermes_app.tools.base import ToolResult

NOTES_FILE = Path(__file__).resolve().parents[2] / "data" / "notes.log"


def append_note(text: str) -> ToolResult:
    if not text.strip():
        return ToolResult(ok=False, output=None, error="Note text cannot be empty")
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now(timezone.utc).isoformat()} | {text.strip()}\n"
    with NOTES_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return ToolResult(ok=True, output={"saved_to": str(NOTES_FILE.relative_to(NOTES_FILE.parents[2]))})
