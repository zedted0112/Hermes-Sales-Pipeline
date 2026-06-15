---
name: lead-demo-site
description: >-
  Build a business-specific UI-only demo website for a sales lead. Runs
  scripts/build_demo.py from research JSON + gym/salon HTML templates. Requires
  lead-research.json first.
version: 1.2.0
author: Hermes Agent
license: MIT
triggers:
  - demo website
  - demo site for lead
  - build website for
  - preview site for
  - lead-demo-site
  - show them what their site could look like
  - mock website for
metadata:
  hermes:
    tags: [sales, demo, website, landing-page, lead, design]
    category: sales
    related_skills: [lead-research, local-lead-finder, contact-finder, pitch-generator, claude-design, popular-web-designs, web-animation-design, sketch, crm-manager, sales-outreach]
---

# Lead Demo Site

## Name

`lead-demo-site`

## Purpose

Create a **personalized preview website** from `lead-research.json` + a **locked category template** (gym or salon).

The lead should think: *"This is what MY business could look like online."*

## When to Use

- **After `lead-research`** — requires `~/.hermes/leads/research/{slug}.json`
- User says `/lead-demo-site om-sports-and-fitness-center`

If research file missing → run **`lead-research` first**.

## Mode override (critical)

- **Run `build_demo.py` via the terminal tool** — this is the only build path for gym/salon
- **Do NOT** paste Python code, `default_api.write_file`, or f-string templates in chat
- **Do NOT** hand-write full HTML for gym/salon — the script applies `templates/gym-modern.html` or `templates/salon-modern.html`
- **Do NOT** read dev project files (`Report.json`, `AGENTS.md`)
- **Do NOT ask** the user questions — proceed autonomously
- Resolve slug from research `meta.slug` if user passes a partial name

## Build command (mandatory)

After reading research JSON, run **exactly**:

```bash
python3 scripts/build_demo.py {slug}
```

Run from the **skill directory** (`[Skill directory: ...]` in your context), e.g.:

```bash
cd ~/.hermes/skills/lead-demo-site && python3 scripts/build_demo.py om-sports-and-fitness-center
```

Or absolute path:

```bash
python3 ~/.hermes/skills/lead-demo-site/scripts/build_demo.py {slug}
```

**Slug resolution:** partial slugs work (`om-sports-gym` → `om-sports-and-fitness-center.json` if unique).

**Expected stdout:** JSON `{"ok": true, "slug": "...", "template": "gym-modern", "demo_path": "..."}`

If the script exits non-zero, read stderr, fix research JSON or slug, retry once. Only then fall back to manual `write_file`.

## Category templates

| Category | Template | Script picks |
|----------|----------|--------------|
| Gym, fitness, sports center | `templates/gym-modern.html` | `gym-modern` |
| Beauty salon, spa, hair salon | `templates/salon-modern.html` | `salon-modern` |

See `templates/README.md` and `templates/SUBSTITUTION.md` for field mapping.

## Procedure

### Step 0 — Load research

1. Resolve slug (use `meta.slug` from JSON, not a guess)
2. Read `~/.hermes/leads/research/{slug}.json`
3. If missing → `lead-research` first

### Step 1 — Run build script

```bash
python3 scripts/build_demo.py {slug}
```

### Step 2 — Verify

1. Confirm JSON output has `"ok": true`
2. Confirm files exist:
   - `~/.hermes/leads/demos/{slug}/index.html`
   - `~/.hermes/leads/demos/{slug}/meta.json`
3. Tell Captain: `open ~/.hermes/leads/demos/{slug}/index.html`

Optional: `browser_vision` on the file URL.

## Output to Captain

```markdown
## Demo ready: Om Sports And Fitness Center

**Preview:** open ~/.hermes/leads/demos/om-sports-and-fitness-center/index.html

**Template:** gym-modern (from lead-research.json)

**Next:** `/pitch-generator Om Sports And Fitness Center`
```

## Anti-patterns (never do)

- Outputting Python/JS code in chat instead of running `build_demo.py`
- Using `write_file` for gym/salon when the script is available
- Building gym/salon layout from scratch
- Wrong slug (`om-sports-gym` when research slug is `om-sports-and-fitness-center` — script fuzzy-matches)
- Generic lorem ipsum or placeholder business names

## Verification rules

- [ ] `build_demo.py` ran successfully (terminal, not chat code)
- [ ] `meta.json` has `"built_by": "build_demo.py"` and `"template_used"`
- [ ] Business name in `<title>` and hero
- [ ] Saved under `~/.hermes/leads/demos/{slug}/`

## V2

Restaurant/clinic templates, deploy to Vercel.
