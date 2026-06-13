"""Refresh Report.json folder tree and bump updated_at (optional maintenance script)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "Report.json"
SKIP = {".git", "__pycache__", ".venv", "node_modules", ".DS_Store"}


def walk_tree(base: Path, prefix: str = "") -> list[str]:
    lines: list[str] = []
    try:
        entries = sorted(base.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except OSError:
        return lines
    for i, entry in enumerate(entries):
        if entry.name in SKIP:
            continue
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(walk_tree(entry, prefix + extension))
    return lines


def main() -> None:
    if not REPORT.exists():
        raise SystemExit(f"Report.json not found at {REPORT}")
    report = json.loads(REPORT.read_text())
    report["project"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    report["folder_structure"]["tree_lines"] = walk_tree(ROOT)
    report["folder_structure"]["generated_at"] = datetime.now(timezone.utc).isoformat()
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Updated {REPORT}")


if __name__ == "__main__":
    main()
