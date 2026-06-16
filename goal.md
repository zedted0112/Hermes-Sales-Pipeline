# Hermes Agent App — Project Goal

## Vision

Build a **chat agent** that talks naturally with the user and **calls tools only when needed**. The agent should decide: answer from context, or invoke a tool to fetch real data from the project.

This is not a one-shot code generator. It is a **persistent conversational agent** with a small, reliable tool arsenal, structured reporting (`Report.json`), and automatic Telegram updates when work is logged.

---

## What we are building

| Layer | Purpose |
|-------|---------|
| **Chat UI** | User types messages in a browser (`http://127.0.0.1:8765`) |
| **Agent loop** | Gemini + tool-calling — multi-turn until a reply is ready |
| **Tool arsenal (basic)** | Small set of focused tools the agent can invoke |
| **Report.json** | Live status — summary, changes, health, current phase |
| **Watcher → Telegram** | When Report.json changes, Hermes sends a summary to your phone |
| **goal.md** | Source of truth for roadmap and phased next steps |
| **instruction.json** | Tells Hermes how to read Report + goal and what to say on Telegram |

---

## Tool arsenal (target for Phase 1)

Keep it **basic**. The agent should be able to:

1. **Call a tool** — generic tool-calling loop (done)
2. **List files** — list contents of a directory in the project
3. **Read file** — read a text file and return contents (with size limits)

Optional later: `file_info`, `ping`, `update_report` (already exist for ops/reporting).

The agent must **choose** when to list vs read vs reply without tools.

---

## Phased roadmap

### Phase 1 — Core chat + file tools

| Phase | Title | Description | Status |
|-------|-------|-------------|--------|
| **1.0** | Scaffold + chat loop | Chat UI, agent loop, Report.json, Telegram watcher | **done** |
| **1.1** | `list_files` tool | Agent can list files/dirs in any project path (sandboxed) | **next** |
| **1.2** | `read_file` tool | Agent can read text files with max size guard | pending |
| **1.3** | Prompt + tool routing | System prompt teaches when to list vs read vs chat | pending |
| **1.4** | Smoke tests | Chat: "list src/", "read main.py" — verify tool use | pending |

### Phase 2 — Reliability

| Phase | Title | Description | Status |
|-------|-------|-------------|--------|
| **2.1** | Error handling | Clear tool errors surfaced to user in chat | pending |
| **2.2** | Session memory | Remember last N turns across chat session | pending |
| **2.3** | Report sync | `update_report` sets `current_phase` from goal.md | pending |

### Phase 3 — Expand (later)

| Phase | Title | Description | Status |
|-------|-------|-------------|--------|
| **3.1** | Write file tool | Agent can propose/save file edits (with guardrails) | pending |
| **3.2** | Custom tools dir | Load tools from `tools/custom/` dynamically | pending |
| **3.3** | Hermes gateway bridge | Optional: same agent on Telegram natively | pending |

---

## How to chat and work with your bot

You have **two chat surfaces** plus **passive Telegram reports**:

### 1. Web chat (project agent with tools)
```bash
PYTHONPATH=src python3 -m hermes_app.main chat
```
Open http://127.0.0.1:8765 — this agent has `update_report`, Gemini tool loop, and auto-updates `Report.json`.

### 2. Telegram — Hermes gateway bot
Message your bot on Telegram. After this fix it knows the project (cwd + `AGENTS.md` + channel prompt).

**Say things like:**
| You type | Bot should |
|----------|------------|
| `what's next?` | Read `goal.md` + `instruction.json` |
| `sync instruction` | Run `python3 scripts/sync_instruction.py` |
| `pick 1` / `pick 2` | Run `apply_user_choice.py` after a watcher alert |
| `status` | Read `Report.json` |

**Do not** expect it to know the project if gateway cwd was wrong — now fixed in `~/.hermes/config.yaml` → `terminal.cwd`.

Restart after config change: `hermes gateway restart`

### 3. Telegram watcher (automatic)
When **anything** updates `Report.json`, cron runs every ~1 min → formatted summary to your phone with pick 1 / pick 2 options. **No need to run cron manually.**

---

## Current focus

**Active phase: 1.1** — implement `list_files` so the agent can answer "what's in this folder?"

After 1.1 ships, update `Report.json` → `status.current_phase` → `1.2` and mark 1.1 done in `instruction.json` roadmap.

---

## Success criteria (Phase 1 complete)

- [ ] User chats "hi" → friendly reply + Report updated
- [ ] User asks "list files in src" → agent calls `list_files` → returns listing
- [ ] User asks "read src/hermes_app/main.py" → agent calls `read_file` → returns content
- [ ] Each meaningful turn updates Report.json → Telegram summary within ~1 min
- [ ] Telegram alert includes **what changed** + **next step from goal** (phase id + title)

---

## Principles

1. **Small tools, used well** — prefer 3 reliable tools over 20 flaky ones
2. **Report is the heartbeat** — every meaningful agent action logs to Report.json
3. **Phased delivery** — one phase at a time (1.1, 1.2, …), never "do everything"
4. **goal.md drives next_steps** — instruction.json and Report.json reflect current phase from here
