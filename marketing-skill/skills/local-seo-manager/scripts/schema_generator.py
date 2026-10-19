#!/usr/bin/env python3
"""
schema_generator.py — LocalBusiness JSON-LD schema generator for local service businesses.

Generates valid schema.org JSON-LD for LocalBusiness, HomeAndConstructionBusiness,
Service, and FAQPage types — ready to paste into WordPress (Rank Math custom schema
or wp_head hook) or any HTML <head>.

Usage:
    python3 schema_generator.py [--config config.json] [--type local-business|service-area|faq]
                                [--country NZ] [--business-type MovingCompany]
    python3 schema_generator.py --sample

If no config provided (or --sample is passed), runs with embedded sample data.

--country        ISO 3166-1 alpha-2 code for addressCountry (default: config
                 address.country or country, else "US").
--business-type  schema.org LocalBusiness subtype, e.g. MovingCompany, Plumber,
                 HVACBusiness, Electrician, HousePainter, Locksmith. Default:
                 ["LocalBusiness", "HomeAndConstructionBusiness"].

Output: JSON-LD block(s) ready for <script type="application/ld+json"> tags.
"""

import json
import argparse
import re
import sys
from typing import Dict, List, Optional


DEFAULT_COUNTRY = "US"
DEFAULT_BUSINESS_TYPE = ["LocalBusiness", "HomeAndConstructionBusiness"]

# Common schema.org LocalBusiness subtypes for service-area businesses. Not
# exhaustive — an unlisted subtype is still emitted, with a stderr warning so a
# typo (e.g. "MovingCompnay") is caught before it reaches the validator.
KNOWN_BUSINESS_TYPES = {
    "LocalBusiness", "HomeAndConstructionBusiness", "ProfessionalService",
    "MovingCompany", "Plumber", "HVACBusiness", "Electrician", "RoofingContractor",
    "GeneralContractor", "HousePainter", "Locksmith", "AutoRepair", "AutomotiveBusiness",
    "DryCleaningOrLaundry", "EmergencyService", "SelfStorage", "AnimalShelter",
    "ChildCare", "HealthAndBeautyBusiness", "LegalService", "Attorney",
    "FinancialService", "AccountingService", "RealEstateAgent", "TravelAgency",
    "Dentist", "MedicalBusiness", "Store", "HomeGoodsStore", "HardwareStore",
}


def resolve_country(cli_value: Optional[str], config: Dict) -> str:
    """CLI flag > config address.country / country > "US". Validated as ISO 3166-1 alpha-2."""
    value = (cli_value or config.get('address', {}).get('country') or config.get('country')
             or DEFAULT_COUNTRY)
    value = value.strip().upper()
    if not re.fullmatch(r'[A-Z]{2}', value):
        raise ValueError(f"--country must be an ISO 3166-1 alpha-2 code (e.g. US, NZ, GB), got {value!r}")
    return value


def resolve_business_type(cli_value: Optional[str], config: Dict):
    """CLI flag > config schema_type > default LocalBusiness + HomeAndConstructionBusiness."""
    value = cli_value or config.get('schema_type')
    if not value:
        return list(DEFAULT_BUSINESS_TYPE)
    value = value.strip()
    if not re.fullmatch(r'[A-Z][A-Za-z]+', value):
        raise ValueError(f"--business-type must be a schema.org type name in PascalCase (e.g. MovingCompany), got {value!r}")
    if value not in KNOWN_BUSINESS_TYPES:
        print(f"[WARN] '{value}' is not in the built-in list of LocalBusiness subtypes — "
              f"check spelling at https://schema.org/{value}", file=sys.stderr)
    return value


# ─── Schema builders ──────────────────────────────────────────────────────────

def build_local_business(config: Dict, country: str = DEFAULT_COUNTRY, business_type=None) -> Dict:
    """Build LocalBusiness schema (default type: LocalBusiness + HomeAndConstructionBusiness)."""
    address = config.get('address', {})
    schema = {
        "@context": "https://schema.org",
        "@type": business_type or list(DEFAULT_BUSINESS_TYPE),
        "name": config['business_name'],
        "url": config['website'],
        "telephone": config['phone'],
        "priceRange": config.get('price_range', '$$'),
        "image": config.get('logo_url', ''),
        "description": config.get('description', ''),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address.get('street', ''),
            "addressLocality": address.get('city', ''),
            "addressRegion": address.get('state', ''),
            "postalCode": address.get('zip', ''),
            "addressCountry": country
        },
        "openingHoursSpecification": _build_hours(config.get('hours', {})),
        "sameAs": config.get('social_profiles', []),
        "hasMap": config.get('google_maps_url', ''),
        "areaServed": _build_area_served(config.get('service_areas', [])),
        "knowsAbout": config.get('services', []),
        "aggregateRating": _build_aggregate_rating(config.get('reviews', {})),
    }
    # Only emit geo coordinates when BOTH are supplied — blank lat/long is invalid
    # per the Rich Results validator this skill tells users to run.
    lat = config.get('latitude', '')
    lng = config.get('longitude', '')
    if lat not in ('', None) and lng not in ('', None):
        schema["geo"] = {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng}
    # Clean empty values
    schema = {k: v for k, v in schema.items() if v not in ('', [], {}, None)}
    return schema


def build_service(config: Dict, service_name: str, neighborhood: str = '', description: str = '',
                  business_type=None) -> Dict:
    """Build Service schema for a specific service page."""
    # The provider is a single entity reference — use the specific subtype when one was given.
    provider_type = business_type if isinstance(business_type, str) else "LocalBusiness"
    schema = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": service_name,
        "provider": {
            "@type": provider_type,
            "name": config['business_name'],
            "telephone": config['phone'],
            "url": config['website'],
        },
        "areaServed": {
            "@type": "City",
            "name": config.get('city', ''),
        },
        "description": description or f"Professional {service_name.lower()} in {neighborhood or config.get('city', '')}.",
    }
    if neighborhood:
        schema["areaServed"] = {
            "@type": "Place",
            "name": f"{neighborhood}, {config.get('city', '')}",
        }
    return schema


def build_faq_page(faqs: List[Dict]) -> Dict:
    """Build FAQPage schema from list of {question, answer} dicts."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq['answer']
                }
            }
            for faq in faqs
        ]
    }


def build_service_area_page_schemas(config: Dict, neighborhood: str, primary_service: str,
                                    faqs: Optional[List[Dict]] = None,
                                    country: str = DEFAULT_COUNTRY, business_type=None) -> List[Dict]:
    """Return all schema blocks needed for a service area page."""
    schemas = [
        build_local_business(config, country=country, business_type=business_type),
        build_service(config, primary_service, neighborhood, business_type=business_type),
    ]
    if faqs:
        schemas.append(build_faq_page(faqs))
    return schemas


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_hours(hours: Dict) -> List[Dict]:
    if not hours:
        return []
    day_map = {
        'monday': 'Monday', 'tuesday': 'Tuesday', 'wednesday': 'Wednesday',
        'thursday': 'Thursday', 'friday': 'Friday', 'saturday': 'Saturday', 'sunday': 'Sunday'
    }
    specs = []
    for day, times in hours.items():
        if times and times.get('open') and times.get('close'):
            specs.append({
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": f"https://schema.org/{day_map.get(day.lower(), day)}",
                "opens": times['open'],
                "closes": times['close']
            })
    return specs


def _build_area_served(areas: List[str]) -> List[Dict]:
    return [{"@type": "Place", "name": area} for area in areas]


def _build_aggregate_rating(reviews: Dict) -> Optional[Dict]:
    # Require BOTH count and average — never fabricate a rating value. Google
    # cross-checks aggregateRating against GBP; a made-up score risks a manual
    # action (see references/local-schema-types.md).
    if not reviews or not reviews.get('count') or not reviews.get('average'):
        return None
    return {
        "@type": "AggregateRating",
        "ratingValue": str(reviews['average']),
        "bestRating": "5",
        "worstRating": "1",
        "ratingCount": str(reviews['count'])
    }


def format_as_script_tag(schema: Dict) -> str:
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


# ─── Sample data ──────────────────────────────────────────────────────────────

SAMPLE_CONFIG = {
    "business_name": "Smart Solution Appliances",
    "website": "https://smartsolutionappliances.com",
    "phone": "(415) 555-0100",
    "price_range": "$$",
    "city": "San Francisco",
    "primary_service": "Appliance Repair",
    "description": "Professional appliance repair in San Francisco. Same-day service for washers, dryers, refrigerators, dishwashers, and ovens.",
    "address": {
        "street": "123 Market Street",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94102"
    },
    "hours": {
        "monday": {"open": "08:00", "close": "18:00"},
        "tuesday": {"open": "08:00", "close": "18:00"},
        "wednesday": {"open": "08:00", "close": "18:00"},
        "thursday": {"open": "08:00", "close": "18:00"},
        "friday": {"open": "08:00", "close": "18:00"},
        "saturday": {"open": "09:00", "close": "15:00"},
        "sunday": {"open": "", "close": ""}
    },
    "services": ["Washer Repair", "Dryer Repair", "Refrigerator Repair", "Dishwasher Repair", "Oven Repair"],
    "service_areas": ["San Francisco", "Richmond District", "Mission District", "Pacific Heights", "Sunset District"],
    "social_profiles": [
        "https://www.yelp.com/biz/smart-solution-appliances-san-francisco",
        "https://www.facebook.com/smartsolutionappliances"
    ],
    "reviews": {"average": 4.8, "count": 124}
}

SAMPLE_FAQS = [
    {
        "question": "How quickly can you reach the Richmond District for appliance repair?",
        "answer": "We offer same-day service in the Richmond District. Call before noon and we can typically arrive the same afternoon."
    },
    {
        "question": "What appliance brands do you service in the Richmond District?",
        "answer": "We repair all major brands including Samsung, LG, Whirlpool, GE, Bosch, Maytag, KitchenAid, Frigidaire, and Electrolux."
    },
    {
        "question": "Are your technicians licensed and insured in San Francisco?",
        "answer": "Yes. All Smart Solution Appliances technicians are fully licensed, bonded, and insured in California."
    },
    {
        "question": "Do you offer a warranty on appliance repairs in Richmond District?",
        "answer": "Yes. All repairs come with a 90-day parts and labor warranty."
    },
]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='LocalBusiness JSON-LD schema generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--config', help='Path to business config JSON')
    source.add_argument('--sample', action='store_true', help='Run with embedded sample data (appliance repair, San Francisco)')
    parser.add_argument('--type', choices=['local-business', 'service-area', 'faq'], default='local-business',
                        help='Schema type to generate')
    parser.add_argument('--country', default=None,
                        help='ISO 3166-1 alpha-2 country code for addressCountry (default: config address.country or country, else US)')
    parser.add_argument('--business-type', default=None,
                        help='schema.org LocalBusiness subtype, e.g. MovingCompany, Plumber, HVACBusiness '
                             '(default: config schema_type, else LocalBusiness + HomeAndConstructionBusiness)')
    parser.add_argument('--neighborhood', help='Neighborhood (for service-area type)', default='')
    parser.add_argument('--service', default=None,
                        help='Service name (for service-area type; default: config primary_service, '
                             'else first config service, else "Appliance Repair")')
    parser.add_argument('--faqs', help='Path to FAQs JSON (for faq / service-area type; default: config faqs)')
    parser.add_argument('--html', action='store_true', help='Output as <script> HTML tag')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = SAMPLE_CONFIG
        print('[INFO] No --config provided. Using sample data.\n')

    try:
        country = resolve_country(args.country, config)
        business_type = resolve_business_type(args.business_type, config)
    except ValueError as e:
        parser.error(str(e))

    # Sample FAQs are appliance-repair copy for the sample business — only fall
    # back to them for the sample run, never for a user-supplied config.
    faqs = None
    if args.faqs:
        with open(args.faqs) as f:
            faqs = json.load(f)
    elif args.config:
        faqs = config.get('faqs')
    elif args.type in ('service-area', 'faq'):
        faqs = SAMPLE_FAQS

    service = (args.service or config.get('primary_service')
               or (config.get('services') or [None])[0] or 'Appliance Repair')

    if args.type == 'local-business':
        schemas = [build_local_business(config, country=country, business_type=business_type)]
    elif args.type == 'service-area':
        schemas = build_service_area_page_schemas(
            config,
            neighborhood=args.neighborhood or ('Richmond District' if not args.config else ''),
            primary_service=service,
            faqs=faqs,
            country=country,
            business_type=business_type,
        )
    elif args.type == 'faq':
        if not faqs:
            parser.error('--type faq needs FAQs: pass --faqs faqs.json or add a "faqs" list to the config')
        schemas = [build_faq_page(faqs)]
    else:
        schemas = [build_local_business(config, country=country, business_type=business_type)]

    for schema in schemas:
        if args.html:
            print(format_as_script_tag(schema))
        else:
            print(json.dumps(schema, indent=2))
        print()

    if not args.html:
        print('─' * 65)
        print('Paste each block inside a <script type="application/ld+json"> tag.')
        print('Validate at: https://validator.schema.org/')
        print('Test rich results at: https://search.google.com/test/rich-results')


if __name__ == '__main__':
    main()
