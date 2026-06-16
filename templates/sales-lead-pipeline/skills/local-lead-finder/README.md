# local-lead-finder

Hermes skill (V1) for discovering local businesses with weak online presence and scoring them as digital-services sales opportunities.

## Quick start

**Telegram or CLI** — send:

```
City: Dehradun
Category: Gym
```

Or:

```
Find gym leads in Dehradun using local-lead-finder
```

If you invoke `/local-lead-finder` with no city/category, Hermes will ask once:

```
Which city and what business category should I find leads for?
Reply like: City: Dehradun, Category: Gym
```

**CLI with skill preloaded:**

```bash
hermes chat -s local-lead-finder
```

Then: `City: Dehradun, Category: Gym`

## Example output

See [sample-output.json](sample-output.json)

## Scoring (max 10)

| Issue | Points |
|-------|--------|
| No website | +5 |
| Website outdated | +3 |
| No online booking | +2 |
| No WhatsApp contact | +2 |
| Inactive social media | +2 |
| Low Google review count | +1 |

## V1 scope

- Lead discovery via web search
- Signal analysis from public info
- Opportunity scoring
- Markdown + JSON report

## Not in V1

- CRM integrations
- Databases / lead storage
- Email or WhatsApp sending
- Maps / Apify APIs
- Outreach automation

## Files

```
~/.hermes/skills/local-lead-finder/
├── SKILL.md              # Agent workflow and rules
├── README.md             # This file
└── sample-output.json    # Example report output
```

## Reload after install

In an active Hermes session: `/reload-skills`

Or start a new chat / restart gateway.
