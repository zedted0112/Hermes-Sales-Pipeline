---
name: lead-research
description: >-
  Deep research on a sales lead before building a demo website. Gathers business
  identity, services, location, brand signals, reviews, and UI copy from public
  sources. Saves lead-research.json via scripts/save_research.py (terminal). No generic guesses.
version: 1.1.0
author: Hermes Agent
license: MIT
triggers:
  - research lead
  - dig into lead
  - gather data for website
  - lead research
  - deep dive on
  - business intelligence for
  - prepare demo data for
metadata:
  hermes:
    tags: [sales, research, leads, intelligence, demo-prep]
    category: sales
    related_skills: [local-lead-finder, contact-finder, lead-demo-site, pitch-generator]
---

# Lead Research

## Name

`lead-research`

## Purpose

**Dig deep** on one lead and collect everything needed to build a **personalized demo website** — not generic filler.

Output is a structured `lead-research.json` that `lead-demo-site` **must read before building HTML**.

Think: mini creative brief + fact sheet written from public data only.

## When to Use

- **Always before** `lead-demo-site` when personalization matters
- After `local-lead-finder` (+ optional `contact-finder`)
- User says "research Bull's Legacy Gym for a demo site"

**Do not use for:**

- Sending messages to the business
- Storing data in external CRMs (use `crm-manager` after)
- Inventing facts not found in sources

## Mode override

- **Do NOT ask the user questions** — research autonomously
- **Do NOT** read dev project files (`Report.json`, `AGENTS.md`)
- **Do NOT invent** owner names, years founded, or prices — use `null` or `"unknown"`
- **Do NOT stop** because one source failed — combine snippets from multiple sources
- **Do NOT end turn until research JSON is saved on disk** — run `save_research.py` via terminal
- **Do NOT** describe saving in chat without running the save script
- Mark uncertain fields `"confidence": "low"` per field where needed

## Input

| Field | Source |
|-------|--------|
| `business_name` | User or lead-finder |
| `city` | User or lead-finder |
| `category` | User or lead-finder |
| `lead_json` | Optional — full lead-finder entry |
| `contact_json` | Optional — contact-finder entry |

## Research procedure

### Step 1 — Baseline search

`web_search`: `"{business_name}" {city} {category}`

Note: address snippets, phone, hours, rating, directory links.

### Step 2 — Directory extract

`web_extract` on best URLs from step 1 (priority order):

1. Justdial / Sulekha / IndiaMART listing
2. Google Maps / JoonSquare / Practo (if category fits)
3. Facebook page
4. Instagram profile
5. Existing website (if any)

Extract: services list, hours, phone, area, review quotes, photos URLs if visible in HTML.

### Step 3 — Social & brand signals

If Instagram/Facebook found:

- Bio text → tagline candidates
- Post themes → `brand_signals.vibe` (e.g. "community fitness", "bridal focus")
- Colors from profile imagery if describable (warm gold, neon green, etc.)

One extra search only if gaps remain: `"{business_name}" {city} reviews services"`

### Step 4 — Synthesize UI brief

Fill `content_for_ui` using **only gathered facts**:

- `hero_headline` — must include **business name**
- `hero_subhead` — city + top 2–3 real services or category hook
- `cta_primary` — match gap (e.g. "Book Free Trial" if no booking)
- `sections[]` — 3–5 section titles + bullet content from real offerings
- `testimonial_snippets` — only paraphrase from real review text; else empty array

### Step 5 — Save output (terminal only)

**You MUST save the file by running the terminal** — not by describing it in chat.

**Option A — write_file then save script:**

1. `write_file` → `~/.hermes/skills/lead-research/drafts/{slug}.json` (full JSON)
2. Terminal:

```bash
python3 scripts/save_research.py {slug} --file drafts/{slug}.json
```

**Option B — pipe JSON via terminal:**

```bash
python3 scripts/save_research.py {slug} <<'EOF'
{paste full JSON here}
EOF
```

**Success = stdout:** `{"ok": true, "slug": "...", "research_path": "..."}`

Create directory if needed: `mkdir -p ~/.hermes/leads/research`

Final path: `~/.hermes/leads/research/{slug}.json`

### Step 6 — Handoff

Tell Captain:

```
Research saved: ~/.hermes/leads/research/bulls-legacy-gym.json
Ready for: /lead-demo-site (will auto-load this file)
```

## Output schema

```json
{
  "meta": {
    "business": "Bull's Legacy Gym",
    "city": "Dehradun",
    "category": "Gym",
    "slug": "bulls-legacy-gym",
    "researched_at": "ISO-8601",
    "research_version": "1.0"
  },
  "identity": {
    "display_name": "Bull's Legacy | Unisex Gym",
    "tagline": null,
    "owner_name": null,
    "year_established": null,
    "business_type": "unisex gym"
  },
  "location": {
    "address": "2 Keshav Road, Kanwali Road, near Laxman Police Chowki",
    "area": "Kanwali Road",
    "city": "Dehradun",
    "state": "Uttarakhand",
    "pin": "248001",
    "landmark": "near Laxman Police Chowki"
  },
  "contact": {
    "phone": "+919759816924",
    "whatsapp": null,
    "email": null,
    "website": null,
    "instagram": null,
    "facebook": null,
    "recommended_channel": "phone"
  },
  "offerings": {
    "services": ["Weight training", "Cardio", "Personal training"],
    "products": [],
    "price_hints": [],
    "hours": "Mon-Sat 6am-10pm (verify)"
  },
  "brand_signals": {
    "vibe": ["local", "no-frills", "neighborhood gym"],
    "tone_words": ["strong", "community", "accessible"],
    "colors_observed": [],
    "competitor_context": "Several gyms on Kanwali Road corridor"
  },
  "reviews": {
    "google_count": 35,
    "rating": null,
    "sample_quotes": []
  },
  "gaps": {
    "from_lead_finder": ["No website", "No online booking", "No social media"],
    "demo_should_highlight": ["Book free trial CTA", "WhatsApp bar", "Programs section"]
  },
  "content_for_ui": {
    "hero_headline": "Bull's Legacy — Train Hard in Dehradun",
    "hero_subhead": "Unisex gym on Kanwali Road • Strength • Cardio • Personal training",
    "cta_primary": "Book Free Trial",
    "cta_secondary": "Call Now",
    "sections": [
      {
        "id": "programs",
        "title": "Our Programs",
        "items": ["Strength training", "Cardio zone", "Personal training"]
      },
      {
        "id": "location",
        "title": "Visit Us",
        "body": "2 Keshav Road, Kanwali Road, Dehradun"
      }
    ],
    "footer_tagline": "Bull's Legacy Gym — Dehradun"
  },
  "media": {
    "logo_url": null,
    "image_urls": [],
    "image_keywords": ["indian gym interior", "fitness training dehradun"]
  },
  "sources": [
    {"url": "...", "type": "justdial", "fields_used": ["phone", "address"]}
  ],
  "confidence": "medium"
}
```

See [sample-research.json](sample-research.json).

## Field rules

| Field | Rule |
|-------|------|
| `services` | Only list services explicitly mentioned in sources |
| `hero_headline` | Must contain business name |
| `sample_quotes` | Max 2 short quotes; paraphrase if needed; cite source |
| `colors_observed` | Only if clearly stated or obvious from described branding |
| `price_hints` | Only if prices appear on listings — never guess |

## Verification rules

Before saving:

- [ ] `meta.business` and `meta.city` set
- [ ] `content_for_ui.hero_headline` includes business name
- [ ] At least 2 of: address, phone, services, hours populated OR `notes` explains gaps
- [ ] `sources` lists every URL used
- [ ] `gaps.demo_should_highlight` ties to lead-finder issues
- [ ] File saved to `~/.hermes/leads/research/{slug}.json`
- [ ] No fabricated owner names or fake testimonials

## Handoff to lead-demo-site

`lead-demo-site` **must**:

1. Read `~/.hermes/leads/research/{slug}.json` if it exists
2. Use `content_for_ui`, `offerings`, `location`, `contact`, `brand_signals`, `media` verbatim where possible
3. If research file missing, run `lead-research` first — do not build from name alone

## Common pitfalls

1. **Stopping early** — one failed extract ≠ done; try next source
2. **Generic hero** — "Welcome to the best gym" without business name
3. **Inventing services** — don't add "CrossFit" unless listed
4. **Skipping save** — must run `save_research.py`; saying "saved" without file = failure
5. **Asking user** — forbidden; use best public data

## V2 (not in scope)

Screenshot brand colors, logo download, automated competitor analysis.
