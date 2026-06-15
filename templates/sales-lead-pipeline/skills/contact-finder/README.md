# contact-finder

Enriches leads from `local-lead-finder` with contact channels (email, phone, WhatsApp, social).

## Pipeline position

```
local-lead-finder → contact-finder → pitch-generator → [human approval] → send
```

## Quick start

```
/contact-finder Bull's Legacy Gym, Dehradun
```

Or with lead JSON from lead-finder:

```
/contact-finder
Business: Bull's Legacy Gym
City: Dehradun
Issues: No website, No online booking
```

## Output

See [sample-output.json](sample-output.json)

## V1 limits

- Public web sources only
- No message sending
- No bulk automation

## Location

`~/.hermes/skills/contact-finder/`
