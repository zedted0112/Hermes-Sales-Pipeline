---
name: followup-manager
description: >-
  Plan and draft follow-up messages for sales leads. Schedules Day 0, 3, 7, 14
  touchpoints with personalized drafts. Tracks status in lead files. No auto-send.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - follow up
  - followup
  - schedule follow up
  - day 3 follow up
  - no reply
metadata:
  hermes:
    tags: [sales, followup, outreach, pipeline]
    category: sales
    related_skills: [pitch-generator, crm-manager]
---

# Follow-up Manager

## Name

`followup-manager`

## Description

Most sales close on follow-up, not the first message. This skill plans a **4-touch sequence** and drafts each message. V1: drafts + schedule only — **no auto-send**.

## When to Use

- After initial pitch was sent (or approved)
- Lead status is `contacted` with no reply
- User says "plan follow-ups for Bull's Legacy Gym"

## Follow-up schedule

| Day | Type | Tone |
|-----|------|------|
| 0 | Initial outreach | Value-first intro (from pitch-generator) |
| 3 | Friendly nudge | Short, no pressure |
| 7 | Value add | Share tip, case study, or free audit offer |
| 14 | Final / close | Polite close or break-up message |

## Procedure

1. Read lead from `~/.hermes/leads/{slug}.json` if exists, or use provided data
2. Check `last_contact_at` and `status` in CRM record
3. Determine which follow-up day applies (or generate full sequence)
4. Draft message for current day — personalize like pitch-generator
5. Update CRM record with `next_followup_at` and draft
6. Present draft + **approval prompt** (never auto-send)

## WhatsApp follow-up examples

**Day 3:**
```
Hi again! Just floating this back up — happy to do a quick free audit of your gym's online presence whenever works. No pressure 🙂
— Nitin
```

**Day 7:**
```
Hi Bull's Legacy team — thought this might help: gyms in Dehradun that added WhatsApp booking typically see faster trial signups. Still happy to show you a 5-min demo if useful.
— Nitin
```

**Day 14 (close):**
```
Hi — I'll assume timing isn't right for now. If you ever want help with a website or online booking, feel free to reach out. Wishing you a great season! 🙏
— Nitin
```

## Human Approval

Same as pitch-generator:

```
─── FOLLOW-UP DRAFT (Day 3) ───
Approve? reply: approve / reject / edit: ...
```

## Output Format

```json
{
  "business": "Bull's Legacy Gym",
  "sequence_day": 3,
  "channel": "whatsapp",
  "recipient": "+919876543210",
  "body": "...",
  "status": "pending_approval",
  "next_followup_at": "2026-06-18",
  "sequence": [
    {"day": 0, "status": "sent", "sent_at": "2026-06-15"},
    {"day": 3, "status": "pending_approval"},
    {"day": 7, "status": "scheduled"},
    {"day": 14, "status": "scheduled"}
  ]
}
```

See [sample-output.json](sample-output.json).

## Rules

- Max 4 touches per lead in V1 — then mark `closed_no_response`
- Never send more than 1 message per day to same lead
- Stop sequence if lead replies — set status `replied`
- **No bulk automated messaging**

## V2 (not in scope)

Cron auto-send, WhatsApp Business API scheduling, email drip campaigns.
