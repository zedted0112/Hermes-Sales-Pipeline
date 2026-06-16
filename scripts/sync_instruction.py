#!/usr/bin/env python3
"""Parse goal.md phases and sync instruction.json + Telegram draft from goal + Report."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "Report.json"
INSTRUCTION = ROOT / "instruction.json"
GOAL = ROOT / "goal.md"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _phase_order(phase_id: str) -> tuple[int, int]:
    parts = str(phase_id).split(".")
    try:
        return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    except ValueError:
        return (999, 999)


def _normalize_status(raw: str) -> str:
    s = raw.lower().strip("* ").strip()
    if s in ("done", "complete", "completed"):
        return "done"
    if s in ("next", "in progress", "in_progress", "active", "current"):
        return "in_progress"
    return "pending"


def parse_goal_md(text: str) -> list[dict]:
    """Extract phase rows from goal.md markdown tables."""
    phases: list[dict] = []
    for line in text.splitlines():
        if not line.strip().startswith("|") or "---" in line:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 4:
            continue
        pid_match = re.search(r"\*\*([\d.]+)\*\*", cols[0])
        if not pid_match:
            continue
        pid = pid_match.group(1)
        title = re.sub(r"`", "", cols[1]).strip()
        desc = cols[2].strip()
        status = _normalize_status(cols[3])
        phases.append({"id": pid, "title": title, "description": desc, "status": status, "source": "goal.md"})
    return phases


def _current_focus(text: str) -> str | None:
    m = re.search(r"\*\*Active phase:\s*([\d.]+)\*\*", text)
    return m.group(1) if m else None


def _steps_for_phase(phase_id: str, title: str) -> list[dict]:
    """Concrete sub-steps derived from goal phase titles."""
    catalog = {
        "1.1": [
            {"step": f"Implement list_files in src/hermes_app/tools/builtin.py", "status": "pending"},
            {"step": "Register list_files in create_default_registry()", "status": "pending"},
            {"step": "Test in chat: 'list files in src/hermes_app'", "status": "pending"},
        ],
        "1.2": [
            {"step": "Implement read_file with max_bytes limit (32KB)", "status": "pending"},
            {"step": "Register read_file in tool registry", "status": "pending"},
            {"step": "Test in chat: 'read src/hermes_app/main.py'", "status": "pending"},
        ],
        "1.3": [
            {"step": "Update agent system prompt — when to list vs read vs chat", "status": "pending"},
        ],
        "1.4": [
            {"step": "Run smoke tests for list + read in chat UI", "status": "pending"},
        ],
    }
    steps = catalog.get(phase_id, [{"step": f"Work on phase {phase_id}: {title}", "status": "pending"}])
    out = []
    for i, s in enumerate(steps):
        out.append({
            "phase": phase_id,
            "step": s["step"],
            "status": "in_progress" if i == 0 else "pending",
        })
    return out


def build_pick_options(phases: list[dict], current: str) -> list[dict]:
    """Options user can reply with on Telegram."""
    cur = next((p for p in phases if p["id"] == current), None)
    pending = [p for p in phases if p["status"] == "pending" and _phase_order(p["id"]) >= _phase_order(current)]
    pending.sort(key=lambda p: _phase_order(p["id"]))

    options = []
    if cur:
        options.append({
            "pick": 1,
            "phase": cur["id"],
            "label": f"Continue Phase {cur['id']}: {cur['title']}",
            "description": cur["description"],
        })
    if pending:
        nxt = pending[0]
        options.append({
            "pick": 2,
            "phase": nxt["id"],
            "label": f"Jump to Phase {nxt['id']}: {nxt['title']}",
            "description": nxt["description"],
        })
    options.append({
        "pick": 3,
        "phase": None,
        "label": "Your own priority — reply with free text",
        "description": "Tell me what you want to focus on; I'll update instruction.json",
    })
    return options


def format_telegram(report: dict, instruction: dict, goal_phases: list[dict], pick_options: list[dict]) -> str:
    summary = report.get("summary") or "Project update"
    since = (report.get("changes") or {}).get("since_last_report") or []
    current = instruction.get("roadmap", {}).get("current_phase", "?")
    cur_phase = next((p for p in goal_phases if p["id"] == str(current)), None)

    lines = [
        "Project update",
        "",
        summary,
    ]

    if since:
        lines += ["", "What changed:"]
        for item in since[-3:]:
            lines.append(f"  • {item}")

    lines += ["", f"Goal — Phase {current}" + (f": {cur_phase['title']}" if cur_phase else "")]
    if cur_phase:
        lines.append(f"  {cur_phase['description']}")

    lines += ["", "Recommended next (from goal.md):"]
    for opt in pick_options[:2]:
        lines.append(f"  {opt['pick']}. {opt['label']}")

    lines += [
        "",
        "Your call — reply on Telegram:",
        "  pick 1  → continue current phase",
        "  pick 2  → jump to next phase",
        "  or type your own priority (e.g. 'focus on read_file first')",
    ]

    user_dir = instruction.get("user_input", {}).get("last_directive")
    if user_dir:
        lines += ["", f"Your last choice: {user_dir}"]

    return "\n".join(lines)


def sync() -> dict:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    instruction = json.loads(INSTRUCTION.read_text(encoding="utf-8"))
    goal_text = GOAL.read_text(encoding="utf-8") if GOAL.exists() else ""

    goal_phases = parse_goal_md(goal_text)
    if goal_phases:
        instruction.setdefault("roadmap", {})["phases"] = [
            {k: v for k, v in p.items() if k != "source"} for p in goal_phases
        ]
        instruction["roadmap"]["source"] = "goal.md"

    status = report.get("status") or {}
    current = (
        status.get("current_phase")
        or (report.get("goal") or {}).get("current_phase")
        or _current_focus(goal_text)
        or instruction.get("roadmap", {}).get("current_phase")
        or "1.1"
    )

    roadmap = instruction.setdefault("roadmap", {})
    roadmap["current_phase"] = str(current)
    roadmap["last_synced_at"] = _now()
    roadmap["last_synced_by"] = "hermes-cron-agent"

    # Respect user pick unless Report explicitly advances phase
    user_input = instruction.setdefault("user_input", {})
    if user_input.get("selected_phase") and not status.get("current_phase"):
        current = user_input["selected_phase"]
        roadmap["current_phase"] = current

    cur_order = _phase_order(str(current))
    for phase in roadmap.get("phases") or []:
        pid = str(phase.get("id", ""))
        po = _phase_order(pid)
        if po < cur_order:
            phase["status"] = "done"
        elif pid == str(current):
            phase["status"] = "in_progress"
        elif phase.get("status") != "done":
            phase["status"] = "pending"

    # next_steps from goal for current phase (unless user locked custom steps)
    if not user_input.get("custom_steps_locked"):
        cur_meta = next((p for p in goal_phases if p["id"] == str(current)), None)
        title = cur_meta["title"] if cur_meta else str(current)
        instruction["next_steps"] = _steps_for_phase(str(current), title)

    pick_options = build_pick_options(goal_phases, str(current))
    instruction["proposed_next_steps"] = pick_options

    telegram_body = format_telegram(report, instruction, goal_phases, pick_options)
    instruction["outbound_telegram"] = {
        "generated_at": _now(),
        "body": telegram_body,
        "pick_options": pick_options,
        "reply_hint": "pick 1 | pick 2 | or type your priority",
    }

    maintenance = instruction.setdefault("hermes_self_maintenance", {})
    maintenance.update({
        "updated_at": _now(),
        "updated_by": "hermes-cron-agent",
        "source_files": ["Report.json", "goal.md"],
        "goal_phases_parsed": len(goal_phases),
    })

    INSTRUCTION.write_text(json.dumps(instruction, indent=2) + "\n", encoding="utf-8")

    next_step = None
    for step in instruction.get("next_steps") or []:
        if isinstance(step, dict) and step.get("status") in ("in_progress", "pending"):
            next_step = f"Phase {step.get('phase')}: {step.get('step')}"
            break

    return {
        "ok": True,
        "current_phase": str(current),
        "goal_phases": len(goal_phases),
        "next_step": next_step,
        "pick_options": pick_options,
        "telegram_body": telegram_body,
    }


if __name__ == "__main__":
    print(json.dumps(sync(), indent=2))
    print("\n--- TELEGRAM ---\n")
    print(json.loads(INSTRUCTION.read_text())["outbound_telegram"]["body"])
