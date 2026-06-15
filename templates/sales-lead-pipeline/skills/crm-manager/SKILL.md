---
name: crm-manager
description: >-
  Local JSON CRM for sales leads. Save, update, and track lead pipeline status
  (new, contacted, replied, won, lost). Stores leads in ~/.hermes/leads/. No
  external CRM integration in V1.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - save lead
  - update lead status
  - crm
  - pipeline
  - lead status
  - mark as contacted
  - mark as replied
metadata:
  hermes:
    tags: [sales, crm, pipeline, leads]
    category: sales
    related_skills: [local-lead-finder, contact-finder, lead-research, lead-demo-site, pitch-generator, followup-manager]
---

# CRM Manager

## Name

`crm-manager`

## Description

Lightweight **file-based CRM** for the sales outreach pipeline. All leads live in `~/.hermes/leads/` as JSON files. No HubSpot, Airtable, or external APIs in V1.

## Storage

```
~/.hermes/leads/
├── bulls-legacy-gym.json      # one file per lead (slug from business name)
├── research/
│   └── bulls-legacy-gym.json  # from lead-research (UI brief)
├── demos/
│   └── bulls-legacy-gym/
│       └── index.html         # from lead-demo-site
├── drafts/
│   └── bulls-legacy-gym-whatsapp-2026-06-15.json
└── pipeline.json              # optional index of all leads
```

## Lead status flow

```
new → contacted → replied → won
                ↘ lost
                ↘ closed_no_response
```

| Status | Meaning |
|--------|---------|
| `new` | Found by lead-finder, not yet contacted |
| `contacted` | Pitch sent or approved draft marked sent |
| `replied` | Lead responded — pause follow-ups |
| `won` | Deal closed |
| `lost` | Not interested |
| `closed_no_response` | 14-day sequence exhausted |

## Procedure

### Save new lead

After `local-lead-finder` + `contact-finder`:

1. Create `~/.hermes/leads/{slug}.json` merging lead + contact data
2. Set `status: new`, `created_at`, `updated_at`
3. Confirm save path to user

### Update status

When user says "mark Bull's Legacy as contacted":

1. Read lead file
2. Update `status`, `updated_at`, optional `notes`
3. Append to `history` array

### List pipeline

Read `pipeline.json` or scan `~/.hermes/leads/*.json` — summarize by status.

## Lead file schema

```json
{
  "id": "bulls-legacy-gym",
  "business": "Bull's Legacy Gym",
  "city": "Dehradun",
  "category": "Gym",
  "status": "new",
  "opportunity_score": 9,
  "issues_found": ["No website", "No online booking"],
  "suggested_services": ["Website", "WhatsApp Booking"],
  "contact": {
    "website": null,
    "email": null,
    "phone": "+919876543210",
    "whatsapp": "+919876543210",
    "instagram": "https://instagram.com/...",
    "recommended_channel": "whatsapp"
  },
  "assets": {
    "research_path": "~/.hermes/leads/research/bulls-legacy-gym.json",
    "demo_path": "~/.hermes/leads/demos/bulls-legacy-gym/index.html"
  },
  "outreach": {
    "last_pitch_at": null,
    "last_channel": null,
    "next_followup_at": null,
    "sequence_day": 0
  },
  "history": [
    {"at": "2026-06-15", "event": "lead_created", "source": "local-lead-finder"}
  ],
  "created_at": "2026-06-15T10:00:00+05:30",
  "updated_at": "2026-06-15T10:00:00+05:30"
}
```

See [sample-lead.json](sample-lead.json).

## Rules

- One JSON file per business (slug: lowercase, hyphens)
- Never delete history — append events
- Never auto-send outreach from CRM actions
- Create `~/.hermes/leads/` if missing

## V2 (not in scope)

Airtable, Notion, HubSpot sync, web dashboard.
