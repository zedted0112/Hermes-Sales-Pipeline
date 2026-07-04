# Hermes Sales Pipeline — Web UI

Local-first sales automation dashboard for the Hermes agent. Find local business leads, research them, build template-driven demo websites, publish to GitHub Pages, and generate outreach pitches — all from one UI.

**Live app (local):** `http://127.0.0.1:8765/app`  
**Chat UI:** `http://127.0.0.1:8765/`  
**Repo:** [github.com/zedted0112/Hermes-Sales-Pipeline](https://github.com/zedted0112/Hermes-Sales-Pipeline)

---

## What this app does

Hermes runs a **deterministic, script-based pipeline** — not hand-written HTML in chat. The web UI is a control panel that:

1. Triggers Hermes skills and shell scripts
2. Streams live agent output to a terminal-style panel
3. Reads/writes lead data under `~/.hermes/leads/`
4. Publishes demos to GitHub Pages when requested

```
Lead Finder → Research → Demo Website → Publish → Pitch
```

| Step | UI label | Backend | Output |
|------|----------|---------|--------|
| 1 | Lead Finder | `local-lead-finder` skill via Hermes CLI | Structured leads list (JSON in run log) |
| 2 | Research | `lead-research` skill | `~/.hermes/leads/research/{slug}.json` |
| 3 | Build demo | `build.sh` / `build_demo.py` | `~/.hermes/leads/demos/{slug}/index.html` |
| 4 | Publish | `publish_to_pages.py` | Live URL on GitHub Pages + `meta.json` update |
| 5 | Pitch | `pitch-generator` skill | Outreach draft using demo URL when available |

---

## Start the app

From project root:

```bash
cd "/Users/himalayancoder/DevSpace/Projects/cheetclaw/hermes agent"
. .venv/bin/activate   # if using venv
PYTHONPATH=src python3 -m hermes_app.main chat
```

Open **http://127.0.0.1:8765/app**

Prerequisites:

- Hermes CLI installed and skills loaded (`local-lead-finder`, `lead-research`, `lead-demo-site`, `pitch-generator`)
- For publish: local clone of `hermes-demos` repo + git push auth
- Lead data directory: `~/.hermes/leads/`

---

## UI layout

### Hero + workflow overview

- Marketing hero with pipeline screenshot (`assets/images/home/dashboard.png`)
- **Workflow** section — how skills connect (click cards to jump to a step)
- **Your data** — KPI cards for saved research and built demos

### Pipeline workspace (`#pipeline`)

Two-column layout matching the product mockup:

| Left | Right |
|------|-------|
| Step cards (forms, leads list, slug/template pickers) | **Live Agent Activity** — green monospace log, KPIs, selected lead / slug / status |

#### Guided mode (default)

- URL: `/app#pipeline-guided` or **Start pipeline** from hero
- Shows **one active step at a time**
- Completing a step unlocks the next; finished steps collapse to headers
- Best for first-time runs end-to-end

#### All steps mode (explorer)

- URL: `/app#pipeline` or nav **Pipeline** tab
- All five step cards visible
- Click any step or stepper button to jump
- Best when revisiting a single step (e.g. re-publish, change template)

Toggle **Guided | All steps** at the top of the pipeline section.

---

## Demo templates

Selected in Step 3 (Build demo). Auto-picked from research category when left on **Auto**.

| Value | Label | Category |
|-------|-------|----------|
| `gym-modern` | Gym Classic | Gym / fitness |
| `gym-modern-dark` | Gym Modern-Dark | Gym / fitness |
| `salon-modern` | Salon Classic | Salon / spa |
| `salon-aesthetic` | Salon Aesthetic | Salon / spa |
| `salon-chocolate` | Salon Chocolate Luxury | Beauty parlour |
| `retail-modern` | Retail Modern | Clothing / retail |

Templates live in:

```
templates/sales-lead-pipeline/skills/lead-demo-site/templates/
```

Build manually (outside UI):

```bash
bash templates/sales-lead-pipeline/skills/lead-demo-site/scripts/build.sh {slug} salon-chocolate
python3 templates/.../scripts/publish_to_pages.py {slug}
```

---

## Data on disk

```
~/.hermes/leads/
├── research/{slug}.json     # Research JSON — required before demo build
├── demos/{slug}/
│   ├── index.html           # Generated demo site
│   ├── meta.json            # template_used, demo_url, published_at
│   └── assets/              # e.g. salon-chocolate hero image
└── drafts/                  # Pitch drafts (from pitch-generator)
```

The UI **Refresh** button and `/api/pipeline/state` read from these paths.

---

## Published demos (GitHub Pages)

Demos are copied to the `hermes-demos` repo and deployed via GitHub Actions.

**Base URL:** `https://zedted0112.github.io/hermes-demos/demos/{slug}/`

| Business | Slug | Template |
|----------|------|----------|
| Fitness Villa | `fitness-villa` | gym-modern-dark |
| Bull's Legacy Gym | `bulls-legacy-gym` | gym-modern-dark |
| Arushi Beauty Parlour | `arushi-beauty-parlour` | salon-chocolate |

---

## API (FastAPI)

Served by `src/hermes_app/web/server.py`.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/app` | This UI |
| GET | `/` | Chat UI |
| GET | `/api/health` | Health check |
| GET | `/api/pipeline/state` | Research + demo counts and lists |
| POST | `/api/pipeline/run/start` | Start a pipeline step (`kind`: `lead_finder`, `research`, `demo_build`, `demo_publish`, `pitch`) |
| GET | `/api/pipeline/run/{run_id}?offset=N` | Stream run logs |

Run start body example:

```json
{
  "kind": "demo_build",
  "slug": "arushi-beauty-parlour",
  "template": "salon-chocolate"
}
```

---

## Frontend files

```
web/static/app/
├── index.html          # App shell, hero, workflow, pipeline workspace
├── index.js            # Pipeline logic, API calls, guided/explorer modes
├── css/
│   ├── index.css       # Pipeline inputs, agent panel, step cards
│   └── tailwind-build.css
├── assets/
│   ├── logo/
│   └── images/home/dashboard.png
└── readme.md           # This file
```

### Tailwind note

UI classes are prefixed with `tw-` to avoid clashes. Production uses `tailwind-build.css`.

```bash
# From web/static/app/ if rebuilding Tailwind
npm run build:tailwind
```

### Cache busting

After JS/CSS changes, bump query strings in `index.html`:

```html
<link rel="stylesheet" href="css/index.css?v=5" />
<script src="./index.js?v=10"></script>
```

---

## Typical workflow (first run)

1. **Step 1** — Enter city + category (e.g. `Dehradun`, `Salon`) → **Run**
2. Click a lead in the results list (auto-fills Step 2)
3. **Step 2** — Confirm business/city/category → **Run research**
4. **Step 3** — Pick slug + template → **Build demo**
5. **Step 4** — **Publish** → copy live URL from agent log
6. **Step 5** — **Generate pitch** (uses published demo link when available)

Watch **Live Agent Activity** on the right for `[lead-finder]`, `[lead-research]`, `[build_demo.py]`, `[publish]` lines.

---

## Related docs

| Path | Content |
|------|---------|
| `templates/sales-lead-pipeline/README.md` | Full skill pipeline install + CLI commands |
| `templates/.../lead-demo-site/SKILL.md` | Demo build + publish skill |
| `templates/.../templates/README.md` | HTML template catalog |
| `AGENTS.md` | Hermes bot instructions (chat vs sales mode) |

---

## Architecture (short)

```
Browser (/app)
    │
    ▼
FastAPI (server.py)
    ├── POST /api/pipeline/run/start
    │       ├── hermes chat -s {skill}     (lead_finder, research, pitch)
    │       └── bash build.sh / publish.py (demo_build, demo_publish)
    │
    └── GET /api/pipeline/run/{id}  ← streamed stdout logs
            │
            ▼
    ~/.hermes/leads/  +  hermes-demos repo (Pages)
```

The UI does not embed business logic for demos — **build_demo.py** fills `{{PLACEHOLDERS}}` from research JSON into category HTML templates.
