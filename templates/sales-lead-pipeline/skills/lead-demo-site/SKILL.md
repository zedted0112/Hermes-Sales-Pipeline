---
name: lead-demo-site
description: >-
  Build a business-specific UI-only demo website for a sales lead — not a generic
  template. Requires lead-research.json first. Uses claude-design + popular-web-designs.
  no backend. Feels like what THEIR gym/salon/clinic should look like online.
version: 1.0.0
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

Create a **personalized preview website** so the lead thinks: *"This is what MY business could look like online."*

This is **not** a generic SaaS landing page, not a Stripe clone, not lorem ipsum. It must use the lead's **real business name**, **city**, **category**, and **gaps** from `local-lead-finder`.

**V1:** One `index.html` file, UI only, no backend, no forms that submit anywhere.

## When to Use

- **After `lead-research`** — demo site must load `~/.hermes/leads/research/{slug}.json`
- After `local-lead-finder` + `contact-finder` if research was run in same session
- User says "build a demo site for Bull's Legacy Gym"
- Before `pitch-generator` — pitch can include "I made a preview for you"

If `lead-research.json` does **not** exist for this business → run **`lead-research` first**. Do not build from business name alone.

**Do not use for:**

- Production websites with auth, booking APIs, databases
- Generic portfolio templates unrelated to the lead
- Auto-deploying without Captain seeing the file first

## Required skills (load and follow)

| Skill | Role |
|-------|------|
| **`lead-research`** | **Required first** — `lead-research.json` with UI copy, services, brand |
| **`claude-design`** | Design process, motion discipline, avoid AI slop, verify artifact |
| **`popular-web-designs`** | Load category-fit template — gym: `framer.md` (motion), `spacex.md` (photo-led), `wise.md` (scale hovers) |
| **`web-animation-design`** | Easing, stagger, scroll reveals, `prefers-reduced-motion` — **install from skills.sh if missing** |
| **`sketch`** | Optional: 2 variants if user says "show me options" |

Load `category-briefs.md` from this skill folder for category-specific vibe, sections, and copy angles.

## Mode override

- **Do NOT** read dev project files (`Report.json`, `instruction.json`, `AGENTS.md`)
- **Do NOT ask** "what style do you want?" — infer from **category + business name**
- **Do NOT** use placeholder names like "Acme Gym" or "Your Business Here"
- **Proceed autonomously** from lead JSON or user-provided business details
- Present preview path when done — do not auto-deploy

## Input

**Primary input:** `~/.hermes/leads/research/{slug}.json` from `lead-research`.

Read these fields directly into the HTML:

| Research field | Use in demo |
|----------------|-------------|
| `content_for_ui.hero_headline` | Hero H1 |
| `content_for_ui.hero_subhead` | Hero subtext |
| `content_for_ui.cta_primary` | Main button |
| `content_for_ui.sections[]` | Page sections |
| `offerings.services` | Program/service cards |
| `location.*` | Footer + map area |
| `contact.*` | `tel:` / `wa.me` links |
| `brand_signals.vibe` | Color + layout mood |
| `gaps.demo_should_highlight` | What to emphasize visually |
| `media.image_keywords` | Unsplash/CSS imagery direction |

Fallback (only if no research file): minimum from user message:

| Field | Example |
|-------|---------|
| `business_name` | Bull's Legacy Gym |
| `city` | Dehradun |
| `category` | Gym |

Strongly preferred (from lead-finder):

- `address`
- `issues_found` (drives what the demo **shows off** — e.g. highlight booking CTA if they lack it)
- `suggested_services`
- `phone` / `whatsapp` (real `tel:` and `wa.me` links in demo)

## The golden rule

> The lead should recognize their business in the first 3 seconds.

Use their **name in the hero**, **city in subhead**, **category-appropriate imagery and copy**. The demo sells the **future state** — professional, trustworthy, bookable.

## Procedure

### Step 0 — Load research

1. Resolve `slug` from business name
2. Read `~/.hermes/leads/research/{slug}.json`
3. If missing → stop and run `lead-research` — **do not guess copy**

### Step 1 — Brief (from research file)

From `lead-research.json` + `category-briefs.md`, decide:

- **Vibe** — use `brand_signals.vibe` + category defaults
- **Hero** — use `content_for_ui.hero_headline` and `hero_subhead` **verbatim** (minor grammar ok)
- **Sections** — build from `content_for_ui.sections` + `offerings.services`
- **CTAs** — use `content_for_ui.cta_primary` + gaps from `gaps.demo_should_highlight`

### Step 2 — Design tokens (modern, not generic)

**Mandatory modern craft** — demos must feel 2024+, not 2015 template:

1. Load **`claude-design`** — follow motion discipline (ease-out entrances, stagger, reduced-motion)
2. Load **`web-animation-design`** — timing, easing, scroll-trigger rules
3. Load **`popular-web-designs`** template by category:
   - **Gym / fitness:** `templates/framer.md` (dark cinematic + motion) or `templates/spacex.md` (photo-led hero)
   - **Salon:** `templates/airbnb.md` or `templates/framer.md` (light variant)
   - **Restaurant:** `templates/airbnb.md`
   - **Clinic:** `templates/linear.app.md` (clean, minimal motion)

**Never ship:** Roboto/Oswald defaults, flat `#1a1a2e` purple-gradient slop, `source.unsplash.com` (broken), zero animation, single hero image only.

**Must include:**
- **3+ real images** — `images.unsplash.com/photo-...?w=1200&q=80` with category keywords from `media.image_keywords`
- **Scroll-triggered reveals** — Intersection Observer or CSS `animation-timeline: view()`
- **Micro-interactions** — button scale on hover (1.02–1.05), card lift, nav blur on scroll
- **Staggered hero** — headline words or lines animate in (200–400ms ease-out each)
- **Stats strip** — rating/reviews/hours with subtle count or fade-in
- **Sticky mobile CTA** — WhatsApp or Book bar fixed at bottom on small screens
- **`prefers-reduced-motion: reduce`** — disable non-essential animation

Optional hub skills (install via `hermes skills install` if user wants more motion):
- `skills-sh/connorads/dotfiles/web-animation-design` — **installed by default**
- `skills-sh/patricio0312rev/skills/framer-motion-animator` — React/Framer patterns
- `skills-sh/ailabs-393/ai-labs-claude-skills/frontend-enhancer` — polish pass

Do **not** copy Stripe/Linear look for a local gym unless adapted — use templates for **craft** (spacing, motion, photography), not brand clone.

### Step 3 — Build single HTML file

- **One file:** `index.html` with embedded CSS + JS (scroll reveals, mobile nav, stat counters)
- **Mobile-first** — most leads open on phone; test sticky CTA
- **Real content:** from `lead-research.json` — business name, city, services
- **Contact block:** real `tel:` and `https://wa.me/` links
- **Images:** min 3× `images.unsplash.com` URLs (hero + 2 section photos). No `source.unsplash.com`.
- **Motion:** hero stagger + section reveals + hover micro-interactions (see `web-animation-design`)
- **Typography:** distinctive pair — e.g. Syne/Bebas + DM Sans, or Space Grotesk + Inter. **Not** Roboto/Oswald/Arial.
- **No backend:** forms use `action="#"` or `tel:` / `wa.me`

### Step 4 — Save

```
~/.hermes/leads/demos/{slug}/index.html
~/.hermes/leads/demos/{slug}/meta.json
```

`slug` = lowercase business name, hyphens (e.g. `bulls-legacy-gym`).

`meta.json`:

```json
{
  "business": "Bull's Legacy Gym",
  "city": "Dehradun",
  "category": "Gym",
  "demo_path": "~/.hermes/leads/demos/bulls-legacy-gym/index.html",
  "generated_at": "ISO-8601",
  "lead_source": "local-lead-finder",
  "preview_command": "open ~/.hermes/leads/demos/bulls-legacy-gym/index.html"
}
```

### Step 5 — Verify

1. `browser_navigate` to `file://` path OR tell Captain: `open <path>`
2. Optional: `browser_vision` — confirm business name visible, mobile layout ok
3. Report path + one-line pitch hook: *"I built a preview of what Bull's Legacy could look like online."*

## Section guide by category

See [category-briefs.md](category-briefs.md) for full detail. Quick map:

| Category | Hero | Must-have sections |
|----------|------|-------------------|
| Gym | "{Name} — Train in {City}" | Programs, Trainers, Membership, Location, Book trial CTA |
| Beauty salon | "{Name} — Beauty & Care in {City}" | Services menu, Gallery, Prices teaser, Book appointment |
| Restaurant / café | "{Name} — {Cuisine} in {City}" | Menu highlights, Ambiance, Hours, Reserve table |
| Clinic / dental | "{Name} — Trusted care in {City}" | Services, Doctors, Hours, Book consultation |
| Coaching / academy | "{Name} — Learn in {City}" | Courses, Outcomes, Faculty, Enroll CTA |

## Anti-patterns (never do)

- Generic "Welcome to our website" with no business name
- Stock hero that says "Business Solutions" or "Digital Agency"
- Dark-mode crypto startup aesthetic for a local salon
- Lorem ipsum paragraphs
- Fake testimonials with American names in Dehradun
- Asking user to pick a template before building

## Output to Captain

```markdown
## Demo ready: Bull's Legacy Gym

**Preview:** open ~/.hermes/leads/demos/bulls-legacy-gym/index.html

**Built for:** Gym in Dehradun — highlights missing website/booking gaps with visible CTAs.

**Next:** Run `/pitch-generator` and include: "I created a quick preview of your online presence — happy to share."
```

## Verification rules

- [ ] Business name in `<title>` and hero
- [ ] City or locality mentioned
- [ ] Category-appropriate sections (not generic "Features/Pricing/About")
- [ ] Single `index.html`, no backend
- [ ] Saved under `~/.hermes/leads/demos/{slug}/`
- [ ] `meta.json` written
- [ ] **Modern UI:** motion, 3+ images, distinctive fonts — not generic dark template
- [ ] `prefers-reduced-motion` respected

## V2 (not in scope)

Multi-page sites, deploy to Vercel, real booking widgets, CMS.
