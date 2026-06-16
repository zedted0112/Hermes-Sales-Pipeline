# lead-demo-site

Business-specific UI-only demo websites for sales leads. **Not generic templates.**

## Pipeline

```
local-lead-finder → contact-finder → lead-research → lead-demo-site → pitch-generator
```

`lead-research` is **required** — demo reads `~/.hermes/leads/research/{slug}.json`.

**Build:** Hermes runs `bash scripts/build.sh {slug}` — do not hand-write HTML or Python in chat.

**Category templates (v1.2):**
- Gym → `templates/gym-modern.html` (Bull's Legacy)
- Salon → `templates/salon-modern.html` (Shear Genius)

## Quick start

```
/lead-research Om Sports Gym, Dehradun
/lead-demo-site om-sports-and-fitness-center
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
├── scripts/build_demo.py   # ← Hermes runs this
├── templates/
│   ├── gym-modern.html
│   └── salon-modern.html
```

## Output location

`~/.hermes/leads/demos/{business-slug}/`
