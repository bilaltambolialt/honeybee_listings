"""Collector 2: business listings from the Geoapify Places API.

Terms: Geoapify allows API results to be cached, stored and redistributed. The free plan
(3,000 credits/day, 5 requests/s) requires attribution: "Powered by Geoapify" and
"(c) OpenStreetMap contributors". This script uses ~156 credits (78 requests x 2 credits).

Geoapify enriches OpenStreetMap data with structured addresses. To keep sources distinct,
places already collected by osm_overpass.py (matched by OSM id) are skipped.

Needs GEOAPIFY_API_KEY in the project-root .env. Run from the project root:
    scraper\\venv\\Scripts\\python scraper\\geoapify_places.py
"""
import csv
import os
import time
from collections import defaultdict
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from common import CITIES, RAW_DIR, ROOT_DIR, USER_AGENT, get_logger, write_raw_csv

API_URL = "https://api.geoapify.com/v2/places"
RADIUS_M = 10_000
RESULTS_PER_REQUEST = 40   # 2 credits per request; gives room to skip overlaps
PAUSE_SECONDS = 0.5        # stays well under the 5 requests/second limit
MAX_PER_GROUP = 5          # same balance rule as the OSM collector

# Geoapify category -> our category name (same 13 categories as the OSM collector)
CATEGORIES: dict[str, str] = {
    "catering.cafe": "Cafe",
    "catering.restaurant": "Restaurant",
    "healthcare.pharmacy": "Pharmacy",
    "healthcare.hospital": "Hospital",
    "healthcare.clinic_or_praxis": "Clinic",
    "healthcare.dentist": "Dentist",
    "service.financial.bank": "Bank",
    "commercial.supermarket": "Supermarket",
    "commercial.food_and_drink.bakery": "Bakery",
    "commercial.elektronics": "Electronics Store",  # Geoapify's own spelling
    "service.beauty.hairdresser": "Salon",
    "sport.fitness.fitness_centre": "Gym",
    "accommodation.hotel": "Hotel",
}

OSM_TYPES = {"n": "node", "w": "way", "r": "relation"}

log = get_logger("geoapify")


def already_collected_osm_ids() -> set[str]:
    """source_id values ("node/123") from the OSM collector's output, if it exists."""
    path = RAW_DIR / "osm_overpass.csv"
    if not path.exists():
        return set()
    with path.open(encoding="utf-8-sig") as f:
        return {row["source_id"] for row in csv.DictReader(f)}


def fetch(category: str, lat: float, lon: float, api_key: str) -> list[dict]:
    params = {
        "categories": category,
        "filter": f"circle:{lon},{lat},{RADIUS_M}",  # Geoapify expects lon before lat
        "limit": RESULTS_PER_REQUEST,
        "apiKey": api_key,
    }
    for attempt in range(1, 4):
        try:
            resp = requests.get(API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("features", [])
            log.warning("HTTP %s for %s (attempt %d)", resp.status_code, category, attempt)
        except requests.RequestException as exc:
            log.warning("%s failed: %s (attempt %d)", category, exc, attempt)
        time.sleep(5 * attempt)
    log.error("Giving up on %s", category)
    return []


def to_row(feature: dict, category: str, city: str, scraped_at: str) -> dict | None:
    props = feature.get("properties", {})
    name = props.get("name")
    if not name:
        return None
    raw = props.get("datasource", {}).get("raw", {})
    phone = props.get("contact", {}).get("phone") or raw.get("phone") or raw.get("contact:phone")
    osm_type, osm_id = raw.get("osm_type"), raw.get("osm_id")
    return {
        "business_name": name,
        "category": category,
        "city": city,
        "address": props.get("address_line2"),
        "phone": phone,
        "source": "Geoapify",
        "source_id": f"{OSM_TYPES.get(osm_type, osm_type)}/{osm_id}" if osm_id else props.get("place_id"),
        "latitude": props.get("lat"),
        "longitude": props.get("lon"),
        "scraped_at": scraped_at,
        # A street name means a real street address, not just "suburb, city, state"
        "_has_street": bool(props.get("street")),
    }


def main() -> None:
    load_dotenv(ROOT_DIR / ".env")
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        raise SystemExit("GEOAPIFY_API_KEY is missing from .env")

    skip_ids = already_collected_osm_ids()
    log.info("Skipping %d places already collected from OpenStreetMap", len(skip_ids))
    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    selected: list[dict] = []
    seen_ids: set[str] = set()
    stats = defaultdict(int)
    for city, (lat, lon) in CITIES.items():
        city_count = 0
        for geo_category, category in CATEGORIES.items():
            features = fetch(geo_category, lat, lon, api_key)
            time.sleep(PAUSE_SECONDS)
            rows = [r for f in features if (r := to_row(f, category, city, scraped_at))]
            stats["found"] += len(rows)
            fresh = [r for r in rows if r["source_id"] not in skip_ids]
            stats["overlap"] += len(rows) - len(fresh)
            # A place can sit in two categories (e.g. cafe + restaurant): keep it only once
            fresh = [r for r in fresh if r["source_id"] not in seen_ids]
            # Most complete first: phone, then street address; keep Geoapify's distance order otherwise
            fresh.sort(key=lambda r: (r["phone"] is None, not r["_has_street"]))
            picked = fresh[:MAX_PER_GROUP]
            selected.extend(picked)
            seen_ids.update(r["source_id"] for r in picked)
            city_count += len(picked)
        log.info("%-10s %4d rows kept", city, city_count)

    for row in selected:
        row.pop("_has_street")
    path = write_raw_csv(selected, "geoapify_places.csv")
    log.info(
        "Found %d places, %d already in the OSM file; kept %d -> %s",
        stats["found"], stats["overlap"], len(selected), path,
    )


if __name__ == "__main__":
    main()
