# Hermes Sales Pipeline

Agentic sales automation: find local business leads, research them, build template-driven demo websites, publish to GitHub Pages, and generate outreach pitches.

**Repo:** [github.com/zedted0112/Hermes-Sales-Pipeline](https://github.com/zedted0112/Hermes-Sales-Pipeline)  
**Pipeline UI:** `http://127.0.0.1:8765/app`  
**Chat UI:** `http://127.0.0.1:8765/`

---

## What this project does

Hermes runs a **deterministic, script-based pipeline** — demos are built from HTML templates + research JSON, not hand-written in chat.

```
Lead Finder → Research → Demo Website → Publish → Pitch
```

| Step | UI label | Backend | Output |
|------|----------|---------|--------|
| 1 | Lead Finder | `local-lead-finder` skill (Hermes CLI) | Structured leads (JSON in run log) |
| 2 | Research | `lead-research` skill | `~/.hermes/leads/research/{slug}.json` |
| 3 | Build demo | `build.sh` / `build_demo.py` | `~/.hermes/leads/demos/{slug}/index.html` |
| 4 | Publish | `publish_to_pages.py` | GitHub Pages URL + `meta.json` update |
| 5 | Pitch | `pitch-generator` skill | Outreach draft (uses demo URL when published) |

The **web app** triggers skills/scripts and streams live agent output to a terminal-style panel beside the step cards.

---

## Quick start

### 1. Install dependencies

```bash
git clone https://github.com/zedted0112/Hermes-Sales-Pipeline.git
cd Hermes-Sales-Pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` only if you want project-local keys. By default the app reads `GEMINI_API_KEY` from `~/.hermes/.env`.

### 2. Install sales pipeline skills (optional, for CLI)

```bash
./templates/sales-lead-pipeline/scripts/install.sh
```

In Hermes chat: `/reload-skills`

### 3. Run the app

```bash
PYTHONPATH=src python3 -m hermes_app.main chat
```

Open **http://127.0.0.1:8765/app** for the pipeline UI.

**Prerequisites:** Hermes CLI, skills loaded, lead data at `~/.hermes/leads/`. For publish: local `hermes-demos` clone + git push auth.

---

## Project structure

```
├── src/hermes_app/           # FastAPI server, agent loop, tools
│   ├── web/server.py         # Chat + pipeline API routes
│   └── main.py               # Entry: python -m hermes_app.main chat
├── web/static/
│   ├── index.html            # Chat UI (/)
│   └── app/                  # Sales pipeline UI (/app)
│       ├── index.html
│       ├── index.js
│       └── css/
├── templates/sales-lead-pipeline/
│   └── skills/               # local-lead-finder, lead-research, lead-demo-site, pitch-generator
│       └── lead-demo-site/
│           ├── scripts/      # build_demo.py, build.sh, publish_to_pages.py
│           └── templates/    # gym, salon, retail HTML demos
├── scripts/                  # instruction sync, report tools
├── AGENTS.md                 # Bot instructions (dev vs sales mode)
└── goal.md                   # Dev roadmap
```

---

## Pipeline UI

### Layout

| Left | Right |
|------|-------|
| Step cards (forms, leads, slug/template) | **Live Agent Activity** — log, KPIs, selected lead / slug |

### Guided vs All steps

| Mode | How to open | Behavior |
|------|-------------|----------|
| **Guided** (default) | `/app#pipeline-guided` or **Start pipeline** | One step at a time; unlock next on completion |
| **All steps** | `/app#pipeline` or nav **Pipeline** | All five cards visible; jump to any step |

### First run

1. Step 1 — city + category → **Run**
2. Click a lead → auto-fills Step 2
3. Step 2 — **Run research**
4. Step 3 — slug + template → **Build demo**
5. Step 4 — **Publish**
6. Step 5 — **Generate pitch**

---

## Demo templates

| Value | Label | Category |
|-------|-------|----------|
| `gym-modern` | Gym Classic | Gym / fitness |
| `gym-modern-dark` | Gym Modern-Dark | Gym / fitness |
| `salon-modern` | Salon Classic | Salon / spa |
| `salon-aesthetic` | Salon Aesthetic | Salon / spa |
| `salon-chocolate` | Salon Chocolate Luxury | Beauty parlour |
| `retail-modern` | Retail Modern | Clothing / retail |

Templates: `templates/sales-lead-pipeline/skills/lead-demo-site/templates/`

```bash
bash templates/sales-lead-pipeline/skills/lead-demo-site/scripts/build.sh {slug} salon-chocolate
python3 templates/sales-lead-pipeline/skills/lead-demo-site/scripts/publish_to_pages.py {slug}
```

---

## Data on disk

```
~/.hermes/leads/
├── research/{slug}.json
├── demos/{slug}/
│   ├── index.html
│   ├── meta.json          # template_used, demo_url, published_at
│   └── assets/
└── drafts/
```

---

## Published demos

**Base URL:** `https://zedted0112.github.io/hermes-demos/demos/{slug}/`

| Business | Slug | Template |
|----------|------|----------|
| Fitness Villa | `fitness-villa` | gym-modern-dark |
| Bull's Legacy Gym | `bulls-legacy-gym` | gym-modern-dark |
| Arushi Beauty Parlour | `arushi-beauty-parlour` | salon-chocolate |

---

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/app` | Pipeline UI |
| GET | `/` | Chat UI |
| GET | `/api/health` | Health check |
| GET | `/api/pipeline/state` | Research + demo lists |
| POST | `/api/pipeline/run/start` | Start step (`lead_finder`, `research`, `demo_build`, `demo_publish`, `pitch`) |
| GET | `/api/pipeline/run/{run_id}` | Stream logs |

Example:

```json
{
  "kind": "demo_build",
  "slug": "arushi-beauty-parlour",
  "template": "salon-chocolate"
}
```

---

## Architecture

```
Browser (/app)
    │
    ▼
FastAPI (src/hermes_app/web/server.py)
    ├── POST /api/pipeline/run/start
    │       ├── hermes chat -s {skill}
    │       └── bash build.sh / publish_to_pages.py
    │
    └── GET /api/pipeline/run/{id}  ← streamed stdout
            │
            ▼
    ~/.hermes/leads/  +  hermes-demos (GitHub Pages)
```

**build_demo.py** fills `{{PLACEHOLDERS}}` from research JSON into category HTML templates.

---

## Related docs

| Path | Content |
|------|---------|
| `templates/sales-lead-pipeline/README.md` | Skill pipeline install + CLI |
| `templates/.../lead-demo-site/SKILL.md` | Demo build + publish |
| `templates/.../templates/README.md` | HTML template catalog |
| `AGENTS.md` | Hermes bot (chat vs sales mode) |
| `web/static/app/readme.md` | Frontend-only notes |

---

## License

See repository for license terms.
