# Sales Lead Pipeline — Hermes Skills Template

Reusable Hermes skill pack for **any local business lead**: find → contact → research → demo site → pitch → CRM → follow-up.

Works for gym, salon, restaurant, clinic, coaching — category is passed per run.

## Install

```bash
./templates/sales-lead-pipeline/scripts/install.sh
```

Optional motion skill (recommended for demo sites):

```bash
hermes skills install skills-sh/connorads/dotfiles/web-animation-design --yes
```

Then in Hermes chat: `/reload-skills`

## Pipeline (any lead)

Replace `{business}`, `{city}`, `{category}`, `{slug}`:

| Step | Command |
|------|---------|
| 1. Find leads | `/local-lead-finder City: {city}, Category: {category}` |
| 2. Contacts | `/contact-finder {business}, {city}` |
| 3. Research | `/lead-research {business}, {city}` → `~/.hermes/leads/research/{slug}.json` |
| 4. Demo site | `/lead-demo-site {slug}` → `~/.hermes/leads/demos/{slug}/index.html` |
| 5. Pitch | `/pitch-generator {business}` |
| 6. Save | `/crm-manager` save lead |
| 7. Follow-up | `/followup-manager` when no reply |

**One-shot bundle:** `/sales-pipeline` (loads all skills)

## Build (Hermes agent)

**Always run the script** — do not write HTML manually for gym/salon:

```bash
```bash
bash ~/.hermes/skills/lead-demo-site/scripts/build.sh {slug}
# or
python3 ~/.hermes/skills/lead-demo-site/scripts/build_demo.py {slug}
```
```

Example:

```bash
python3 ~/.hermes/skills/lead-demo-site/scripts/build_demo.py om-sports-and-fitness-center
open ~/.hermes/leads/demos/om-sports-and-fitness-center/index.html
```

Templates with `{{PLACEHOLDERS}}` live in `templates/`. The script fills them from `lead-research.json`.

## Category demo templates (v1.2)

| Category | HTML template | Reference |
|----------|---------------|-----------|
| Gym / fitness | `gym-modern.html` | Gym Classic — schedule, plans, booking modal |
| Gym / fitness | `gym-modern-dark.html` | Gym Modern-Dark — gold ELITE-style layout |
| Beauty salon | `salon-modern.html` | Salon Classic — original Shear Genius layout |
| Beauty salon | `salon-aesthetic.html` | Salon Aesthetic — newsletter-style, stats + newsletter |
| Clothing / retail | `skills/lead-demo-site/templates/retail-modern.html` | Kashmiri Sons |

Hermes loads these via `skill_view` and swaps in lead content — see `templates/SUBSTITUTION.md`.

## Output paths (per lead)

```
~/.hermes/leads/
├── {slug}.json              # CRM record
├── research/{slug}.json     # UI brief (required before demo)
├── demos/{slug}/index.html  # Personalized preview
└── drafts/{slug}-*.json     # Pitch drafts
```

**Slug rule:** lowercase business name, hyphens — e.g. `Bull's Legacy Gym` → `bulls-legacy-gym`

## Built-in Hermes skills used

- `claude-design` — design process + motion
- `popular-web-designs` — category templates (framer, spacex, airbnb, …)
- `web-animation-design` — easing, scroll reveals (install from skills.sh)

## Customize

Edit skills under `templates/sales-lead-pipeline/skills/`, then re-run `install.sh`.

Category vibes: `skills/lead-demo-site/category-briefs.md`

Sample schemas: each skill folder has `sample-*.json`.
