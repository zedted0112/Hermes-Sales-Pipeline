#!/usr/bin/env python3
"""Build a lead demo site from lead-research.json + category HTML template.

Usage:
  python3 build_demo.py <slug>
  python3 build_demo.py om-sports-and-fitness-center
  python3 build_demo.py --research ~/.hermes/leads/research/foo.json

Resolves slug from research meta.slug. Writes:
  ~/.hermes/leads/demos/{slug}/index.html
  ~/.hermes/leads/demos/{slug}/meta.json

Optional:
  --output-dir <path> writes the same structure under <path>/{slug}/
  --base-url <url> adds meta.demo_url to meta.json
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

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
RETAIL_CATEGORIES = {
    "clothing store", "clothing", "boutique", "apparel", "fashion", "retail",
    "designer boutique", "garment",
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
    "https://images.unsplash.com/photo-1562322140-8baeececf3df?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?w=600&q=80&auto=format&fit=crop",
]
HERO_GYM = "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1920&q=80&auto=format&fit=crop"
VISIT_GYM = "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1200&q=80&auto=format&fit=crop"
HERO_SALON = "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=900&q=80&auto=format&fit=crop"
HERO_RETAIL = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1920&q=80&auto=format&fit=crop"
RETAIL_IMAGES = [
    "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1200&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600&q=80&auto=format&fit=crop",
]


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
    if cat in RETAIL_CATEGORIES or "cloth" in cat or "boutique" in cat or "fashion" in cat or "apparel" in cat:
        return "retail-modern"
    if cat in SALON_CATEGORIES or "salon" in cat or "spa" in cat:
        return "salon-modern"
    if cat in GYM_CATEGORIES or "gym" in cat or "fitness" in cat or "sport" in cat:
        return "gym-modern"
    raise SystemExit(f"No HTML template for category '{category}'. Supported: gym, salon, retail/clothing.")


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
        ("💪", "Expert Coaching", vibes[0].capitalize() if vibes else "Proficient coaches dedicated to your progress."),
        ("🤝", "Community", f"{reviews}+ happy members" if reviews else "A friendly, welcoming training environment."),
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


def parse_rating(val) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    m = re.search(r"(\d+\.?\d*)", str(val))
    return float(m.group(1)) if m else None


def gym_service_chips_html(services: list[str]) -> str:
    return "\n      ".join(f'<span class="chip">{e(s)}</span>' for s in services[:12])


GYM_TRAINER_IMAGES = [
    "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=400&q=80&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80&auto=format&fit=crop",
]
GYM_TRAINER_ROLES = [
    ("Head Coach", "Strength & conditioning specialist"),
    ("Group Fitness", "Zumba, aerobics & dance fitness"),
    ("Yoga & Wellness", "Flexibility, core & recovery"),
]


def gym_schedule_html(services: list[str]) -> str:
    days = [
        ("mon", "Mon", "Today"),
        ("tue", "Tue", ""),
        ("wed", "Wed", ""),
        ("thu", "Thu", ""),
        ("fri", "Fri", ""),
        ("sat", "Sat", "Weekend"),
    ]
    times = ["6:00 AM", "7:30 AM", "5:30 PM", "7:00 PM"]
    coaches = ["Coach Raj", "Coach Priya", "Coach Amit", "Coach Team"]
    svcs = services or ["Strength Training", "Cardio", "Yoga", "HIIT"]
    while len(svcs) < 4:
        svcs.append(svcs[-1])

    tabs = []
    for i, (did, label, sub) in enumerate(days):
        active = " active" if i == 0 else ""
        sub_html = f"<span>{e(sub)}</span>" if sub else ""
        tabs.append(f'<button type="button" class="schedule-tab{active}" data-day="{did}">{e(label)}{sub_html}</button>')

    bodies = []
    for i, (did, _, _) in enumerate(days):
        active = " active" if i == 0 else ""
        rows = []
        for j, t in enumerate(times):
            svc = svcs[(i + j) % len(svcs)]
            rows.append(
                f'<div class="class-row">\n'
                f'            <div class="class-time">{e(t)}</div>\n'
                f'            <div class="class-info"><strong>{e(svc)}</strong><span>{e(coaches[j % len(coaches)])} · 45 min</span></div>\n'
                f'            <button type="button" class="class-book" data-class="{e(svc)}">Book</button>\n'
                f"          </div>"
            )
        bodies.append(f'<div class="schedule-day{active}" id="day-{did}">\n          ' + "\n          ".join(rows) + "\n        </div>")

    return (
        f'<div class="schedule-tabs">\n        {"\n        ".join(tabs)}\n      </div>\n'
        f'      <div class="schedule-body">\n        {"\n        ".join(bodies)}\n      </div>'
    )


def gym_plans_html(services: list[str], business: str) -> str:
    featured = services[0] if services else "Gym access"
    mid = services[1] if len(services) > 1 else "Group classes"
    premium = services[2] if len(services) > 2 else "Personal training"
    plans = [
        ("Starter", "999", "/month", False, [
            "Gym floor access",
            f"{featured} sessions",
            "Locker & shower",
            "Weekday hours",
        ]),
        ("Pro", "1,499", "/month", True, [
            "Everything in Starter",
            f"Unlimited {mid}",
            "Weekend access",
            "1 free PT session / month",
        ]),
        ("Elite", "2,499", "/month", False, [
            "Everything in Pro",
            f"Weekly {premium}",
            "Nutrition check-in",
            "Priority class booking",
        ]),
    ]
    cards = []
    for name, price, period, popular, feats in plans:
        badge = '<span class="plan-badge">Most popular</span>\n      ' if popular else ""
        pop_cls = " popular" if popular else ""
        feat_html = "\n          ".join(f"<li>{e(f)}</li>" for f in feats)
        cards.append(
            f'<article class="plan-card{pop_cls} reveal">\n'
            f"      {badge}"
            f"      <h3>{e(name)}</h3>\n"
            f'      <div class="plan-price">₹{price}<small>{e(period)}</small></div>\n'
            f"      <ul class=\"plan-features\">\n          {feat_html}\n"
            f"      </ul>\n"
            f'      <button type="button" class="btn btn-primary" style="width:100%" data-open-modal>Join {e(name)}</button>\n'
            f"    </article>"
        )
    return "\n      ".join(cards)


def gym_phone_classes_html(services: list[str]) -> str:
    times = ["6:00 AM", "5:30 PM", "7:00 PM"]
    svcs = (services or ["Cardio", "Strength", "Yoga"])[:3]
    rows = []
    for t, svc in zip(times, svcs):
        rows.append(
            f'<div class="phone-class"><span class="dot"></span><div><strong>{e(svc)}</strong><br>{e(t)}</div></div>'
        )
    return "\n              ".join(rows)


def gym_trainers_html() -> str:
    cards = []
    for i, (role, bio) in enumerate(GYM_TRAINER_ROLES):
        cards.append(
            f'<article class="trainer-card reveal">\n'
            f'          <div class="trainer-img"><img src="{GYM_TRAINER_IMAGES[i]}" alt="{e(role)}" loading="lazy"></div>\n'
            f'          <div class="trainer-info">\n'
            f'            <div class="role">{e(role)}</div>\n'
            f"            <h3>Coach {e(['Raj', 'Priya', 'Amit'][i])}</h3>\n"
            f"            <p>{e(bio)}</p>\n"
            f"          </div>\n"
            f"        </article>"
        )
    return "\n        ".join(cards)


def gym_testimonials_html(data: dict) -> str:
    quotes = data.get("reviews", {}).get("sample_quotes") or []
    city = data.get("meta", {}).get("city") or "town"
    if not quotes:
        quotes = [
            f"Best gym in {city} — great trainers and a motivating vibe every morning.",
            "Love the group classes. Zumba and yoga are my weekly highlight!",
            "Clean facility, friendly staff. Worth every rupee — highly recommend.",
        ]
    names = ["Member", "Priya S.", "Rahul K.", "Ananya M."]
    cards = []
    for i, q in enumerate(quotes[:4]):
        text = q if isinstance(q, str) else q.get("text", "")
        author = q.get("author", names[i % len(names)]) if isinstance(q, dict) else names[i % len(names)]
        initial = author[0].upper() if author else "M"
        cards.append(
            f'<article class="testimonial">\n'
            f'          <div class="stars">★★★★★</div>\n'
            f"          <blockquote>{e(text)}</blockquote>\n"
            f'          <cite><span class="avatar">{e(initial)}</span> {e(author)} · Google review</cite>\n'
            f"        </article>"
        )
    return "\n        ".join(cards)


def gym_faq_html(data: dict) -> str:
    gaps = data.get("gaps", {}).get("demo_should_highlight") or []
    hours = data.get("offerings", {}).get("hours") or "Mon–Sat, morning to evening"
    business = data.get("meta", {}).get("business") or "our gym"
    booking_gap = next((g for g in gaps if "book" in g.lower()), None)
    faqs = [
        ("Do you offer a free trial?", f"Yes — book a free trial session at {business}. No commitment required."),
        ("What are your timings?", hours),
        ("Can I book classes online?", booking_gap or "Call or WhatsApp us to reserve your spot. Online booking coming soon."),
        ("Do you have personal training?", "Yes — certified trainers offer 1-on-1 sessions. Ask when you visit."),
        ("Is parking available?", "Street parking is available near our location. Ask our front desk for directions."),
    ]
    items = []
    for q, a in faqs:
        items.append(
            f'<div class="faq-item">\n'
            f'          <button type="button" class="faq-q">{e(q)}<span class="chevron">▼</span></button>\n'
            f'          <div class="faq-a"><div class="faq-a-inner">{e(a)}</div></div>\n'
            f"        </div>"
        )
    return "\n        ".join(items)


def gym_social_links_html(data: dict) -> str:
    c = data.get("contact", {})
    links = []
    if c.get("instagram"):
        links.append(f'<a href="{e(c["instagram"])}" class="social-btn" target="_blank" rel="noopener">📸 Instagram</a>')
    if c.get("facebook"):
        links.append(f'<a href="{e(c["facebook"])}" class="social-btn" target="_blank" rel="noopener">👍 Facebook</a>')
    if c.get("email"):
        links.append(f'<a href="mailto:{e(c["email"])}" class="social-btn">✉️ Email</a>')
    return "\n            ".join(links) if links else ""


def gym_booking_options_html(services: list[str]) -> str:
    opts = ['<option value="Free trial">Free trial session</option>']
    for s in services[:10]:
        opts.append(f'<option value="{e(s)}">{e(s)}</option>')
    opts.append('<option value="Personal training">Personal training</option>')
    return "\n          ".join(opts)


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
    addr = (loc.get("address") or "").strip()
    landmark = (loc.get("landmark") or "").strip()
    city_line = ", ".join(
        x for x in [loc.get("city"), loc.get("state"), loc.get("pin")] if x
    ).strip()
    lines: list[str] = []
    if addr:
        lines.append(addr)
    else:
        if landmark:
            lines.append(landmark)
        if city_line:
            lines.append(city_line)
    addr_lower = addr.lower()
    if landmark and landmark.lower() not in addr_lower and landmark not in lines:
        lines.append(landmark)
    if city_line and city_line.lower() not in addr_lower and city_line not in lines:
        lines.append(city_line)
    return "<br>\n            ".join(e(x) for x in lines if x)


def map_query(data: dict) -> str:
    loc = data.get("location", {})
    meta = data.get("meta", {})
    parts = [
        meta.get("business"),
        loc.get("landmark"),
        loc.get("area"),
        loc.get("city"),
        loc.get("state"),
    ]
    return ", ".join(str(x).strip() for x in parts if x)


def map_directions_href(data: dict) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(map_query(data))}"


def gym_visit_media_html(data: dict) -> str:
    business = data.get("meta", {}).get("business", "Gym")
    map_href = map_directions_href(data)
    return (
        f'<a href="{map_href}" target="_blank" rel="noopener" class="visit-photo-link">\n'
        f'          <img src="{VISIT_GYM}" alt="{e(f"Visit {business}")}" loading="lazy">\n'
        f'          <span class="visit-map-pin">📍 Get directions on Google Maps</span>\n'
        f"        </a>"
    )


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


def gym_dark_float_cards_html(services: list[str], pri_href: str, pri_text: str) -> str:
    svcs = (services or ["Push-Ups", "Pull-Ups", "Squats", "Lunges", "Plank"])[:5]
    reps = ["3 × 12", "3 × 10", "4 × 8", "3 × 15", "3 × 12"]
    rows = "".join(
        f"<li><span>{e(s)}</span><span>{reps[i % len(reps)]}</span></li>" for i, s in enumerate(svcs)
    )
    cta = pri_text.upper() if len(pri_text) <= 18 else "BOOK NOW"
    return (
        f'<div class="float-card left">\n'
        f"          <strong>1 on 1 · Coach Session</strong>\n"
        f'          <span style="color:var(--muted)">Personal training available</span>\n'
        f'          <a href="{pri_href}" class="mini-btn">{e(cta)}</a>\n'
        f"        </div>\n"
        f'        <div class="float-card right">\n'
        f"          <strong>Sample Workout</strong>\n"
        f"          <ul>{rows}</ul>\n"
        f"        </div>"
    )


def gym_dark_classes_html(services: list[str]) -> tuple[str, str]:
    svcs = list(services) if services else ["Cardio", "Strength", "Yoga", "HIIT"]
    while len(svcs) < 4:
        svcs.append(svcs[-1])
    svcs = svcs[:4]
    items = []
    for i, svc in enumerate(svcs):
        img = GYM_IMAGES[i % len(GYM_IMAGES)]
        active = " active" if i == 0 else ""
        items.append(
            f'<div class="class-item{active}" data-img="{img}">\n'
            f'          <span class="class-num">{i + 1:02d}</span>\n'
            f"          <div><h3>{e(svc.upper())}</h3><p>Expert-led · all fitness levels</p></div>\n"
            f"        </div>"
        )
    return "\n        ".join(items), GYM_IMAGES[0]


def gym_dark_goals_html(data: dict) -> str:
    gaps = data.get("gaps", {}).get("demo_should_highlight") or []
    cards = [
        ("📅", "Smart Class Schedule", "View weekly programs and reserve your spot in seconds."),
        ("🏆", "Weekly Challenges", gaps[0] if gaps else "Stay motivated with community fitness goals."),
        ("💪", "1-on-1 Coaching", "Personal trainers to guide your form, nutrition, and progress."),
    ]
    out = []
    for icon, title, body in cards:
        out.append(
            f'<article class="goal-card">\n'
            f'          <div class="icon">{icon}</div>\n'
            f"          <h3>{e(title)}</h3>\n"
            f"          <p>{e(body)}</p>\n"
            f"        </article>"
        )
    return "\n        ".join(out)


def gym_dark_facilities_html(services: list[str]) -> str:
    labels = (services or ["Cardio Zone", "Free Weights", "Studio", "Recovery"])[:5]
    while len(labels) < 4:
        labels.append(labels[-1])
    items = []
    for i, label in enumerate(labels[:5]):
        wide = " wide" if i == 0 else ""
        img = GYM_IMAGES[i % len(GYM_IMAGES)]
        items.append(
            f'<div class="fac-item{wide}">\n'
            f'          <img src="{img}" alt="{e(label)}" loading="lazy">\n'
            f'          <span class="fac-label">{e(label)}</span>\n'
            f"        </div>"
        )
    return "\n        ".join(items)


def gym_dark_trainers_html() -> str:
    cards = []
    for i, (role, bio) in enumerate(GYM_TRAINER_ROLES):
        cards.append(
            f'<article class="trainer-card">\n'
            f'          <img src="{GYM_TRAINER_IMAGES[i]}" alt="{e(role)}" loading="lazy">\n'
            f'          <div class="info">\n'
            f'            <div class="role">{e(role)}</div>\n'
            f"            <h3>Coach {e(['Raj', 'Priya', 'Amit'][i])}</h3>\n"
            f"            <p>{e(bio)}</p>\n"
            f"          </div>\n"
            f"        </article>"
        )
    return "\n        ".join(cards)


def build_gym(data: dict, template_name: str = "gym-modern") -> str:
    if template_name == "gym-modern-dark":
        return _build_gym_modern_dark(data)
    return _build_gym_modern(data)


def _build_gym_modern_dark(data: dict) -> str:
    template = (TEMPLATES_DIR / "gym-modern-dark.html").read_text(encoding="utf-8")
    meta = data["meta"]
    ui = data["content_for_ui"]
    loc = data["location"]
    reviews = data.get("reviews", {})
    services = services_list(data)
    about = section_by_id(data, "about")
    phone = phone_digits(data.get("contact", {}).get("phone"))
    wa = phone_digits(data.get("contact", {}).get("whatsapp") or data.get("contact", {}).get("phone"))
    pri_href, pri_text, _ = primary_contact(data)
    sec_href, sec_text = secondary_contact(data)
    display = data.get("identity", {}).get("display_name") or meta["business"]
    rating_val = parse_rating(reviews.get("rating"))
    count = reviews.get("google_count") or 0
    rating_str = f"{rating_val:.1f}" if rating_val else "—"
    classes_html, preview_img = gym_dark_classes_html(list(services))
    name_upper = e(short_name(display).upper())

    mapping = {
        "PAGE_TITLE": e(f"{meta['business']} — {meta['city']}"),
        "LOGO_NAME": e(short_name(display).upper()),
        "CITY": e(meta["city"]),
        "NAV_CTA_HREF": pri_href,
        "NAV_CTA_TEXT": e(sticky_short(pri_text).upper()),
        "EYEBROW": e(f"{loc.get('area') or loc.get('city')}, {meta['city']}"),
        "HERO_H1": f"BUILD YOUR <em>STRONGEST</em> BODY WITH {name_upper}",
        "HERO_SUB": e(ui.get("hero_subhead") or "Expert trainers. Premium equipment. Results that last."),
        "HERO_IMG": HERO_GYM,
        "HERO_ALT": e(services[0] if services else "Fitness"),
        "HERO_FLOAT_CARDS_HTML": gym_dark_float_cards_html(list(services), pri_href, pri_text),
        "PRIMARY_CTA_HREF": pri_href,
        "PRIMARY_CTA_TEXT": e(pri_text.upper() if len(pri_text) <= 20 else "START FREE TRIAL"),
        "SECONDARY_CTA_HREF": sec_href,
        "SECONDARY_CTA_TEXT": e(sec_text),
        "STAT_REVIEWS": str(count) if count else "—",
        "STAT_RATING": rating_str if rating_val else "—",
        "STAT_OPEN": e(open_time_label(data.get("offerings", {}).get("hours"))),
        "PROGRAMS_BLURB": e(
            (about or {}).get("body")
            or f"From {services[0].lower() if services else 'cardio'} to {services[-1].lower() if len(services) > 1 else 'strength'} — programs for every level."
        ),
        "CLASSES_LIST_HTML": classes_html,
        "CLASS_PREVIEW_IMG": preview_img,
        "GOALS_HTML": gym_dark_goals_html(data),
        "FACILITIES_HTML": gym_dark_facilities_html(list(services)),
        "TRAINERS_HTML": gym_dark_trainers_html(),
        "VISIT_MEDIA_HTML": gym_visit_media_html(data),
        "MAP_DIRECTIONS_HREF": map_directions_href(data),
        "ADDRESS_HTML": address_html(data),
        "HOURS": e(data.get("offerings", {}).get("hours") or ""),
        "CALL_HREF": f"tel:+{phone}" if phone else pri_href,
        "CALL_LABEL": e(f"Call {phone_display(data.get('contact', {}).get('phone'))}" if phone else pri_text),
        "WA_HREF": f"https://wa.me/{wa}" if wa else sec_href,
        "FOOTER_1": e(ui.get("footer_tagline") or f"{meta['business']} — {meta['city']}"),
        "FOOTER_2": e(f"{short_name(display)} · Premium fitness · {meta['city']}"),
        "STICKY_PRIMARY_HREF": pri_href,
        "STICKY_PRIMARY_TEXT": e(sticky_short(pri_text)),
    }
    return fill_template(template, mapping)


def _build_gym_modern(data: dict) -> str:
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
    rating_val = parse_rating(reviews.get("rating"))
    count = reviews.get("google_count") or 0
    rating_str = f"{rating_val:.1f}" if rating_val else "—"

    mapping = {
        "PAGE_TITLE": e(f"{meta['business']} — {meta['city']}"),
        "LOGO_EMOJI": "🏋️",
        "LOGO_NAME": e(short_name(display)),
        "NAV_CTA_HREF": pri_href,
        "NAV_CTA_TEXT": e(pri_text),
        "HERO_IMG": HERO_GYM,
        "HERO_ALT": e(services[0] if services else "Fitness"),
        "EYEBROW": (
            f"<span>★ {rating_str}</span> · {count} Google reviews · "
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
        "STAT_RATING": rating_str if rating_val else "—",
        "STAT_RATING_DECIMAL": "1" if rating_val else "0",
        "STAT_OPEN": e(open_time_label(data.get("offerings", {}).get("hours"))),
        "SERVICE_CHIPS_HTML": gym_service_chips_html(list(services)),
        "MARQUEE_HTML": marquee_html(services + [meta["city"]]),
        "PROGRAMS_BLURB": e(
            (about or {}).get("body")
            or f"From {services[0].lower() if services else 'strength training'} to {services[-1].lower() if len(services) > 1 else 'group classes'} — programs for every fitness level."
        ),
        "BENTO_HTML": gym_bento_html(list(services)),
        "SCHEDULE_HTML": gym_schedule_html(list(services)),
        "PLANS_BLURB": e(
            f"Flexible memberships at {short_name(display)}. All plans include access to our main floor and expert guidance."
        ),
        "PLANS_HTML": gym_plans_html(list(services), meta["business"]),
        "PHONE_CLASSES_HTML": gym_phone_classes_html(list(services)),
        "TRAINERS_HTML": gym_trainers_html(),
        "TESTIMONIALS_HTML": gym_testimonials_html(data),
        "FAQ_HTML": gym_faq_html(data),
        "BOOKING_OPTIONS_HTML": gym_booking_options_html(list(services)),
        "WHY_TITLE": e(f"Why {short_name(display)}"),
        "WHY_BLURB": e(
            (data.get("identity", {}).get("tagline") or "")[:120]
            or "Strong community. Expert coaching. Results that last."
        ),
        "WHY_ITEMS_HTML": gym_why_html(data),
        "VISIT_MEDIA_HTML": gym_visit_media_html(data),
        "MAP_DIRECTIONS_HREF": map_directions_href(data),
        "ADDRESS_HTML": address_html(data),
        "HOURS": e(data.get("offerings", {}).get("hours") or ""),
        "CALL_HREF": f"tel:+{phone}" if phone else pri_href,
        "CALL_LABEL": e(f"Call {phone_display(data.get('contact', {}).get('phone'))}" if phone else pri_text),
        "WA_HREF": f"https://wa.me/{wa}" if wa else sec_href,
        "SOCIAL_LINKS_HTML": gym_social_links_html(data),
        "FOOTER_1": e(ui.get("footer_tagline") or f"{meta['business']} — {meta['city']}"),
        "FOOTER_2": e(f"{short_name(display)} · {loc.get('area') or meta['city']}"),
        "STICKY_PRIMARY_HREF": pri_href,
        "STICKY_PRIMARY_TEXT": e(sticky_short(pri_text)),
        "STICKY_SECONDARY_HREF": f"https://wa.me/{wa}" if wa else sec_href,
        "STICKY_SECONDARY_TEXT": "WhatsApp",
    }
    return fill_template(template, mapping)


def retail_services_html(services: list[str], price_hints: list[str]) -> str:
    icons = ["👗", "🤵", "✨", "💍", "✂️", "🛍️"]
    cards = []
    for i in range(6):
        if i < len(services):
            title = services[i]
            body = f"Curated {title.lower()} — quality fabrics and expert styling."
            price = price_hints[i] if i < len(price_hints) else "View collection"
        else:
            title, body, price = "New Arrivals", "Latest seasonal styles.", "Explore in store"
        cards.append(
            f'<article class="service-card reveal">\n'
            f'          <div class="icon">{icons[i]}</div>\n'
            f"          <h3>{e(title)}</h3>\n"
            f"          <p>{e(body)}</p>\n"
            f'          <span class="price-tag">{e(price)}</span>\n'
            f"        </article>"
        )
    return "\n        ".join(cards)


def retail_gallery_html() -> str:
    alts = ["Boutique interior", "Ethnic wear", "Bridal collection", "Designer suits", "Fashion display"]
    parts = [f'<div class="g-item wide"><img src="{RETAIL_IMAGES[0]}" alt="{e(alts[0])}" loading="lazy"></div>']
    for i in range(1, 5):
        parts.append(f'<div class="g-item"><img src="{RETAIL_IMAGES[i]}" alt="{e(alts[i])}" loading="lazy"></div>')
    return "\n        ".join(parts)


def build_retail(data: dict) -> str:
    template = (TEMPLATES_DIR / "retail-modern.html").read_text(encoding="utf-8")
    meta = data["meta"]
    ui = data["content_for_ui"]
    loc = data["location"]
    c = data.get("contact", {})
    services = services_list(data)
    prices = data.get("offerings", {}).get("price_hints") or []
    pri_href, pri_text, _ = primary_contact(data)
    sec_href, sec_text = secondary_contact(data)
    display = data.get("identity", {}).get("display_name") or meta["business"]
    tagline = data.get("identity", {}).get("tagline") or ""
    year = data.get("identity", {}).get("year_established")
    vibes = data.get("brand_signals", {}).get("vibe") or []
    gaps = data.get("gaps", {}).get("demo_should_highlight") or []
    quotes = data.get("reviews", {}).get("sample_quotes") or []
    fb = c.get("facebook")
    pills = (vibes[:2] + gaps[:2]) or ["Designer wear", "Custom tailoring", "Since 1975"]
    pills_html = "\n          ".join(f"<span>{e(p)}</span>" for p in pills[:4])
    quote = quotes[0] if quotes else tagline
    sec_href_btn = fb if fb else sec_href
    sec_label = "Instagram" if c.get("instagram") and not fb else ("Facebook" if fb else sec_text)
    if c.get("instagram") and sec_label == "Instagram":
        sec_href_btn = c["instagram"]

    mapping = {
        "PAGE_TITLE": e(f"{meta['business']} — {meta['city']}"),
        "LOGO_HTML": salon_logo_html(display),
        "NAV_CTA_HREF": "#book",
        "NAV_CTA_TEXT": "Shop Now",
        "HERO_BADGE": e(f"Designer Boutique · {loc.get('area') or loc.get('city')}, {meta['city']}" + (f" · Est. {year}" if year else "")),
        "HERO_H1": e(ui.get("hero_headline") or meta["business"]),
        "HERO_SUB": e(ui.get("hero_subhead") or ""),
        "PRIMARY_CTA_HREF": pri_href,
        "PRIMARY_CTA_TEXT": e(pri_text),
        "SECONDARY_CTA_HREF": sec_href,
        "SECONDARY_CTA_TEXT": e(sec_text),
        "HERO_IMG": HERO_RETAIL,
        "FLOAT_HOURS": e(data.get("offerings", {}).get("hours") or "Mon–Sat 10am–8pm"),
        "FLOAT_LOCATION": e(f"{loc.get('area') or loc.get('city')} · {meta['city']}"),
        "MARQUEE_HTML": marquee_html(services[:6] + [meta["city"]]),
        "SERVICES_TITLE": "Our Collections",
        "SERVICES_BLURB": e(tagline[:140] if tagline else "Premium designer wear for every occasion."),
        "SERVICES_HTML": retail_services_html(services, prices),
        "GALLERY_TITLE": e(f"Inside {short_name(display)}"),
        "GALLERY_HTML": retail_gallery_html(),
        "QUOTE": e(quote or tagline),
        "PILLS_HTML": pills_html,
        "ADDRESS_HTML": address_html(data),
        "HOURS": e(data.get("offerings", {}).get("hours") or ""),
        "VISIT_PRIMARY_HREF": pri_href,
        "VISIT_PRIMARY_TEXT": e(pri_text),
        "VISIT_SECONDARY_HREF": sec_href_btn,
        "VISIT_SECONDARY_TEXT": e(sec_label),
        "VISIT_IMG": RETAIL_IMAGES[1],
        "FOOTER_TEXT": e(ui.get("footer_tagline") or f"{meta['business']} — {meta['city']}"),
        "STICKY_PRIMARY_HREF": pri_href,
        "STICKY_PRIMARY_TEXT": "Book Now",
        "STICKY_SECONDARY_HREF": sec_href,
        "STICKY_SECONDARY_TEXT": "WhatsApp",
    }
    return fill_template(template, mapping)


def build_salon(data: dict, template_name: str = "salon-modern") -> str:
    template_file = "salon-aesthetic.html" if template_name == "salon-aesthetic" else "salon-modern.html"
    template = (TEMPLATES_DIR / template_file).read_text(encoding="utf-8")
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

    # Aesthetic template uses extra fields. Never invent facts; use safe defaults.
    reviews = data.get("reviews", {})
    google_count = reviews.get("google_count")
    year = data.get("identity", {}).get("year_established")

    about_sec = section_by_id(data, "about") or {}
    about_body = about_sec.get("body") or ui.get("footer_tagline") or tagline or ""
    about_blurb = tagline or (vibes[0] if vibes else "A calm, premium experience with attention to detail.")
    about_more = (
        "Quality products, thoughtful consultation, and a warm studio vibe — designed around your hair and skin goals."
        if not about_body
        else about_body
    )

    # Stats: use only observed facts; otherwise show neutral placeholders.
    stat_clients = str(google_count) if isinstance(google_count, int) and google_count > 0 else "—"
    stat_stylists = "—"
    stat_since = str(year) if year else "—"

    # Aesthetic template expects a row/list style services HTML; reuse existing services but in rows.
    def salon_services_rows_html(svcs: list[str]) -> str:
        picked = (svcs or [])[:8]
        defaults = [
            "Haircut & Styling",
            "Hair Color",
            "Facials",
            "Makeup",
            "Manicure / Pedicure",
            "Threading / Waxing",
        ]
        while len(picked) < 6:
            picked.append(defaults[len(picked) % len(defaults)])
        out = []
        for i, s in enumerate(picked[:6]):
            tag = "Popular" if i in (0, 1) else "Service"
            out.append(
                f'<div class="service-row">'
                f"<div><strong>{e(s)}</strong><br><span>Personalised consultation · Premium products</span></div>"
                f"<div><span>Book for pricing</span></div>"
                f'<div style="text-align:right"><span class="service-tag">{e(tag)}</span></div>'
                f"</div>"
            )
        return "\n          ".join(out)

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
        "SERVICES_TITLE": "Our Services",
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

        # Salon Aesthetic extra placeholders (safe defaults)
        "STAT_CLIENTS": e(stat_clients),
        "STAT_STYLISTS": e(stat_stylists),
        "STAT_SINCE": e(stat_since),
        "ABOUT_BLURB": e(about_blurb),
        "ABOUT_BODY": e(about_body or "A modern salon experience built around comfort, quality, and confidence."),
        "ABOUT_MORE": e(about_more),
        # When using salon-aesthetic, swap services html to row format
        "SERVICES_HTML": (
            salon_services_rows_html(services)
            if template_name == "salon-aesthetic"
            else salon_services_html(services)
        ),
    }
    return fill_template(template, mapping)


def write_outputs(data: dict, html: str, template_name: str, output_dir: Path | None = None, base_url: str | None = None) -> Path:
    slug = data["meta"]["slug"]
    out_root = output_dir if output_dir else DEMOS_DIR
    out_dir = out_root / slug
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
        "demo_url": (f"{base_url.rstrip('/')}/demos/{slug}/" if base_url else None),
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
    parser.add_argument(
        "--template",
        choices=["gym-modern", "gym-modern-dark", "salon-modern", "salon-aesthetic", "retail-modern"],
        help="Override automatic template pick",
    )
    parser.add_argument("--output-dir", help="Write demo into this directory (root).")
    parser.add_argument("--base-url", help="If set, writes meta.demo_url based on this base URL.")
    args = parser.parse_args()

    if not args.slug and not args.research:
        parser.error("Provide slug or --research path")

    research_path = Path(args.research).expanduser() if args.research else resolve_research_path(args.slug)
    data = load_research(research_path)
    template_name = args.template or pick_template_name(data["meta"].get("category", ""))

    if template_name in {"gym-modern", "gym-modern-dark"}:
        html = build_gym(data, template_name)
    elif template_name == "retail-modern":
        html = build_retail(data)
    elif template_name in {"salon-modern", "salon-aesthetic"}:
        html = build_salon(data, template_name)
    else:
        raise SystemExit(f"Unknown template '{template_name}'")

    output_dir = Path(args.output_dir).expanduser() if args.output_dir else None
    out = write_outputs(data, html, template_name, output_dir=output_dir, base_url=args.base_url)
    print(json.dumps({"ok": True, "slug": data["meta"]["slug"], "template": template_name, "demo_path": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
