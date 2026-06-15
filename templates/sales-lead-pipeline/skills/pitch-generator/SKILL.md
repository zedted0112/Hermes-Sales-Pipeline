---
name: pitch-generator
description: >-
  Generate personalized sales outreach drafts from lead + contact data. Creates
  channel-specific pitches (WhatsApp, Instagram, email, phone script). Human
  approval required before any send. No auto-send in V1.
version: 1.0.0
author: Hermes Agent
license: MIT
triggers:
  - generate pitch
  - write outreach
  - personalized message
  - sales pitch
  - draft message
  - whatsapp message for lead
metadata:
  hermes:
    tags: [sales, outreach, pitch, copywriting, whatsapp]
    category: sales
    related_skills: [local-lead-finder, contact-finder, lead-research, lead-demo-site, crm-manager, followup-manager]
---

# Pitch Generator

## Name

`pitch-generator`

## Description

Turns lead analysis + contact data into **personalized outreach drafts**. References specific gaps (no website, no booking, inactive Instagram) — never generic "Hi Sir, need website?"

**V1: draft only.** Present to Captain for approval. **Never auto-send.**

## When to Use

- After `contact-finder` has contact channels
- User says "write a pitch for Bull's Legacy Gym"
- User provides lead JSON + contact JSON

## Required inputs

| Input | Source |
|-------|--------|
| Business name | lead-finder |
| Issues found | lead-finder (`issues_found`, `suggested_services`) |
| Best channel | contact-finder (`recommended_channel`) |
| Demo site built | `lead-demo-site` (`meta.json` → `pitch_hook`, `preview_command`) |
| Sender name | Default: **Nitin** (override if user specifies) |

## Mode override

- **Do NOT auto-send** email, WhatsApp, Instagram, or any message
- **Always end with approval prompt** — see [Human Approval](#human-approval)
- **Do NOT ask** "should I write a pitch?" — write it
- Personalize using **observed issues** from lead data

## Pitch rules

### Do

- Reference the business by name
- Mention 1–2 specific gaps you observed
- Offer 2–3 concrete services from `suggested_services`
- Soft CTA: "free audit", "quick chat", "would you be open to..."
- Match tone to channel (WhatsApp = short; email = slightly formal)

### Don't

- Generic spam: "Hi Sir, need website?"
- False claims ("I visited your gym yesterday")
- Pressure tactics or bulk-sales language
- Send without approval

## Channel templates

### WhatsApp (primary for local gyms)

```
Hi Bull's Legacy Team 👋

I came across your gym in Dehradun — great local presence! I noticed you don't have a website or online booking yet.

Many fitness businesses nearby are getting more inquiries through:
• A simple professional website
• WhatsApp booking for trial sessions
• Google visibility improvements

I help gyms set this up. Would you be open to a free 10-min audit?

I also put together a quick preview of what your gym could look like online — happy to share if you're interested.

— Nitin
```

### Instagram DM (shorter)

```
Hi! Love what Bull's Legacy is doing in Dehradun. Quick question — are you looking to add online booking or a website? I help local gyms with exactly that. Happy to share ideas if useful 🙌
— Nitin
```

### Email

```
Subject: Quick idea for Bull's Legacy Gym's online presence

Hi Bull's Legacy Team,

I noticed your gym has a strong local presence in Dehradun but currently doesn't have a website or online booking system.

Many fitness businesses are seeing increased inquiries through simple WhatsApp booking and Google visibility improvements.

I can help set up:
• Professional Website
• WhatsApp Booking
• Google Business Optimization

Would you be interested in a free audit?

Regards,
Nitin
```

### Phone script (bullet points)

- Intro: who you are, 10 seconds
- Observed gap: no website / no online booking
- Offer: free audit, no obligation
- Ask: good time for 10-min call?

## Human Approval

After generating drafts, **always** present:

```
─── DRAFT READY ───
Channel: WhatsApp
To: +91xxxxxxxxxx

[message body]

Approve to save draft?
Reply: approve / reject / edit: <your changes>
```

**V1:** Saving approved draft to `~/.hermes/leads/drafts/` as JSON. Sending is manual or V2.

## Output Format

```json
{
  "business": "Bull's Legacy Gym",
  "channel": "whatsapp",
  "recipient": "+919876543210",
  "subject": null,
  "body": "...",
  "sender": "Nitin",
  "status": "pending_approval",
  "personalization_used": [
    "No website",
    "No online booking",
    "Strong local presence"
  ],
  "services_offered": ["Website", "WhatsApp Booking", "Google Business Optimization"]
}
```

See [sample-output.json](sample-output.json).

## Verification Rules

- [ ] References business name
- [ ] Uses at least one specific issue from lead data
- [ ] Channel matches `recommended_channel` from contact-finder
- [ ] Ends with approval prompt — not sent
- [ ] No false or unverifiable claims

## V2 (not in scope)

Auto-send via email API, WhatsApp Business API, LinkedIn automation.
