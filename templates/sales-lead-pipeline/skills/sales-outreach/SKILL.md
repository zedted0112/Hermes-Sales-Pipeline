---
name: sales-outreach
description: >-
  Orchestrate the full sales pipeline: lead-finder → contact-finder →
  lead-research → lead-demo-site → pitch-generator → human approval → crm save → followup-manager. Targeted
  local business outreach only. Never bulk auto-send.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - sales outreach
  - full pipeline
  - find lead and pitch
  - outreach pipeline
  - gym outreach dehradun
metadata:
  hermes:
    tags: [sales, outreach, pipeline, orchestration]
    category: sales
    related_skills: [local-lead-finder, contact-finder, lead-research, lead-demo-site, pitch-generator, crm-manager, followup-manager]
---

# Sales Outreach Pipeline

## Name

`sales-outreach`

## Description

Orchestrates the full **Captain-approved** sales workflow for local business leads. Runs skills in order — **never skips human approval before send**.

## Pipeline

```
1. local-lead-finder     → scored leads
2. contact-finder        → email, phone, WhatsApp, social
3. lead-research         → deep dive → lead-research.json (UI brief)
4. lead-demo-site        → run `bash scripts/build.sh {slug}` (terminal only; templates on disk)
5. pitch-generator       → personalized draft (include demo link if built)
6. HUMAN APPROVAL        → Captain: approve / reject / edit
7. crm-manager           → save lead + mark contacted (after manual send)
8. followup-manager      → Day 3/7/14 drafts when no reply
```

## When to Use

- User wants end-to-end: "find gym leads in Dehradun and draft outreach"
- User says "run sales pipeline for Dehradun gyms"

## Orchestration rules

1. Run **one skill at a time** in pipeline order
2. Pass JSON output from each step to the next
3. **Stop at approval gate** — present pitch draft, wait for user
4. **Never auto-send** — V1 sending is manual (copy-paste WhatsApp/email)
5. After user confirms sent, `crm-manager` → status `contacted`
6. **Do not ask** mid-pipeline permission to continue (except approval gate)

## Human approval gate

After `pitch-generator`:

```
═══ CAPTAIN APPROVAL REQUIRED ═══
Business: Bull's Legacy Gym
Channel: WhatsApp (+919876543210)

[draft message]

Reply:
  approve     → save to CRM as contacted (you send manually)
  reject      → discard draft
  edit: ...    → regenerate with edits
```

## Channel priority (local businesses)

1. WhatsApp
2. Instagram DM
3. Phone
4. Email
5. Contact form

## Anti-spam rules (mandatory)

- Max **5 leads per session** in V1
- Max **1 message per lead per day**
- Personalized only — no copy-paste blast
- Stop if lead replies
- Never use automation to bulk message WhatsApp/Instagram/LinkedIn

## Quick commands

| Goal | Command |
|------|---------|
| Full pipeline | `/sales-outreach Dehradun, Gym, 2 leads` |
| Demo site only | `/lead-demo-site bulls-legacy-gym` (after research) |
| Research first | `/lead-research Bull's Legacy Gym, Dehradun` |
| Lead only | `/local-lead-finder City: Dehradun Category: Gym` |
| Contact only | `/contact-finder Bull's Legacy Gym, Dehradun` |
| Pitch only | `/pitch-generator Bull's Legacy Gym` |
| Save lead | `/crm-manager save lead Bull's Legacy Gym` |
| Follow up | `/followup-manager Bull's Legacy Gym day 3` |

## V2 (not in scope)

WhatsApp Business API, email SMTP send, LinkedIn automation, bulk campaigns.
