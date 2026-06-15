# Template substitution map

When adapting `gym-modern.html` or `salon-modern.html` for a new lead, replace these slots from `lead-research.json`.

## Universal fields

| Template slot | JSON path | Notes |
|---------------|-----------|-------|
| `<title>` | `meta.business` + `meta.city` | |
| Logo / nav name | `identity.display_name` or short name | Keep styling, shorten if long |
| Hero H1 | `content_for_ui.hero_headline` | Verbatim preferred |
| Hero subtext | `content_for_ui.hero_subhead` | |
| Primary CTA label | `content_for_ui.cta_primary` | gym: often "Book Free Trial" · salon: "Book an Appointment" |
| Secondary CTA | `content_for_ui.cta_secondary` | Link: phone, WhatsApp, or email |
| Marquee items | `offerings.services` | Repeat for infinite scroll |
| Service/program cards | `offerings.services` | Expand with category-typical items if list is short |
| Address block | `location.address`, `location.city`, `location.pin` | |
| Hours | `offerings.hours` | |
| Footer tagline | `content_for_ui.footer_tagline` | |
| About/quote block | `identity.tagline` or `content_for_ui.sections` where `id=about` | salon template |

## Contact links

| Channel | HTML |
|---------|------|
| Phone | `href="tel:+91XXXXXXXXXX"` (strip spaces) |
| WhatsApp | `href="https://wa.me/91XXXXXXXXXX"` (no +) |
| Email | `href="mailto:email@domain.com?subject=Appointment%20Request"` |
| Facebook | `contact.facebook` if present |

Use `contact.recommended_channel` to decide sticky mobile CTA priority.

## Gym template only (`gym-modern.html`)

| Slot | JSON path |
|------|-----------|
| Stats: review count | `reviews.google_count` — hide stat if null |
| Stats: rating | `reviews.rating` — use `data-count` + `data-decimal="1"` |
| Stats: open time | parse from `offerings.hours` or use "6am" |
| Bento program cards (4) | `offerings.services` + category extras (Cardio, PT, etc.) |
| Why-us bullets | `brand_signals.tone_words` or `gaps.demo_should_highlight` |
| Eyebrow line | rating + reviews + area from `location.area` |

## Salon template only (`salon-modern.html`)

| Slot | JSON path |
|------|-----------|
| Hero badge | `location.area` + `meta.city` |
| Service cards (6) | Expand `offerings.services` → Haircut, Color, Facial, Bridal, Nails, Beauty |
| Price tags | `offerings.price_hints` or "From ₹… · Book for pricing" if gaps include no price list |
| Gallery alt text | `media.image_keywords` |
| Blockquote | `identity.tagline` or about section body |
| Why pills | `brand_signals.vibe` + `gaps.demo_should_highlight` |

## Images

Replace Unsplash URLs only — keep same number and layout positions:

- Hero background/hero visual
- Bento/card images (gym: 4 · salon: gallery 5 + visit)
- Use `media.image_keywords` in search: `images.unsplash.com/photo-...?w=1200&q=80&auto=format&fit=crop`

## meta.json (always write)

```json
{
  "business": "{meta.business}",
  "city": "{meta.city}",
  "category": "{meta.category}",
  "template_used": "gym-modern",
  "research_path": "~/.hermes/leads/research/{slug}.json",
  "demo_path": "~/.hermes/leads/demos/{slug}/index.html",
  "generated_at": "ISO-8601",
  "lead_source": "lead-research",
  "preview_command": "open ~/.hermes/leads/demos/{slug}/index.html"
}
```

`template_used`: `gym-modern` | `salon-modern`
