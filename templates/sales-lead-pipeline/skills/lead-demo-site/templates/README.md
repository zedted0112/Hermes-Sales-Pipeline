# Category HTML templates — modern demos

Hermes **must** start from these files. Do not design gym/salon layouts from scratch.

| Category keywords | Template file | Reference lead |
|-------------------|---------------|----------------|
| `gym`, `fitness`, `gymnasium`, `crossfit`, `health club` | `templates/gym-modern.html` | Bull's Legacy Gym |
| `beauty salon`, `salon`, `spa`, `unisex salon`, `hair salon`, `beauty` | `templates/salon-modern.html` | Shear Genius Unisex Salon |

## How to load

```
skill_view(name="lead-demo-site", file_path="templates/gym-modern.html")
skill_view(name="lead-demo-site", file_path="templates/salon-modern.html")
skill_view(name="lead-demo-site", file_path="templates/gym-modern-dark.html")
skill_view(name="lead-demo-site", file_path="templates/retail-modern.html")
skill_view(name="lead-demo-site", file_path="templates/salon-chocolate.html")
```

## Build procedure

1. Read `lead-research.json` for the new lead
2. Load the **category template** (match `meta.category` — see table above)
3. **Copy the full HTML** — keep all `<style>`, `<script>`, class names, motion, grid structure **unchanged**
4. **Replace content only** — see [SUBSTITUTION.md](SUBSTITUTION.md)
5. Swap Unsplash image URLs using `media.image_keywords` (keep same layout slots)
6. Save to `~/.hermes/leads/demos/{slug}/index.html`

## What you MUST NOT change

- CSS variables, animations, keyframes, Intersection Observer logic
- Section order and component types (bento, marquee, sticky CTA, etc.)
- Font families (gym: Syne + DM Sans · salon: Cormorant Garamond + Outfit)
- Overall color system per category (gym = dark + orange · salon = cream + sage)

## What you MUST change

- Every instance of the reference business name → new lead name
- City, address, hours, phone, WhatsApp, email, Facebook
- Hero headline/subhead from `content_for_ui`
- Service/program cards from `offerings.services` (expand to 4–6 items if needed)
- Stats strip (reviews/rating/hours) from `reviews` + `offerings.hours`
- `meta.json` `template_used` field

## Other categories

Restaurant, clinic, coaching — no locked template yet. Use `claude-design` + `category-briefs.md` until templates are added.
