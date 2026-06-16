#!/usr/bin/env python3
"""Save lead-research.json — Hermes agent must run this (not describe saving).

Usage:
  python3 save_research.py <slug> < path/to/draft.json
  python3 save_research.py <slug> --file draft.json
  python3 save_research.py <slug>   # reads JSON from stdin
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
OUT_DIR = HERMES_HOME / "leads" / "research"


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    meta = data.get("meta") or {}
    if not meta.get("business"):
        errors.append("meta.business required")
    if not meta.get("city"):
        errors.append("meta.city required")
    ui = data.get("content_for_ui") or {}
    headline = ui.get("hero_headline") or ""
    business = meta.get("business") or ""
    if business and business.lower() not in headline.lower():
        errors.append("content_for_ui.hero_headline must include business name")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: save_research.py <slug> [--file path.json]", file=sys.stderr)
        return 1

    slug_arg = sys.argv[1].strip().lower().replace("_", "-")
    file_arg = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--file":
        file_arg = Path(sys.argv[3]).expanduser()

    if file_arg:
        raw = file_arg.read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    if not raw.strip():
        print("Error: no JSON input", file=sys.stderr)
        return 1

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON: {e}", file=sys.stderr)
        return 1

    slug = data.get("meta", {}).get("slug") or slug_arg
    slug = slugify(slug)
    data.setdefault("meta", {})["slug"] = slug
    if not data["meta"].get("researched_at"):
        data["meta"]["researched_at"] = datetime.now(timezone.utc).isoformat()
    data["meta"].setdefault("research_version", "1.0")

    errors = validate(data)
    if errors:
        print("Validation failed:", "; ".join(errors), file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{slug}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "slug": slug, "research_path": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
