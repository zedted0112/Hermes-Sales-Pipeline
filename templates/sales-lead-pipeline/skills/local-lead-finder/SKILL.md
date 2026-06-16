---
name: local-lead-finder
description: >-
  Use when finding local business leads with weak online presence for digital
  services sales. Given a city and business category, discovers businesses,
  scores opportunity (0-10), and produces a lead report. No CRM or outreach.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - find local leads
  - local lead finder
  - local lead generator
  - lead generator
  - get me a lead
  - find businesses in
  - sales opportunities
  - poor online presence
  - city and category
  - dehradun
  - gym leads
metadata:
  hermes:
    tags: [leads, sales, local-business, prospecting, digital-presence]
    category: sales
    related_skills: [contact-finder, lead-research, lead-demo-site, pitch-generator, crm-manager, sales-outreach, maps]
---

# Local Lead Finder

## Name

`local-lead-finder`

## Description

V1 workflow for identifying local businesses with poor online presence and turning them into scored sales opportunities. Input is a **city** and **business category**. Output is a structured lead report per business.

No CRM, databases, outreach automation, or external API integrations in V1. Use public web search and publicly visible business information only.

## When to Use

- User asks to find local leads, prospects, or sales opportunities
- User provides a city and business category (e.g. "Dehradun", "Gym")
- User says `City: X` and `Category: Y`
- User wants to score businesses on digital presence gaps
- User wants a report of businesses that need websites, booking, or social media help

**Do not use for:**

- Sending emails, WhatsApp messages, or automated outreach
- CRM sync, lead storage, or pipeline management
- Voice agents or call automation
- Paid API scraping (Google Maps API, Apify) — reserved for V2

## Mode override

When this skill is active:

- **Do NOT** read `Report.json`, `instruction.json`, `goal.md`, or `AGENTS.md`
- **Do NOT** run dev scripts or start coding
- **Do NOT** discuss pick 1/pick 2 or project phases
- **Ask only if inputs are missing**:
  - If the user did **not** provide a clear city and category (or provided only one), you MUST ask exactly one short question to collect both.
  - After you get the answer, proceed autonomously and do not ask further questions.
- Otherwise, **do NOT ask the user questions** — no "which result should I explore?", no "do you have a preference?". **Proceed autonomously to the final report.**
- **First action:** one `web_search` for `"{category} in {city}"` (e.g. `gyms in Dehradun`)
- **Second action:** `web_extract` on the best directory/listing URL from results (Justdial, Sulekha, datagemba, vfitnessclub, etc.)
- **Third action:** pick 2 small/local business names from extract or snippets; one `web_search` per business if needed
- **Always deliver the scored report** — use best available evidence; mark uncertain signals as `"unable to verify"` but **never stop to ask the user**

## Procedure

### Step 1 — Confirm inputs

Required:

| Input | Example |
|-------|---------|
| City | Dehradun |
| Business category | Gym |

If missing, ask exactly once in this format (no extra text):

```
Which city and what business category should I find leads for?
Reply like: City: Dehradun, Category: Gym
```

Optional (defaults if omitted):

| Input | Default |
|-------|---------|
| Number of leads | 5 |
| Output format | Markdown report + JSON |

### Step 2 — Find businesses

**Search budget (2-lead request):**
1. `web_search` — `"{category} in {city}"` (one query only)
2. `web_extract` — top directory/listing URL from step 1
3. Up to 2 more `web_search` — one per chosen business name

Do **not** run parallel unrelated searches (no yoga if category is Gym). Do **not** ask the user to pick URLs.

V1 sources (no API keys):

1. **Web search** — e.g. `"gyms in Dehradun"`
2. **web_extract** on directory pages (Justdial, Sulekha, datagemba, vfitnessclub, FITPASS listings)
3. **Per-business search** — `"<gym name> Dehradun website instagram"`

Aim for **2–5 distinct businesses** per user request. Prefer small/local operators over large chains.

Record for each business:

- Business name
- Address or area (if found)
- Website URL (or note "none found")
- Phone / WhatsApp (if visible)
- Social profiles (Instagram, Facebook, etc.)
- Google review count (approximate if exact count unavailable)
- Online booking link or form (if any)

### Step 3 — Analyze digital presence

| Signal | How to assess |
|--------|---------------|
| Website | Search `"<business name> <city>"`; visit URL if found |
| Website quality | Outdated if: old copyright (3+ years), non-mobile layout, broken links, no HTTPS, stale content |
| Online booking | Appointment widget, booking URL, Calendly, class schedule with signup |
| WhatsApp | `wa.me` link, WhatsApp button, or number labeled WhatsApp on listing |
| Social media | Profile exists; **inactive** = no post in 90+ days or only 0–2 posts total |
| Google reviews | **Low** = fewer than 20 reviews |

Only flag issues supported by observed evidence. If uncertain, note `"unable to verify"` and do not add score for that signal. **Still produce the report** — imperfect data is acceptable in V1.

### Step 4 — Score each business

Apply [Scoring Logic](#scoring-logic). Sum applicable points, then **cap at 10**.

### Step 5 — Map issues to suggested services

| Issue | Suggested service |
|-------|-------------------|
| No website | Website |
| Outdated website | Website redesign |
| No online booking | Online booking / WhatsApp booking |
| No WhatsApp contact | WhatsApp Business setup |
| Inactive social media | Social media setup / management |
| Low Google review count | Google Business Profile optimization |

Include 1–3 services per business, matched to the highest-impact issues.

### Step 6 — Generate report

Produce:

1. **Summary** — city, category, date, total leads, top opportunity (highest score)
2. **Per-business entries** — use [Output Format](#output-format)
3. **JSON block** — machine-readable array matching `sample-output.json` schema

Sort businesses by opportunity score (highest first).

## Scoring Logic

Add points for each confirmed issue. **Maximum score: 10** (cap after summing).

| Issue | Points |
|-------|--------|
| No website | +5 |
| Website looks outdated | +3 |
| No online booking | +2 |
| No WhatsApp contact | +2 |
| Inactive social media | +2 |
| Low Google review count | +1 |

**Rules:**

- **No website** and **outdated website** are mutually exclusive — apply only one.
- Do not double-count the same gap under different labels.
- If raw sum exceeds 10, set `opportunity_score` to 10.
- Score 8–10 = hot lead; 5–7 = warm; 1–4 = low priority.

## Output Format

### Markdown (per business)

```markdown
### Business: XYZ Gym

**Opportunity Score:** 9/10

**Issues Found:**
- No website
- No online booking
- Inactive Instagram

**Suggested Service:**
- Website
- WhatsApp Booking
- Social Media Setup

**Reason:**
Business appears to have low digital presence and would benefit from an online customer acquisition system.
```

### JSON schema

```json
{
  "meta": {
    "city": "Dehradun",
    "category": "Gym",
    "generated_at": "ISO-8601",
    "lead_count": 5
  },
  "leads": [
    {
      "business_name": "XYZ Gym",
      "address": "optional",
      "opportunity_score": 9,
      "issues_found": ["No website", "No online booking", "Inactive Instagram"],
      "suggested_services": ["Website", "WhatsApp Booking", "Social Media Setup"],
      "reason": "Business appears to have low digital presence and would benefit from an online customer acquisition system.",
      "signals": {
        "has_website": false,
        "website_outdated": false,
        "has_online_booking": false,
        "has_whatsapp": false,
        "social_active": false,
        "google_review_count": 8
      },
      "score_breakdown": {
        "no_website": 5,
        "no_online_booking": 2,
        "inactive_social_media": 2
      }
    }
  ]
}
```

See [sample-output.json](sample-output.json) for a full example.

## Verification Rules

Before delivering the report, confirm **every lead entry** includes:

- [ ] **Business name** — real, identifiable business (not a placeholder)
- [ ] **Opportunity score** — integer 1–10 with cap applied
- [ ] **Issues found** — at least one issue, each backed by observed evidence
- [ ] **Suggested services** — at least one service mapped from issues
- [ ] **Reason** — short explanation tying gaps to sales opportunity

Report-level checks:

- [ ] City and category match the user request
- [ ] Leads are sorted by score (descending)
- [ ] No CRM/outreach actions were taken
- [ ] JSON output validates against the schema above

If any check fails, fix the report before presenting to the user.

## Common Pitfalls

1. **Scoring without evidence** — only add points for signals you actually observed.
2. **Chains as leads** — skip national franchises with polished websites.
3. **Exceeding max score** — always cap at 10.
4. **Both no-website and outdated-website** — pick one.
5. **Asking the user mid-workflow** — never ask which URL to visit or for permission to continue.
6. **Skipping JSON** — always include structured output for future tooling.

## V2 Expansion (not in scope)

Reserved for later: Google Maps API, Apify scrapers, lead database, CRM export, email/WhatsApp outreach, voice agents. V1 must work with web search only.
