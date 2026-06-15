---
name: contact-finder
description: >-
  Use after local-lead-finder to discover contact channels for a business lead.
  Finds website, email, phone, WhatsApp, Instagram, Facebook, and contact forms
  from public sources. Outputs structured contact JSON. No sending messages.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - find contact
  - contact finder
  - get email for
  - get phone for
  - whatsapp for
  - contact details
  - reach this business
metadata:
  hermes:
    tags: [sales, leads, contact, outreach, prospecting]
    category: sales
    related_skills: [local-lead-finder, lead-research, lead-demo-site, pitch-generator, crm-manager]
---

# Contact Finder

## Name

`contact-finder`

## Description

V1 skill to enrich a lead from `local-lead-finder` with **reachable contact channels**. Input is a business name (+ city). Output is structured contact JSON.

**No sending** — discovery only. Never email, WhatsApp, or DM anyone.

## When to Use

- After `local-lead-finder` produced leads — user wants to reach them
- User says "find contact for Bull's Legacy Gym"
- User provides lead JSON or business name + city
- Before `pitch-generator` — pitches need a channel

**Do not use for:**

- Sending messages (use `pitch-generator` + human approval first)
- Bulk scraping thousands of leads
- Bypassing platform ToS or anti-spam rules

## Mode override

- **Do NOT ask the user questions** — proceed autonomously
- **Do NOT** read dev project files (`Report.json`, `instruction.json`)
- **Never auto-send** any message
- Deliver contact JSON even if some fields are `null`

## Input

| Field | Required | Example |
|-------|----------|---------|
| `business_name` | Yes | Bull's Legacy Gym |
| `city` | Yes | Dehradun |
| `lead_data` | No | JSON from `local-lead-finder` (issues, suggested_services) |

## Procedure

### Step 1 — Search

One `web_search`: `"{business_name} {city} contact phone email instagram"`

### Step 2 — Extract

- `web_extract` on business website, Google Business / Justdial / Sulekha listing, or Facebook/Instagram URL from results
- Look on page for: email, phone, `wa.me`, WhatsApp button, contact form URL, social links

### Step 3 — Secondary search (if needed)

One more search only if email/phone still missing: `"{business_name} {city} justdial"` or `"{business_name} instagram"`

### Step 4 — Normalize & rank channels

| Channel | How to detect |
|---------|---------------|
| `website` | Business-owned URL (not directory) |
| `email` | mailto:, info@, contact@ on site or listing |
| `phone` | tel:, +91, 10-digit Indian mobile |
| `whatsapp` | wa.me link, WhatsApp icon, number labeled WhatsApp |
| `instagram` | instagram.com/handle |
| `facebook` | facebook.com/page |
| `contact_form` | /contact, Typeform, Google Form, WP contact page |

**Best channel rank** (for local businesses — use in `recommended_channel`):

1. WhatsApp
2. Instagram DM
3. Phone call
4. Email
5. Contact form

### Step 5 — Output

Return markdown summary + JSON per [Output Format](#output-format).

## Output Format

```json
{
  "business": "Bull's Legacy Gym",
  "city": "Dehradun",
  "website": null,
  "email": null,
  "phone": "+91xxxxxxxxxx",
  "whatsapp": "+91xxxxxxxxxx",
  "instagram": "https://instagram.com/...",
  "facebook": null,
  "contact_form": null,
  "recommended_channel": "whatsapp",
  "confidence": "medium",
  "sources": ["justdial listing", "instagram bio"],
  "notes": "No dedicated website found. WhatsApp number from Instagram bio."
}
```

See [sample-output.json](sample-output.json).

## Verification Rules

Every output must include:

- [ ] `business` name
- [ ] At least one contact field populated OR explicit `notes` why none found
- [ ] `recommended_channel` based on rank above
- [ ] `sources` — where each field was found
- [ ] No messages sent

## Common Pitfalls

1. **Directory email** — `info@justdial.com` is not the business email; mark null
2. **Asking user** — never ask which URL to check; pick best and extract
3. **Fake confidence** — use `"low"` if only indirect evidence
4. **Auto-send** — forbidden in V1

## V2 (not in scope)

Hunter.io, Apollo, LinkedIn API, automated enrichment databases.
