#!/usr/bin/env python3
"""Build a lead demo site from lead-research.json + category HTML template.

Usage:
  python3 build_demo.py <slug>
  python3 build_demo.py om-sports-and-fitness-center
  python3 build_demo.py --research ~/.hermes/leads/research/foo.json

Resolves slug from research meta.slug. Writes:
  ~/.hermes/leads/demos/{slug}/index.html
  ~/.hermes/leads/demos/{slug}/meta.json
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
RESEARCH_DIR = HERMES_HOME / "leads" / "research"
DEMOS_DIR = HERMES_HOME / "leads" / "demos"

GYM_CATEGORIES = {
    "gym", "fitness", "gymnasium", "crossfit", "health club", "sports & fitness center",
    "sports and fitness center", "fitness center",
}
SALON_CATEGORIES = {
    "beauty salon", "salon", "spa", "unisex salon", "hair salon", "beauty",
}

GYM_IMAGES = [
    "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=1200&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=800&q=80&auto=format&fit=crop",
]
SALON_IMAGES = [
    "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?w=1200&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1633681926022-84c23e8cb04d?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?w=600&q=80&auto=format&fit=crop",
]
HERO_GYM = "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1920&q=80&auto=format&fit=crop"
HERO_SALON = "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=900&q=80&auto=format&fit=crop"


def e(text: str | None) -> str:
    return html.escape(text or "", quote=True)


def phone_digits(phone: str | None) -> str:
    if not phone:
        return ""
    return re.sub(r"\D", "", phone)


def phone_display(phone: str | None) -> str:
    d = phone_digits(phone)
    if len(d) == 12 and d.startswith("91"):
        d = d[2:]
    if len(d) == 10:
        return f"+91 {d[:5]} {d[5:]}"
    return phone or ""


def resolve_research_path(arg: str) -> Path:
    p = Path(arg).expanduser()
    if p.is_file():
        return p
    slug = arg.strip().lower().replace("_", "-")
    exact = RESEARCH_DIR / f"{slug}.json"
    if exact.is_file():
        return exact
    matches = sorted(RESEARCH_DIR.glob(f"{slug}*.json"))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Ambiguous slug '{slug}'. Matches:", file=sys.stderr)
        for m in matches:
            print(f"  {m.name}", file=sys.stderr)
        sys.exit(1)
    print(f"No research file for '{slug}' in {RESEARCH_DIR}", file=sys.stderr)
    sys.exit(1)


def load_research(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def pick_template_name(category: str) -> str:
    cat = (category or "").strip().lower()
    if cat in SALON_CATEGORIES or "salon" in cat or "spa" in cat:
        return "salon-modern"
    if cat in GYM_CATEGORIES or "gym" in cat or "fitness" in cat or "sport" in cat:
        return "gym-modern"
    raise SystemExit(f"No HTML template for category '{category}'. Add template or use gym/salon.")


def section_by_id(data: dict, sid: str) -> dict | None:
    for sec in data.get("content_for_ui", {}).get("sections", []):
        if sec.get("id") == sid:
            return sec
    return None


def services_list(data: dict) -> list[str]:
    ui = data.get("content_for_ui", {})
    sec = section_by_id(data, "services")
    if sec and sec.get("items"):
        return [str(x) for x in sec["items"]]
    svcs = data.get("offerings", {}).get("services") or []
    return [str(s) for s in svcs] if svcs else ["Training", "Fitness", "Classes"]


def hero_lines(headline: str) -> tuple[str, str]:
    if ":" in headline:
        a, b = headline.split(":", 1)
        return a.strip(), b.strip()
    words = headline.split()
    if len(words) <= 4:
        return headline, ""
    return " ".join(words[:4]), " ".join(words[4:])


def hero_h1_gym(headline: str) -> str:
    line1, line2 = hero_lines(headline)

    def line_html(text: str) -> str:
        if not text:
            return ""
        words = "".join(
            f'<span class="word">{e(w)}</span> ' for w in text.split()
        )
        return f'<span class="line">{words.strip()}</span>'

    parts = [line_html(line1)]
    if line2:
        parts.append(f'<span class="line"><span class="word">{e(line2)}</span></span>')
    return "\n        ".join(p for p in parts if p)


def marquee_html(items: list[str], repeat: int = 2) -> str:
    out: list[str] = []
    for _ in range(repeat):
        for item in items:
            out.append(f"<span>{e(item)} <em>·</em></span>")
    return "\n      ".join(out)


def gym_bento_html(services: list[str]) -> str:
    while len(services) < 4:
        services.append(services[-1] if services else "Training")
    services = services[:4]
    descs = [
        "Our flagship program — built for results at every level.",
        "Structured training with expert guidance.",
        "Build endurance and energy with dedicated zones.",
        "Personalized coaching tailored to your goals.",
    ]
    cards = []
    featured = (
        f'<article class="card featured reveal">\n'
        f'          <img src="{GYM_IMAGES[0]}" alt="{e(services[0])}" loading="lazy">\n'
        f'          <div class="card-body"><h3>{e(services[0])}</h3><p>{e(descs[0])}</p></div>\n'
        f"        </article>"
    )
    cards.append(featured)
    for i, svc in enumerate(services[1:4], start=1):
        cards.append(
            f'<article class="card reveal">\n'
            f'          <img src="{GYM_IMAGES[i]}" alt="{e(svc)}" loading="lazy">\n'
            f'          <div class="card-body"><h3>{e(svc)}</h3><p>{e(descs[i])}</p></div>\n'
            f"        </article>"
        )
    return "\n        ".join(cards)


def gym_why_html(data: dict) -> str:
    vibes = data.get("brand_signals", {}).get("tone_words") or []
    gaps = data.get("gaps", {}).get("demo_should_highlight") or []
    reviews = data.get("reviews", {}).get("google_count")
    items = [
        ("💪", "Expert Coaching", vibes[0] if vibes else "Proficient coaches dedicated to your progress."),
        ("🤝", "Community", f"{reviews}+ reviews" if reviews else "A friendly, welcoming training environment."),
        ("📱", "Easy Booking", gaps[0] if gaps else "Book via phone or WhatsApp in seconds."),
    ]
    blocks = []
    for icon, title, body in items:
        blocks.append(
            f'<div class="why-item reveal">\n'
            f'          <div class="icon">{icon}</div>\n'
            f"          <h3>{e(title)}</h3>\n"
            f"          <p>{e(body)}</p>\n"
            f"        </div>"
        )
    return "\n        ".join(blocks)


def salon_services_html(services: list[str]) -> str:
    icons = ["✂️", "🎨", "✨", "💍", "💅", "🧴"]
    defaults = [
        ("Haircut & Styling", "Precision cuts for men and women.", "From ₹299 · Book for pricing"),
        ("Hair Color & Treatment", "Color, highlights, and nourishing treatments.", "From ₹999"),
        ("Facials & Skin Care", "Treatments tailored to your skin type.", "From ₹699"),
        ("Bridal & Makeup", "Packages for weddings and celebrations.", "Packages available"),
        ("Nails & Manicure", "Manicure, pedicure, and nail art.", "From ₹399"),
        ("Beauty Services", "Waxing, threading, and grooming.", "View menu when booking"),
    ]
    cards = []
    for i in range(6):
        if i < len(services):
            title = services[i]
            body = f"Professional {title.lower()} with quality products."
            price = "Book for pricing"
        else:
            title, body, price = defaults[i]
        cards.append(
            f'<article class="service-card reveal">\n'
            f'          <div class="icon">{icons[i]}</div>\n'
            f"          <h3>{e(title)}</h3>\n"
            f"          <p>{e(body)}</p>\n"
            f'          <span class="price-tag">{e(price)}</span>\n'
            f"        </article>"
        )
    return "\n        ".join(cards)


def salon_gallery_html() -> str:
    alts = ["Hair styling", "Beauty treatment", "Salon ambiance", "Hair color", "Spa care"]
    parts = [
        f'<div class="g-item wide"><img src="{SALON_IMAGES[0]}" alt="{e(alts[0])}" loading="lazy"></div>'
    ]
    for i in range(1, 5):
        parts.append(
            f'<div class="g-item"><img src="{SALON_IMAGES[i]}" alt="{e(alts[i])}" loading="lazy"></div>'
        )
    return "\n        ".join(parts)


def address_html(data: dict) -> str:
    loc = data.get("location", {})
    lines = [
        loc.get("address"),
        loc.get("landmark"),
        f"{loc.get('city', '')}, {loc.get('state', '')} {loc.get('pin', '')}".strip(),
    ]
    return "<br>\n            ".join(e(x) for x in lines if x)


def primary_contact(data: dict) -> tuple[str, str, str]:
    """Returns (href, label, channel) for primary CTA."""
    c = data.get("contact", {})
    ui = data.get("content_for_ui", {})
    cta = ui.get("cta_primary") or "Book Now"
    ch = c.get("recommended_channel") or ""
    phone = phone_digits(c.get("phone") or c.get("whatsapp"))
    wa = phone_digits(c.get("whatsapp") or c.get("phone"))
    email = c.get("email")

    if ch == "whatsapp" and wa:
        return f"https://wa.me/{wa}", cta, "wa"
    if ch == "email" and email:
        subj = "Appointment%20Request"
        return f"mailto:{email}?subject={subj}", cta, "email"
    if phone:
        return f"tel:+{phone if phone.startswith('91') else '91' + phone}", cta, "phone"
    if wa:
        return f"https://wa.me/{wa}", cta, "wa"
    if email:
        return f"mailto:{email}", cta, "email"
    return "#", cta, "none"


def secondary_contact(data: dict) -> tuple[str, str]:
    c = data.get("contact", {})
    ui = data.get("content_for_ui", {})
    label = ui.get("cta_secondary") or "Contact Us"
    wa = phone_digits(c.get("whatsapp") or c.get("phone"))
    email = c.get("email")
    if wa:
        return f"https://wa.me/{wa}", "WhatsApp Now"
    if email:
        return f"mailto:{email}", label if "email" in label.lower() else "Email Us"
    return "#", label


def short_name(display_name: str) -> str:
    name = display_name.split("|")[0].strip()
    words = name.split()
    return " ".join(words[:2]) if len(words) > 2 else name


def salon_logo_html(display_name: str) -> str:
    parts = display_name.replace("|", " ").split()
    if len(parts) >= 2:
        return f"{e(parts[0])} <em>{e(' '.join(parts[1:3]))}</em>"
    return e(display_name)


def open_time_label(hours: str | None) -> str:
    if not hours:
        return "Open"
    m = re.search(r"(\d{1,2})\s*(?:am|AM)", hours)
    return f"{m.group(1)}am" if m else "Open"


def sticky_short(cta: str) -> str:
    if len(cta) <= 14:
        return cta
    if cta.lower().startswith("book"):
        return "Book Now"
    return cta.split()[0]


def fill_template(template: str, mapping: dict[str, str]) -> str:
    out = template
    for key, val in mapping.items():
        out = out.replace(f"{{{{{key}}}}}", val)
    missing = re.findall(r"\{\{([A-Z0-9_]+)\}\}", out)
    if missing:
        print(f"Warning: unfilled placeholders: {', '.join(sorted(set(missing)))}", file=sys.stderr)
    return out


def build_gym(data: dict) -> str:
    template = (TEMPLATES_DIR / "gym-modern.html").read_text(encoding="utf-8")
    meta = data["meta"]
    ui = data["content_for_ui"]
    loc = data["location"]
    reviews = data.get("reviews", {})
    services = services_list(data)
    about = section_by_id(data, "about")
    phone = phone_digits(data.get("contact", {}).get("phone"))
    wa = phone_digits(data.get("contact", {}).get("whatsapp") or data.get("contact", {}).get("phone"))
    pri_href, pri_text, pri_ch = primary_contact(data)
    sec_href, sec_text = secondary_contact(data)
    display = data.get("identity", {}).get("display_name") or meta["business"]
    rating = reviews.get("rating") or 0
    count = reviews.get("google_count") or 0

    mapping = {
        "PAGE_TITLE": e(f"{meta['business']} — {meta['city']}"),
        "LOGO_EMOJI": "🏋️",
        "LOGO_NAME": e(short_name(display)),
        "NAV_CTA_HREF": pri_href,
        "NAV_CTA_TEXT": e(pri_text),
        "HERO_IMG": HERO_GYM,
        "HERO_ALT": e(services[0] if services else "Fitness"),
        "EYEBROW": (
            f"<span>★ {rating}</span> · {count} Google reviews · "
            f"{e(loc.get('area') or loc.get('city'))}, {e(meta['city'])}"
            if count else
            f"{e(loc.get('area') or loc.get('city'))}, {e(meta['city'])}"
        ),
        "HERO_H1_HTML": hero_h1_gym(ui.get("hero_headline") or meta["business"]),
        "HERO_SUB": e(ui.get("hero_subhead") or ""),
        "PRIMARY_CTA_HREF": pri_href,
        "PRIMARY_CTA_TEXT": e(pri_text),
        "SECONDARY_CTA_HREF": sec_href,
        "SECONDARY_CTA_TEXT": e(sec_text),
        "STAT_REVIEWS": str(count) if count else "—",
        "STAT_RATING": str(rating) if rating else "—",
        "STAT_RATING_DECIMAL": "1" if rating else "0",
        "STAT_OPEN": e(open_time_label(data.get("offerings", {}).get("hours"))),
        "MARQUEE_HTML": marquee_html(services + [meta["city"]]),
        "PROGRAMS_BLURB": e(
            (about or {}).get("body")
            or f"Train your way at {loc.get('area') or meta['city']}'s neighborhood fitness center."
        ),
        "BENTO_HTML": gym_bento_html(list(services)),
        "WHY_TITLE": e(f"Why {short_name(display)}"),
        "WHY_BLURB": e(
            data.get("identity", {}).get("tagline")
            or "Strong community. Expert coaching. Results that last."
        ),
        "WHY_ITEMS_HTML": gym_why_html(data),
        "VISIT_IMG": "https://images.unsplash.com/photo-1540497077202-7bf8a69ad5fd?w=1200&q=80&auto=format&fit=crop",
        "ADDRESS_HTML": address_html(data),
        "HOURS": e(data.get("offerings", {}).get("hours") or ""),
        "CALL_HREF": f"tel:+{phone}" if phone else pri_href,
        "CALL_LABEL": e(f"Call {phone_display(data.get('contact', {}).get('phone'))}" if phone else pri_text),
        "WA_HREF": f"https://wa.me/{wa}" if wa else sec_href,
        "FOOTER_1": e(ui.get("footer_tagline") or f"{meta['business']} — {meta['city']}"),
        "FOOTER_2": e(f"{short_name(display)} · {loc.get('area') or meta['city']}"),
        "STICKY_PRIMARY_HREF": pri_href,
        "STICKY_PRIMARY_TEXT": e(sticky_short(pri_text)),
        "STICKY_SECONDARY_HREF": f"https://wa.me/{wa}" if wa else sec_href,
        "STICKY_SECONDARY_TEXT": "WhatsApp",
    }
    return fill_template(template, mapping)


def build_salon(data: dict) -> str:
    template = (TEMPLATES_DIR / "salon-modern.html").read_text(encoding="utf-8")
    meta = data["meta"]
    ui = data["content_for_ui"]
    loc = data["location"]
    c = data.get("contact", {})
    services = services_list(data)
    pri_href, pri_text, _ = primary_contact(data)
    sec_href, sec_text = secondary_contact(data)
    display = data.get("identity", {}).get("display_name") or meta["business"]
    tagline = data.get("identity", {}).get("tagline") or ""
    vibes = data.get("brand_signals", {}).get("vibe") or []
    gaps = data.get("gaps", {}).get("demo_should_highlight") or []
    fb = c.get("facebook")

    pills = (vibes[:2] + gaps[:2]) or ["Professional stylists", "Quality products", "Online booking ready"]
    pills_html = "\n          ".join(f"<span>{e(p)}</span>" for p in pills[:4])

    sec_href_btn = fb if fb else sec_href
    sec_label = "Facebook" if fb else sec_text

    mapping = {
        "PAGE_TITLE": e(f"{meta['business']} — {meta['city']}"),
        "LOGO_HTML": salon_logo_html(display),
        "NAV_CTA_HREF": "#book",
        "NAV_CTA_TEXT": "Book Now",
        "HERO_BADGE": e(f"Unisex Salon · {loc.get('area') or loc.get('city')}, {meta['city']}"),
        "HERO_H1": e(ui.get("hero_headline") or meta["business"]),
        "HERO_SUB": e(ui.get("hero_subhead") or ""),
        "PRIMARY_CTA_HREF": pri_href,
        "PRIMARY_CTA_TEXT": e(pri_text),
        "SECONDARY_CTA_HREF": sec_href,
        "SECONDARY_CTA_TEXT": e(sec_text),
        "HERO_IMG": HERO_SALON,
        "FLOAT_HOURS": e(data.get("offerings", {}).get("hours") or "Mon–Sat 9am–9pm"),
        "FLOAT_LOCATION": e(f"{loc.get('area') or loc.get('city')} · {meta['city']}"),
        "MARQUEE_HTML": marquee_html(services[:6] + ["Unisex Salon"]),
        "SERVICES_BLURB": e(tagline[:120] if tagline else "Full-service hair & beauty you'll love."),
        "SERVICES_HTML": salon_services_html(services),
        "GALLERY_TITLE": e(f"Inside {short_name(display)}"),
        "GALLERY_HTML": salon_gallery_html(),
        "QUOTE": e(tagline or "Dedicated to excellent service, quality products, and an enjoyable atmosphere."),
        "PILLS_HTML": pills_html,
        "ADDRESS_HTML": address_html(data),
        "HOURS": e(data.get("offerings", {}).get("hours") or ""),
        "VISIT_PRIMARY_HREF": pri_href,
        "VISIT_PRIMARY_TEXT": e(pri_text),
        "VISIT_SECONDARY_HREF": sec_href_btn,
        "VISIT_SECONDARY_TEXT": e(sec_label),
        "VISIT_IMG": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=800&q=80&auto=format&fit=crop",
        "FOOTER_TEXT": e(ui.get("footer_tagline") or f"{meta['business']} — {meta['city']}"),
        "STICKY_PRIMARY_HREF": pri_href,
        "STICKY_PRIMARY_TEXT": "Book Now",
        "STICKY_SECONDARY_HREF": sec_href,
        "STICKY_SECONDARY_TEXT": "Email" if c.get("email") else "Contact",
    }
    return fill_template(template, mapping)


def write_outputs(data: dict, html: str, template_name: str) -> Path:
    slug = data["meta"]["slug"]
    out_dir = DEMOS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "index.html"
    html_path.write_text(html, encoding="utf-8")
    meta = {
        "business": data["meta"]["business"],
        "city": data["meta"]["city"],
        "category": data["meta"]["category"],
        "template_used": template_name,
        "research_path": str(RESEARCH_DIR / f"{slug}.json"),
        "demo_path": str(html_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lead_source": "lead-research",
        "preview_command": f"open {html_path}",
        "built_by": "build_demo.py",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return html_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build lead demo site from research JSON")
    parser.add_argument("slug", nargs="?", help="Lead slug or partial slug")
    parser.add_argument("--research", help="Path to research JSON (overrides slug lookup)")
    args = parser.parse_args()

    if not args.slug and not args.research:
        parser.error("Provide slug or --research path")

    research_path = Path(args.research).expanduser() if args.research else resolve_research_path(args.slug)
    data = load_research(research_path)
    template_name = pick_template_name(data["meta"].get("category", ""))

    if template_name == "gym-modern":
        html = build_gym(data)
    else:
        html = build_salon(data)

    out = write_outputs(data, html, template_name)
    print(json.dumps({"ok": True, "slug": data["meta"]["slug"], "template": template_name, "demo_path": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
