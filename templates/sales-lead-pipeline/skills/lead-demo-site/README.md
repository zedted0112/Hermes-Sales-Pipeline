# lead-demo-site

Business-specific UI-only demo websites for sales leads. **Not generic templates.**

## Pipeline

```
local-lead-finder → contact-finder → lead-research → lead-demo-site → pitch-generator
```

`lead-research` is **required** — demo reads `~/.hermes/leads/research/{slug}.json`.

## Quick start

```
/lead-research Bull's Legacy Gym, Dehradun
/lead-demo-site bulls-legacy-gym
```

## Preview

```bash
open ~/.hermes/leads/demos/bulls-legacy-gym/index.html
```

## Composed Hermes skills

- `lead-research` — fact sheet + UI copy (input)
- `claude-design` — design quality
- `popular-web-designs` — craft reference (category-adapted)
- `sketch` — optional 2 variants

## Files

```
lead-demo-site/
├── SKILL.md
├── README.md
├── category-briefs.md
└── sample-meta.json
```

## Output location

`~/.hermes/leads/demos/{business-slug}/`
