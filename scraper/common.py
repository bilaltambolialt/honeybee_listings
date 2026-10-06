"""Settings and helpers shared by all collectors."""
import csv
import logging
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"

# Identify ourselves honestly to every service we call
USER_AGENT = "honeybee-listings-collector/1.0 (+https://github.com/bilaltambolialt/honeybee_listings)"

# Target cities with their centre point (lat, lon). Collectors search within a radius of each.
CITIES: dict[str, tuple[float, float]] = {
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Bengaluru": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
}

# Columns every collector writes, so the cleaning step can combine the files directly
RAW_COLUMNS = [
    "business_name", "category", "city", "address", "phone", "source",
    "source_id", "latitude", "longitude", "scraped_at",
]


_INDIC_SCRIPT = re.compile(r"[ऀ-෿]")  # Devanagari, Bengali, Tamil, Telugu, Kannada, ...


def prefer_english(name: str, english_name: str | None) -> str:
    """Use the English name when the main name is written in an Indian script and one exists."""
    if english_name and _INDIC_SCRIPT.search(name):
        return english_name
    return name


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    return logging.getLogger(name)


def write_raw_csv(rows: list[dict], filename: str) -> Path:
    """Write rows to data/raw/<filename> (UTF-8 with BOM so Excel shows Indian scripts correctly)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path
