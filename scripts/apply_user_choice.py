#!/usr/bin/env python3
"""Apply user choice from Telegram — updates instruction.json next_steps and phase."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTION = ROOT / "instruction.json"
REPORT = ROOT / "Report.json"

sys.path.insert(0, str(ROOT / "scripts"))
from sync_instruction import _steps_for_phase, parse_goal_md, sync  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def apply_pick(pick: int) -> dict:
    instruction = json.loads(INSTRUCTION.read_text(encoding="utf-8"))
    options = instruction.get("proposed_next_steps") or instruction.get("outbound_telegram", {}).get("pick_options") or []
    chosen = next((o for o in options if o.get("pick") == pick), None)
    if not chosen:
        return {"ok": False, "error": f"Invalid pick {pick}. Options: {[o.get('pick') for o in options]}"}

    user_input = instruction.setdefault("user_input", {})
    user_input["last_directive"] = chosen["label"]
    user_input["last_directive_at"] = _now()
    user_input["selected_pick"] = pick

    if chosen.get("phase"):
        user_input["selected_phase"] = chosen["phase"]
        instruction.setdefault("roadmap", {})["current_phase"] = chosen["phase"]
        instruction["next_steps"] = _steps_for_phase(chosen["phase"], chosen.get("label", ""))
        user_input["custom_steps_locked"] = pick != 3
    else:
        user_input["custom_steps_locked"] = False

    instruction["hermes_self_maintenance"] = {
        "updated_at": _now(),
        "updated_by": "hermes-telegram-user-choice",
    }
    INSTRUCTION.write_text(json.dumps(instruction, indent=2) + "\n", encoding="utf-8")

    # Mirror phase into Report.json if present
    if REPORT.exists() and chosen.get("phase"):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        report.setdefault("status", {})["current_phase"] = chosen["phase"]
        report.setdefault("goal", {})["current_phase"] = chosen["phase"]
        report["summary"] = f"User chose Phase {chosen['phase']}: {chosen.get('label', '')}"
        report.setdefault("changes", {}).setdefault("since_last_report", []).append(
            f"User selected pick {pick}: {chosen['label']}"
        )
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    sync()
    return {"ok": True, "applied": chosen}


def apply_text(text: str) -> dict:
    instruction = json.loads(INSTRUCTION.read_text(encoding="utf-8"))
    user_input = instruction.setdefault("user_input", {})
    user_input["last_directive"] = text.strip()
    user_input["last_directive_at"] = _now()
    user_input["selected_pick"] = "custom"
    user_input["custom_steps_locked"] = True

    # Custom step from user text
    current = instruction.get("roadmap", {}).get("current_phase", "1.1")
    instruction["next_steps"] = [
        {"phase": current, "step": text.strip(), "status": "in_progress"},
        {"phase": current, "step": "(derived from your Telegram message)", "status": "pending"},
    ]

    instruction["hermes_self_maintenance"] = {
        "updated_at": _now(),
        "updated_by": "hermes-telegram-user-choice",
    }
    INSTRUCTION.write_text(json.dumps(instruction, indent=2) + "\n", encoding="utf-8")

    if REPORT.exists():
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        report["summary"] = f"User priority: {text.strip()[:120]}"
        report.setdefault("changes", {}).setdefault("since_last_report", []).append(
            f"User custom priority: {text.strip()}"
        )
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    sync()
    return {"ok": True, "applied": text.strip()}


def parse_user_message(msg: str) -> dict:
    msg = msg.strip()
    m = re.match(r"^pick\s*(\d+)$", msg, re.I)
    if m:
        return apply_pick(int(m.group(1)))
    if re.match(r"^(\d+)$", msg):
        return apply_pick(int(msg))
    return apply_text(msg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pick", type=int)
    parser.add_argument("--text", type=str)
    parser.add_argument("message", nargs="?", help="Raw Telegram message e.g. 'pick 1'")
    args = parser.parse_args()

    if args.pick:
        result = apply_pick(args.pick)
    elif args.text:
        result = apply_text(args.text)
    elif args.message:
        result = parse_user_message(args.message)
    else:
        result = {"ok": False, "error": "Provide --pick N, --text, or a message"}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
