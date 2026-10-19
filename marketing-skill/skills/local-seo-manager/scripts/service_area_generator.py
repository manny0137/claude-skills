#!/usr/bin/env python3
"""
service_area_generator.py — Service area page content generator for local businesses.

Generates a structured brief for a neighborhood-specific service area page,
including word-count targets, uniqueness checklist, FAQ starters, and
schema boilerplate for the page.

Usage:
    python3 service_area_generator.py [--config config.json] [--neighborhood "Richmond District"]
                                      [--industry moving] [--country NZ]
    python3 service_area_generator.py --sample   (runs sample demo — appliance repair, San Francisco)
    python3 service_area_generator.py --list-industries

Industry-specific sections (specialty H2, common-problems H2, FAQ starters,
differentiators) come from a built-in profile table. Profile resolution:
--industry flag > config "industry" > config "business_type" alias > generic.
Unknown industries fall back to generic sections built from your service list.

Output: Page brief as markdown, ready to hand to content-production skill or write directly.
"""

import json
import argparse
import sys
from typing import Dict, List, Optional, Tuple


# ─── Industry profiles ────────────────────────────────────────────────────────
# Placeholders available in profile strings: {neighborhood}, {city}, {service}
# ({service} = primary service, lower-cased). Keep entries short — they are
# writing prompts for a human or content skill, not finished copy.

INDUSTRY_PROFILES: Dict[str, Dict] = {
    "appliance-repair": {
        "label": "Appliance repair",
        "aliases": ["appliance", "appliance repair", "appliances"],
        "keyword": "appliance repair",
        "meta_hook": "Same-day service available.",
        "specialty_heading": "Appliance Brands We Service in {neighborhood}",
        "specialty_intro": "Write 1-2 sentences about each major brand. Brands: {items}",
        "specialty_angle": "Angle: our technicians are trained on [brand]-specific diagnostics and use OEM parts.",
        "specialty_items": ["Samsung", "LG", "Whirlpool", "GE", "Bosch", "Maytag", "KitchenAid", "Frigidaire"],
        "uses_brands": True,
        "problems_heading": "Common Appliance Problems in {neighborhood} Homes",
        "problems": [
            "Washer not draining (common in older building plumbing setups)",
            "Refrigerator not cooling (older homes with limited ventilation)",
            "Dryer overheating (lint buildup in older vented systems)",
        ],
        "differentiators": "same-day availability, {years} years serving {city}, warranty on parts and labor,\ncertified technicians, upfront pricing before work begins.",
        "faqs": [
            "How quickly can you reach {neighborhood} for appliance repair?",
            "What {service} services do you offer in {neighborhood}?",
            "Do you offer same-day appliance repair in {neighborhood}?",
            "Are your technicians licensed and insured in {city}?",
            "How much does {service} typically cost in {neighborhood}?",
        ],
    },
    "hvac": {
        "label": "HVAC / heating & cooling",
        "aliases": ["heating", "cooling", "air conditioning", "heat pump", "heating and cooling"],
        "keyword": "hvac repair",
        "meta_hook": "Emergency and same-day service available.",
        "specialty_heading": "Heating & Cooling Systems We Service in {neighborhood}",
        "specialty_intro": "Cover each system type and the brands you service. Systems/brands: {items}",
        "specialty_angle": "Angle: factory-trained on these systems; maintenance plans that protect manufacturer warranties.",
        "specialty_items": ["furnaces", "heat pumps", "central AC", "ductless mini-splits", "boilers", "Carrier", "Trane", "Lennox", "Daikin"],
        "uses_brands": True,
        "problems_heading": "Common Heating & Cooling Problems in {neighborhood} Homes",
        "problems": [
            "No heat on the first cold night (pilot, ignitor or thermostat faults)",
            "AC running but not cooling (low refrigerant, frozen coil, dirty filter)",
            "Uneven temperatures between rooms (duct leaks or undersized system in older homes)",
        ],
        "differentiators": "24/7 emergency response, {years} years serving {city}, licensed and certified technicians,\nflat-rate pricing, maintenance plans.",
        "faqs": [
            "Do you offer emergency HVAC service in {neighborhood}?",
            "How often should I service my heating and cooling system in {city}?",
            "Should I repair or replace my system?",
            "Are your HVAC technicians licensed and insured in {city}?",
            "How much does {service} typically cost in {neighborhood}?",
        ],
    },
    "plumbing": {
        "label": "Plumbing",
        "aliases": ["plumber", "plumbers", "drain", "drains"],
        "keyword": "plumber",
        "meta_hook": "Emergency plumbers available.",
        "specialty_heading": "Plumbing Services We Provide in {neighborhood}",
        "specialty_intro": "Write 1-2 sentences per service. Services: {items}",
        "specialty_angle": "Angle: what the homeowner notices, what we do about it, and how long it typically takes.",
        "specialty_items": ["leak detection & repair", "blocked drains", "hot water systems", "toilet & tap repair", "pipe replacement", "bathroom & kitchen plumbing"],
        "uses_brands": False,
        "problems_heading": "Common Plumbing Problems in {neighborhood} Homes",
        "problems": [
            "Slow or blocked drains (tree roots in older sewer lines)",
            "Low water pressure (corroded galvanized pipes in older housing stock)",
            "No hot water (failed element, thermostat or end-of-life cylinder)",
        ],
        "differentiators": "24/7 emergency call-outs, {years} years serving {city}, licensed plumbers,\nupfront quotes before work begins, workmanship guarantee.",
        "faqs": [
            "Do you offer emergency plumbing in {neighborhood}?",
            "How quickly can a plumber get to {neighborhood}?",
            "What {service} services do you offer in {neighborhood}?",
            "Are your plumbers licensed and insured in {city}?",
            "How much does a plumber typically cost in {neighborhood}?",
        ],
    },
    "electrical": {
        "label": "Electrical",
        "aliases": ["electrician", "electricians", "electric"],
        "keyword": "electrician",
        "meta_hook": "Licensed electricians, upfront quotes.",
        "specialty_heading": "Electrical Services We Provide in {neighborhood}",
        "specialty_intro": "Write 1-2 sentences per service. Services: {items}",
        "specialty_angle": "Angle: safety and code compliance — what needs a licensed electrician and why.",
        "specialty_items": ["fault finding", "switchboard upgrades", "rewiring", "lighting installation", "EV charger installation", "safety inspections"],
        "uses_brands": False,
        "problems_heading": "Common Electrical Problems in {neighborhood} Homes",
        "problems": [
            "Breakers tripping repeatedly (overloaded circuits in older wiring)",
            "Flickering lights (loose connections or failing fittings)",
            "Not enough outlets for modern loads (EV chargers, heat pumps, home offices)",
        ],
        "differentiators": "licensed and insured electricians, {years} years serving {city}, compliance certificates provided,\nupfront pricing, tidy work.",
        "faqs": [
            "Do you offer emergency electricians in {neighborhood}?",
            "Do I need an electrician to install an EV charger in {city}?",
            "What {service} services do you offer in {neighborhood}?",
            "Are your electricians licensed and insured in {city}?",
            "How much does an electrician typically cost in {neighborhood}?",
        ],
    },
    "cleaning": {
        "label": "Cleaning",
        "aliases": ["cleaner", "cleaners", "house cleaning", "maid service", "janitorial"],
        "keyword": "cleaners",
        "meta_hook": "Vetted, insured cleaners. Book online.",
        "specialty_heading": "Cleaning Services We Offer in {neighborhood}",
        "specialty_intro": "Write 1-2 sentences per service, including what is and is not included. Services: {items}",
        "specialty_angle": "Angle: a clear checklist of what gets cleaned, and how long a typical visit takes.",
        "specialty_items": ["regular house cleaning", "deep cleaning", "end-of-tenancy / move-out cleaning", "office cleaning", "carpet cleaning", "window cleaning"],
        "uses_brands": False,
        "problems_heading": "Cleaning Needs We See in {neighborhood}",
        "problems": [
            "End-of-tenancy cleans to get the bond/deposit back (rental-heavy streets)",
            "Busy households wanting a fortnightly regular clean",
            "Post-renovation dust in older homes being renovated",
        ],
        "differentiators": "vetted and insured cleaners, {years} years serving {city}, same cleaner each visit,\nsatisfaction guarantee (re-clean if anything is missed), eco-friendly products on request.",
        "faqs": [
            "Do you bring your own cleaning supplies to {neighborhood} homes?",
            "Do I need to be home while you clean?",
            "What does an end-of-tenancy clean in {city} include?",
            "Are your cleaners vetted and insured?",
            "How much does {service} typically cost in {neighborhood}?",
        ],
    },
    "moving": {
        "label": "Moving / removals",
        "aliases": ["movers", "mover", "removals", "removalists", "moving company", "relocation"],
        "keyword": "movers",
        "meta_hook": "Free quotes for local and long-distance moves.",
        "specialty_heading": "Moves We Handle in {neighborhood}",
        "specialty_intro": "Write 1-2 sentences per move type. Move types: {items}",
        "specialty_angle": "Angle: crew size, truck size and typical duration for each move type.",
        "specialty_items": ["apartment & flat moves", "family home moves", "office relocations", "long-distance moves", "packing & unpacking", "storage"],
        "uses_brands": False,
        "problems_heading": "Moving Challenges in {neighborhood}",
        "problems": [
            "Narrow streets and limited truck parking (permits or loading-zone bookings)",
            "Apartment buildings with lift bookings, stairs or strict move-in windows",
            "Heavy or fragile items (pianos, antiques, artwork) that need extra crew or crating",
        ],
        "differentiators": "fixed-price quotes, {years} years moving {city} households, insured goods in transit,\ntrained crews (not day labour), protective padding and floor covers as standard.",
        "faqs": [
            "How far in advance should I book movers in {neighborhood}?",
            "Do you offer fixed-price quotes for moves in {city}?",
            "Are my belongings insured during the move?",
            "Can you help with packing and storage?",
            "How much does {service} typically cost in {neighborhood}?",
        ],
    },
}

GENERIC_PROFILE: Dict = {
    "label": "Generic (any service-area business)",
    "aliases": [],
    "keyword": None,  # falls back to the primary service
    "meta_hook": "Serving {neighborhood} and surrounding areas.",
    "specialty_heading": "Services We Offer in {neighborhood}",
    "specialty_intro": "Write 1-2 sentences per service. Services: {items}",
    "specialty_angle": "Angle: what the customer gets, how long it takes, and what makes your approach different.",
    "specialty_items": [],  # filled from the config's service list
    "uses_brands": False,
    "problems_heading": "Common {service_title} Needs in {neighborhood}",
    "problems": [
        "A need specific to the housing stock or businesses in {neighborhood}",
        "A seasonal or time-sensitive need customers in {city} search for",
        "A situation where customers usually call too late, and what it costs them",
    ],
    "differentiators": "response time, {years} years serving {city}, licensing/insurance,\nguarantees, upfront pricing.",
    "faqs": [
        "How quickly can you reach {neighborhood}?",
        "What {service} services do you offer in {neighborhood}?",
        "Do you serve areas near {neighborhood}?",
        "Are you licensed and insured in {city}?",
        "How much does {service} typically cost in {neighborhood}?",
    ],
}


def resolve_industry(industry: Optional[str], business_type: str = '') -> Tuple[str, Dict]:
    """Return (profile_key, profile). Explicit industry wins; else match business_type; else generic."""
    for candidate in (industry, business_type):
        if not candidate:
            continue
        needle = candidate.strip().lower().replace('_', '-')
        for key, profile in INDUSTRY_PROFILES.items():
            if needle == key or needle in profile['aliases'] or needle.replace('-', ' ') in profile['aliases']:
                return key, profile
        if candidate is industry and needle != 'generic':
            print(f"[WARN] Unknown --industry '{candidate}'. Using generic sections. "
                  f"Known: {', '.join(INDUSTRY_PROFILES)}", file=sys.stderr)
            break
    return 'generic', GENERIC_PROFILE


# ─── Page brief builder ───────────────────────────────────────────────────────

def build_page_brief(
    business_name: str,
    business_type: str,
    services: List[str],
    primary_service: str,
    neighborhood: str,
    city: str,
    state: str,
    phone: str,
    website: str,
    years_in_business: int,
    brands_serviced: Optional[List[str]] = None,
    nearby_neighborhoods: Optional[List[str]] = None,
    zip_code: str = '',
    landmark: str = '',
    industry: Optional[str] = None,
    country: str = 'US',
) -> str:
    _, profile = resolve_industry(industry, business_type)
    nearby = nearby_neighborhoods or []
    service_list = ', '.join(services)
    postal_label = 'zip code' if country.upper() == 'US' else 'postcode'

    fmt = {
        'neighborhood': neighborhood,
        'city': city,
        'service': primary_service.lower(),
        'service_title': primary_service,
        'years': years_in_business,
    }

    def f(text: str) -> str:
        return text.format(**fmt)

    # Specialty items: a user-supplied brand list wins for brand-led industries;
    # otherwise the profile's defaults; generic falls back to the service list.
    if profile['uses_brands'] and brands_serviced:
        specialty_items = brands_serviced
    else:
        specialty_items = profile['specialty_items'] or services
    keyword = profile['keyword'] or primary_service.lower()

    title = f"{primary_service} in {neighborhood}, {city} | {business_name}"
    meta_desc = (
        f"{business_name} provides professional {primary_service.lower()} in {neighborhood}, {city}, {state}. "
        f"{f(profile['meta_hook'])} Call {phone} or book online."
    )

    slug = f"{primary_service.lower().replace(' ', '-')}-{neighborhood.lower().replace(' ', '-')}-{city.lower().replace(' ', '-')}"

    lines = []
    lines.append(f"# Page Brief: {title}")
    lines.append(f"\n**URL slug:** `/{slug}/`")
    lines.append(f"**Target word count:** 1,000-1,500 words")
    lines.append(f"**Primary keyword:** {primary_service} in {neighborhood}")
    secondary = [f"{primary_service.lower()} {neighborhood.lower()}", f"{primary_service.lower()} near {neighborhood.lower()}"]
    if zip_code:
        secondary.append(f"{keyword} {zip_code}")
    elif keyword != primary_service.lower():
        secondary.append(f"{keyword} {neighborhood.lower()}")
    lines.append(f"**Secondary keywords:** {', '.join(secondary)}")
    lines.append(f"**Schema required:** LocalBusiness + Service + FAQPage")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"## SEO Metadata")
    lines.append(f"")
    lines.append(f"**Title tag:** {title}")
    lines.append(f"**Meta description:** {meta_desc}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"## Page Structure")
    lines.append("")

    lines.append(f"### H1: {primary_service} in {neighborhood}")
    lines.append("")
    lines.append(f"**Opening paragraph (~150 words):**")
    lines.append(f"Write a unique intro for {neighborhood}. Must include:")
    lines.append(f"- Neighborhood name in first sentence")
    lines.append(f"- Primary service ({primary_service.lower()}) in first two sentences")
    lines.append(f"- {business_name}'s years of experience ({years_in_business} years)")
    lines.append(f"- Identify {business_name} as a {business_type} business, and reference the core services offered: {service_list}")
    lines.append(f"- One specific local reference (landmark, cross-street, or characteristic of {neighborhood})")
    if landmark:
        lines.append(f"- Suggested landmark to mention: {landmark}")
    lines.append(f"- DO NOT use: 'look no further', 'your one-stop shop', 'we are proud to'")
    lines.append("")

    lines.append(f"### H2: {f(profile['specialty_heading'])}")
    lines.append(profile['specialty_intro'].format(items=', '.join(specialty_items)))
    lines.append(f(profile['specialty_angle']))
    if not profile['uses_brands'] and brands_serviced:
        lines.append(f"Also mention brands/products you work with: {', '.join(brands_serviced)}")
    lines.append("")

    lines.append(f"### H2: Our {neighborhood} Service Area")
    lines.append(f"Describe the coverage boundaries: streets, {postal_label}s, adjacent areas.")
    if zip_code:
        lines.append(f"Mention {postal_label}: {zip_code}")
    if nearby:
        lines.append(f"Mention nearby neighborhoods we also serve: {', '.join(nearby)}")
        lines.append(f"(Include internal links to those service area pages if they exist)")
    lines.append("")

    lines.append(f"### H2: {f(profile['problems_heading'])}")
    lines.append(f"Write 3-5 specific scenarios relevant to the area. Examples:")
    for problem in profile['problems']:
        lines.append(f"- {f(problem)}")
    lines.append(f"Add one 2-3 sentence explanation per scenario. This section drives local relevance.")
    lines.append("")

    lines.append(f"### H2: Why {neighborhood} Residents Choose {business_name}")
    lines.append(f"3-4 differentiators. Be specific — no generic claims.")
    lines.append(f"Examples: {f(profile['differentiators'])}")
    lines.append("")

    lines.append(f"### H2: Frequently Asked Questions")
    lines.append(f"Write 5 Q&A pairs. Use FAQPage schema on these.")
    lines.append(f"Suggested questions:")
    for i, question in enumerate(profile['faqs'], 1):
        lines.append(f"{i}. {f(question)}")
    lines.append("")

    lines.append(f"### H2: Book {primary_service} in {neighborhood}")
    lines.append(f"CTA section. Include:")
    lines.append(f"- Phone: {phone}")
    lines.append(f"- Website: {website}")
    lines.append(f"- Hours (if known)")
    lines.append(f"- Restate service area: '{business_name} serves {neighborhood} and surrounding areas in {city}, {state}.'")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Schema to Add")
    lines.append("")
    lines.append("Run `scripts/schema_generator.py` with `--type service-area` to generate the JSON-LD"
                 + (f" (add `--country {country.upper()}`)" if country.upper() != 'US' else '') + ".")
    lines.append("Required schema blocks for this page:")
    lines.append("1. `LocalBusiness` — business entity (name, address, phone, url)")
    lines.append("2. `Service` — the specific service on this page")
    lines.append("3. `FAQPage` — wrap the FAQ H2 section")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Uniqueness Checklist")
    lines.append("")
    lines.append("Before publishing, verify:")
    lines.append(f"- [ ] Opening paragraph is NOT copied from another neighborhood page")
    lines.append(f"- [ ] At least 2 {neighborhood}-specific references (landmarks, streets, {postal_label}, characteristics)")
    lines.append(f"- [ ] Internal links TO: main {primary_service.lower()} page + 2 nearby neighborhood pages")
    lines.append(f"- [ ] Internal link FROM: at least the main {primary_service.lower()} page to this page")
    lines.append(f"- [ ] Meta description is unique (not shared with any other page)")
    lines.append(f"- [ ] FAQ questions are specific to this neighborhood (not generic)")
    lines.append("")

    return '\n'.join(lines)


# ─── Sample data ──────────────────────────────────────────────────────────────

SAMPLE_CONFIG = {
    "business_name": "Smart Solution Appliances",
    "business_type": "appliance repair",
    "primary_service": "Appliance Repair",
    "services": ["washer repair", "dryer repair", "refrigerator repair", "dishwasher repair", "oven repair", "microwave repair"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "(415) 555-0100",
    "website": "https://smartsolutionappliances.com",
    "years_in_business": 10,
    "brands_serviced": ["Samsung", "LG", "Whirlpool", "GE", "Bosch", "Maytag", "KitchenAid", "Frigidaire", "Electrolux"]
}

SAMPLE_NEIGHBORHOODS = [
    {"neighborhood": "Richmond District", "zip": "94118", "landmark": "Golden Gate Park", "nearby": ["Sunset District", "Presidio Heights", "Inner Richmond"]},
    {"neighborhood": "Mission District", "zip": "94110", "landmark": "Dolores Park", "nearby": ["Bernal Heights", "Noe Valley", "Castro"]},
    {"neighborhood": "Pacific Heights", "zip": "94115", "landmark": "Lafayette Park", "nearby": ["Cow Hollow", "Marina District", "Lower Pacific Heights"]},
]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Service area page brief generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--config', help='Path to business config JSON')
    source.add_argument('--sample', action='store_true', help='Run the sample demo (appliance repair, San Francisco)')
    parser.add_argument('--neighborhood', help='Neighborhood name to generate for')
    parser.add_argument('--zip', '--postcode', dest='zip', help='Zip code / postcode for the neighborhood')
    parser.add_argument('--landmark', help='Local landmark to reference', default='')
    parser.add_argument('--nearby', help='Comma-separated nearby neighborhoods', default='')
    parser.add_argument('--industry', default=None,
                        help=f"Industry profile for industry-specific sections: {', '.join(INDUSTRY_PROFILES)}, generic "
                             "(default: config industry, else inferred from config business_type, else generic)")
    parser.add_argument('--country', default=None,
                        help='ISO 3166-1 alpha-2 country code; non-US uses "postcode" wording (default: config country, else US)')
    parser.add_argument('--list-industries', action='store_true', help='List built-in industry profiles and exit')
    parser.add_argument('--all-sample', action='store_true', help='Generate briefs for all sample neighborhoods')
    args = parser.parse_args()

    if args.list_industries:
        for key, profile in INDUSTRY_PROFILES.items():
            print(f"{key:<18} {profile['label']}  (aliases: {', '.join(profile['aliases'])})")
        print(f"{'generic':<18} {GENERIC_PROFILE['label']}  (fallback)")
        return

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = SAMPLE_CONFIG
        if not args.neighborhood:
            print('[INFO] No --config or --neighborhood provided. Running sample demo.\n')

    industry = args.industry or config.get('industry')
    country = (args.country or config.get('country') or 'US').strip().upper()

    def brief_for(neighborhood: str, zip_code: str, landmark: str, nearby: List[str]) -> str:
        return build_page_brief(
            business_name=config['business_name'],
            business_type=config.get('business_type', ''),
            services=config['services'],
            primary_service=config['primary_service'],
            neighborhood=neighborhood,
            city=config['city'],
            state=config.get('state', ''),
            phone=config['phone'],
            website=config['website'],
            years_in_business=config.get('years_in_business', 0),
            brands_serviced=config.get('brands_serviced'),
            nearby_neighborhoods=nearby,
            zip_code=zip_code,
            landmark=landmark,
            industry=industry,
            country=country,
        )

    if args.all_sample:
        for nb in SAMPLE_NEIGHBORHOODS:
            print(brief_for(nb['neighborhood'], nb.get('zip', ''), nb.get('landmark', ''), nb.get('nearby', [])))
            print('\n' + '=' * 65 + '\n')
        return

    neighborhood = args.neighborhood or SAMPLE_NEIGHBORHOODS[0]['neighborhood']
    nearby = [n.strip() for n in args.nearby.split(',')] if args.nearby else []
    print(brief_for(neighborhood, args.zip or '', args.landmark or '', nearby))


if __name__ == '__main__':
    main()
