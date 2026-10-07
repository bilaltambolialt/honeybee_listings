"""Collector 1: business listings from OpenStreetMap via the Overpass API.

Data: (c) OpenStreetMap contributors, licensed under ODbL (https://www.openstreetmap.org/copyright).
Fair use: the public Overpass instance allows ~10,000 requests/day; this script sends one
request per city (6 in total) with a 15-second pause between them.

Run from the project root:
    scraper\\venv\\Scripts\\python scraper\\osm_overpass.py
"""
import time
from collections import defaultdict
from datetime import datetime, timezone

import requests

from common import CITIES, USER_AGENT, get_logger, prefer_english, write_raw_csv

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",  # official mirror, used if the main one is busy
]
RADIUS_M = 10_000          # search 10 km around each city centre
PAUSE_BETWEEN_CITIES = 15  # seconds; avoids HTTP 429 "too many requests" from the free public service
MAX_PER_GROUP = 6          # keep at most N listings per (city, category) so no category dominates

# OSM tag -> our category name
CATEGORY_TAGS: dict[tuple[str, str], str] = {
    ("amenity", "cafe"): "Cafe",
    ("amenity", "restaurant"): "Restaurant",
    ("amenity", "pharmacy"): "Pharmacy",
    ("amenity", "hospital"): "Hospital",
    ("amenity", "clinic"): "Clinic",
    ("amenity", "dentist"): "Dentist",
    ("amenity", "bank"): "Bank",
    ("shop", "supermarket"): "Supermarket",
    ("shop", "bakery"): "Bakery",
    ("shop", "electronics"): "Electronics Store",
    ("shop", "hairdresser"): "Salon",
    ("shop", "beauty"): "Salon",
    ("leisure", "fitness_centre"): "Gym",
    ("tourism", "hotel"): "Hotel",
}

log = get_logger("osm")


def build_query(lat: float, lon: float) -> str:
    """One Overpass query per city: every wanted tag, named places only."""
    values_by_key: dict[str, list[str]] = defaultdict(list)
    for key, value in CATEGORY_TAGS:
        values_by_key[key].append(value)
    clauses = "\n".join(
        f'  nwr["{key}"~"^({"|".join(values)})$"]["name"](around:{RADIUS_M},{lat},{lon});'
        for key, values in values_by_key.items()
    )
    # "out center" gives a single point for buildings (ways) as well as nodes
    return f"[out:json][timeout:120];\n(\n{clauses}\n);\nout center tags;"


def fetch(query: str) -> list[dict]:
    """POST the query, retrying on busy servers and falling back to the mirror."""
    for endpoint in ENDPOINTS:
        for attempt in range(1, 4):
            try:
                resp = requests.post(endpoint, data={"data": query}, headers={"User-Agent": USER_AGENT}, timeout=180)
                if resp.status_code == 200:
                    return resp.json()["elements"]
                log.warning("%s returned HTTP %s (attempt %d)", endpoint, resp.status_code, attempt)
            except requests.RequestException as exc:
                log.warning("%s failed: %s (attempt %d)", endpoint, exc, attempt)
            time.sleep(10 * attempt)  # back off: 10 s, 20 s, 30 s
    raise RuntimeError("All Overpass endpoints failed")


def category_of(tags: dict) -> str | None:
    for (key, value), category in CATEGORY_TAGS.items():
        if tags.get(key) == value:
            return category
    return None


def address_of(tags: dict) -> str | None:
    if tags.get("addr:full"):
        return tags["addr:full"]
    parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb") or tags.get("addr:neighbourhood"),
        tags.get("addr:postcode"),
    ]
    return ", ".join(p for p in parts if p) or None


def to_row(element: dict, city: str, scraped_at: str) -> dict | None:
    tags = element.get("tags", {})
    category = category_of(tags)
    if not category:
        return None
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    return {
        "business_name": prefer_english(tags["name"], tags.get("name:en")),
        "category": category,
        "city": city,
        "address": address_of(tags),
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "source": "OpenStreetMap",
        "source_id": f"{element['type']}/{element['id']}",
        "latitude": lat,
        "longitude": lon,
        "scraped_at": scraped_at,
    }


def select_balanced(rows: list[dict]) -> list[dict]:
    """Keep up to MAX_PER_GROUP per (city, category), preferring the most complete records."""
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["city"], row["category"])].append(row)
    selected = []
    for group in groups.values():
        # Rows with an address and phone first; source_id as a stable tie-break
        group.sort(key=lambda r: (r["address"] is None, r["phone"] is None, r["source_id"]))
        selected.extend(group[:MAX_PER_GROUP])
    return selected


def main() -> None:
    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    all_rows: list[dict] = []
    for i, (city, (lat, lon)) in enumerate(CITIES.items()):
        if i:
            time.sleep(PAUSE_BETWEEN_CITIES)
        elements = fetch(build_query(lat, lon))
        rows = [r for e in elements if (r := to_row(e, city, scraped_at))]
        log.info("%-10s %5d places found", city, len(rows))
        all_rows.extend(rows)

    selected = select_balanced(all_rows)
    path = write_raw_csv(selected, "osm_overpass.csv")
    log.info("Found %d places in total; kept %d balanced rows -> %s", len(all_rows), len(selected), path)


if __name__ == "__main__":
    main()
