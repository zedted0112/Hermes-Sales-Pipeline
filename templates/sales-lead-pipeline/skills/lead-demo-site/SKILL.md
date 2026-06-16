---
name: lead-demo-site
description: >-
  Build demo website for a sales lead by running scripts/build.sh in terminal.
  Uses gym/salon/retail HTML templates + lead-research.json. NEVER write HTML or
  Python in chat — terminal only.
version: 1.3.0
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
    related_skills: [lead-research, local-lead-finder, contact-finder, pitch-generator, crm-manager, sales-outreach]
---

# Lead Demo Site

## Your only job

Run the build script in the **terminal tool**. Templates + Python already exist on disk.

```bash
bash scripts/build.sh {slug}
```

From skill directory (`[Skill directory: ...]`):

```bash
cd ~/.hermes/skills/lead-demo-site && bash scripts/build.sh {slug}
```

## STOP — forbidden actions

| Forbidden | Why |
|-----------|-----|
| Pasting Python (`default_api`, `execute_code`, f-strings) in chat | Does not create files |
| Pasting HTML in chat | Wrong — templates handle layout |
| `write_file` for `index.html` on gym/salon/retail | Use `build.sh` instead |
| Saying "I will generate..." without running terminal | Must run script same turn |

**Success = terminal shows** `SUCCESS: open /path/to/index.html` **and** JSON with `"ok": true`.

## Prerequisites

1. `~/.hermes/leads/research/{slug}.json` must exist (from `lead-research`)
2. If missing → run `lead-research` first, then come back

## Procedure

### Step 1 — Resolve slug

Read research JSON. Use `meta.slug` exactly (e.g. `kashmiri-sons-dehradun`).
Partial slugs work: `kashmiri-sons` if unique.

### Step 2 — Run build (mandatory, same turn)

```bash
bash scripts/build.sh kashmiri-sons-dehradun
```

Alternative:

```bash
python3 scripts/build_demo.py kashmiri-sons-dehradun
```

### Step 3 — Report

Only after script succeeds:

```markdown
## Demo ready: Kashmiri Sons

**Preview:** open ~/.hermes/leads/demos/kashmiri-sons-dehradun/index.html
**Template:** retail-modern (from build_demo.py)
**Next:** /pitch-generator Kashmiri Sons
```

## Category templates (automatic)

| Category | Template key | Visual name |
|----------|--------------|-------------|
| Gym, fitness, sports | `gym-modern` | Gym Classic — orange app-style |
| Gym, fitness, sports | `gym-modern-dark` | Gym Modern-Dark — gold ELITE-style |
| Salon, spa, beauty | `salon-modern` | Salon Classic — soft cream layout |
| Salon, spa, beauty | `salon-aesthetic` | Salon Aesthetic — newsletter-style layout |
| Clothing, boutique, retail | `retail-modern` | Retail — boutique storefront |

By default the script picks template from `meta.category` in research JSON.

For **gym** leads, if Captain has not picked yet:

- Ask once:
  - **Option 1:** Gym Classic (`gym-modern`)
  - **Option 2:** Gym Modern-Dark (`gym-modern-dark`)
- After they answer:

```bash
bash scripts/build.sh {slug} gym-modern
bash scripts/build.sh {slug} gym-modern-dark
```

For **salon** leads, if Captain has not picked yet:

- Ask once:  
  - **Option 1:** Salon Classic (`salon-modern`)  
  - **Option 2:** Salon Aesthetic (`salon-aesthetic`)
- After they answer, run:

```bash
bash scripts/build.sh {slug} salon-modern      # option 1
bash scripts/build.sh {slug} salon-aesthetic   # option 2
```

## Mode override

- Do NOT read dev project files
- Do NOT ask user questions
- Do NOT end turn until `build.sh` succeeds or fails twice

## If build fails

1. Read stderr
2. Fix research JSON or slug
3. Retry `bash scripts/build.sh {slug}` once
4. If still failing — report error to Captain; do not hand-write HTML

## Verification

- [ ] Terminal ran `build.sh` or `build_demo.py`
- [ ] Output contains `"ok": true`
- [ ] `meta.json` has `"built_by": "build_demo.py"`
- [ ] Tell Captain `open {demo_path}`
