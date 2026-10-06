"""Collector 3: bank branch listings from the Reserve Bank of India (RBI) directory.

Source: RBI NEFT/RTGS branch lists, as compiled and published by Razorpay under the MIT
licence (https://github.com/razorpay/ifsc). Independent of OpenStreetMap.

The full file (~36 MB, every bank branch in India) is downloaded once into data/cache/
(git-ignored); only the selected sample is written to data/raw/.

Run from the project root:
    scraper\\venv\\Scripts\\python scraper\\rbi_bank_branches.py
"""
import re
from datetime import datetime, timezone
from itertools import zip_longest

import pandas as pd
import requests

from common import CITIES, ROOT_DIR, USER_AGENT, get_logger, write_raw_csv

DATASET_URL = "https://github.com/razorpay/ifsc/releases/download/v2.0.62/IFSC.csv"
CACHE_PATH = ROOT_DIR / "data" / "cache" / "IFSC.csv"
PER_CITY = 25  # 6 cities x 25 = 150 rows
# Small co-operative banks register IFSC codes through a sponsor bank's office (often in
# Mumbai), so they appear in cities where they have no real branch. Requiring a minimum
# number of branches in the city keeps only banks with a genuine local presence.
MIN_BRANCHES_IN_CITY = 15

# Exact RBI spellings (capitals, old and new names) accepted for each city. A loose
# match would wrongly include separate places such as NAVI MUMBAI or BANGALORE RURAL.
CITY_NAMES: dict[str, set[str]] = {
    "Mumbai": {"MUMBAI", "GREATER MUMBAI", "MUMBAI SUBURBAN", "BRIHAN MUMBAI"},
    "Delhi": {"DELHI", "NEW DELHI", "CENTRAL DELHI", "NORTH DELHI", "SOUTH DELHI", "EAST DELHI",
              "WEST DELHI", "NORTH WEST DELHI", "NORTH EAST DELHI", "SOUTH WEST DELHI"},
    "Bengaluru": {"BANGALORE", "BANGALORE URBAN", "BENGALURU", "BENGALURU URBAN"},
    "Chennai": {"CHENNAI", "CHENNAI ( MADRAS )"},
    "Hyderabad": {"HYDERABAD", "HYDERABAD URBAN"},
    "Pune": {"PUNE"},
}

# Address check: PIN code prefix and names (old and new) that confirm each city
CITY_PIN_PREFIX = {"Mumbai": "400", "Delhi": "110", "Bengaluru": "560", "Chennai": "600", "Hyderabad": "500", "Pune": "411"}
CITY_ADDRESS_NAMES = {
    "Mumbai": ("MUMBAI", "BOMBAY"),
    "Delhi": ("DELHI",),
    "Bengaluru": ("BANGALORE", "BENGALURU"),
    "Chennai": ("CHENNAI", "MADRAS"),
    "Hyderabad": ("HYDERABAD", "SECUNDERABAD"),
    "Pune": ("PUNE", "POONA"),
}
PIN_RE = re.compile(r"\b(\d{3})\s?\d{3}\b")
# A number listed for more than this many branches nationwide is a helpline, not a branch phone
MAX_BRANCHES_PER_PHONE = 5

log = get_logger("rbi")


def address_matches_city(address: str, city: str) -> bool:
    """If the address has a PIN code it must belong to the city; otherwise it must name the city."""
    address = address.upper()
    pins = PIN_RE.findall(address)
    if pins:
        return any(prefix == CITY_PIN_PREFIX[city] for prefix in pins)
    return any(name in address for name in CITY_ADDRESS_NAMES[city])


def download_if_missing() -> None:
    if CACHE_PATH.exists():
        log.info("Using cached file %s", CACHE_PATH)
        return
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    log.info("Downloading %s (~36 MB, one request)", DATASET_URL)
    with requests.get(DATASET_URL, headers={"User-Agent": USER_AGENT}, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        tmp = CACHE_PATH.with_suffix(".part")
        with tmp.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
        tmp.rename(CACHE_PATH)


def looks_like_phone(value) -> bool:
    # RBI uses placeholders such as "0" or "NA" when there is no number
    if not isinstance(value, str):
        return False
    digits = re.sub(r"\D", "", value)
    # 1800 numbers are national toll-free helplines, not branch phones
    is_toll_free = digits.removeprefix("91").removeprefix("0").startswith("1800")
    return len(digits) >= 6 and not is_toll_free


def pick_branches(city_df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Round-robin across banks so the sample isn't dominated by the largest bank."""
    # Within each bank: branches with a phone first, then by IFSC for a stable result
    city_df = city_df.sort_values(["_phone", "IFSC"], ascending=[False, True])
    queues = [group.index.tolist() for _, group in city_df.groupby("BANK", sort=True)]
    order = [idx for row in zip_longest(*queues) for idx in row if idx is not None]
    return city_df.loc[order[:n]]


def main() -> None:
    download_if_missing()
    df = pd.read_csv(CACHE_PATH, dtype=str)
    log.info("Loaded %d bank branches", len(df))
    phone_use = df["CONTACT"].value_counts()
    helplines = set(phone_use[phone_use > MAX_BRANCHES_PER_PHONE].index)
    df["_phone"] = df["CONTACT"].map(lambda v: looks_like_phone(v) and v not in helplines)
    log.info("Ignoring %d shared helpline numbers", len(helplines))
    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    rows: list[dict] = []
    for city in CITIES:
        in_city = df["CITY"].str.strip().isin(CITY_NAMES[city])
        city_df = df[in_city & df["ADDRESS"].notna()]
        city_df = city_df[city_df["ADDRESS"].map(lambda a: address_matches_city(a, city))]
        branch_counts = city_df["BANK"].value_counts()
        local_banks = branch_counts[branch_counts >= MIN_BRANCHES_IN_CITY].index
        city_df = city_df[city_df["BANK"].isin(local_banks)]
        picked = pick_branches(city_df, PER_CITY)
        log.info("%-10s %5d branches of %3d local banks; kept %d", city, len(city_df), len(local_banks), len(picked))
        for _, r in picked.iterrows():
            rows.append({
                "business_name": f"{r['BANK']} - {r['BRANCH']}",
                "category": "Bank",
                "city": city,
                "address": r["ADDRESS"],
                "phone": r["CONTACT"] if r["_phone"] else None,
                "source": "RBI Bank Directory",
                "source_id": r["IFSC"],
                "latitude": None,
                "longitude": None,
                "scraped_at": scraped_at,
            })

    path = write_raw_csv(rows, "rbi_bank_branches.csv")
    log.info("Kept %d rows -> %s", len(rows), path)


if __name__ == "__main__":
    main()
