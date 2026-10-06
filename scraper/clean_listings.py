"""Combine the raw collector outputs into one clean, de-duplicated dataset.

Input:  data/raw/*.csv           (one file per source, common columns)
Output: data/clean/listings_clean.csv

Each cleaning step is a small function that returns the cleaned DataFrame and a short
note of what it changed; notebooks/cleaning_eda.ipynb walks through the same steps.

Run from the project root:
    scraper\\venv\\Scripts\\python scraper\\clean_listings.py
"""
import re
from math import asin, cos, radians, sin, sqrt

import pandas as pd

from common import CITIES, RAW_DIR, ROOT_DIR, get_logger

CLEAN_PATH = ROOT_DIR / "data" / "clean" / "listings_clean.csv"
OUTPUT_COLUMNS = ["business_name", "category", "city", "address", "phone", "source", "source_id"]
REQUIRED = ["business_name", "category", "city", "source"]
TEXT_COLUMNS = ["business_name", "category", "city", "address", "phone", "source"]

# Two-digit STD (area) codes of our cities, used to format landlines
CITY_STD_CODE = {"Mumbai": "22", "Delhi": "11", "Bengaluru": "80", "Chennai": "44", "Hyderabad": "40", "Pune": "20"}
# Lowercase when not the first word in a title-cased name
SMALL_WORDS = {"of", "and", "the", "in", "at", "for", "on", "by", "to"}
# Two listings closer than this (with the same name and city) are the same place
SAME_PLACE_METRES = 150

log = get_logger("clean")


# ---------------------------------------------------------------- loading
def load_raw() -> pd.DataFrame:
    files = sorted(RAW_DIR.glob("*.csv"))
    frames = [pd.read_csv(f, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[""]) for f in files]
    log.info("Loaded %s", ", ".join(f"{f.name} ({len(df)})" for f, df in zip(files, frames)))
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------- text helpers
def tidy_spaces(value):
    """Collapse runs of whitespace, remove space before commas, ensure one space after."""
    if not isinstance(value, str):
        return value
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+,", ",", value)
    value = re.sub(r",(?=\S)", ", ", value)
    value = re.sub(r"(,\s*){2,}", ", ", value)
    return value.strip(" ,") or None


def smart_title(text: str) -> str:
    """Title-case ALL-CAPS text: 'ADARSH NAGAR-HYDERABAD' -> 'Adarsh Nagar-Hyderabad'.

    Letter groups without vowels (MW, GR, FLR, SBI-style codes) are abbreviations and stay upper case.
    """
    def fix_word(match: re.Match) -> str:
        word = match.group(0)
        if not re.search(r"[AEIOUY]", word.upper()):
            return word.upper()
        return word.lower() if word.lower() in SMALL_WORDS else word.capitalize()

    titled = re.sub(r"[A-Za-z]+(?:'[A-Za-z]+)?", fix_word, text)
    return titled[0].upper() + titled[1:] if titled else titled


def fix_caps(value):
    """Title-case a value (or each ' - ' part of it) only when it is entirely upper case.

    A name that starts with a single upper-case word keeps it: usually a brand or acronym
    (OYO, VLCC, KFC). Later parts, such as RBI branch names after " - ", are always converted.
    """
    if not isinstance(value, str):
        return value
    parts = value.split(" - ")
    fixed = [
        smart_title(p) if p.isupper() and (i > 0 or " " in p.strip()) else p
        for i, p in enumerate(parts)
    ]
    return " - ".join(fixed)


# ---------------------------------------------------------------- phone helpers
def normalise_phone(value, city: str):
    """Return one phone number in '+91 ...' format, or None if it can't be a valid Indian number.

    Keeps the first number when several are listed. Mobile: +91 98765 43210.
    Landline in one of our cities: +91 22 2401 4419.
    """
    if not isinstance(value, str):
        return None
    first = re.split(r"[;,/]", value)[0]
    digits = re.sub(r"\D", "", first)
    # Strip prefixes in dialling order; numbers often mix them, e.g. "+91 011 2616 5060"
    if digits.startswith("00"):
        digits = digits[2:]                    # 00 international prefix
    if len(digits) >= 12 and digits.startswith("91"):
        digits = digits[2:]                    # 91 country code
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]                    # 0 trunk prefix
    if len(digits) == 8 and city in CITY_STD_CODE:
        digits = CITY_STD_CODE[city] + digits  # local landline written without area code
    if len(digits) != 10:
        return None
    std = CITY_STD_CODE.get(city)
    # Bengaluru's area code 80 looks like a mobile prefix; its landlines continue with 2-4
    is_bengaluru_landline = city == "Bengaluru" and digits.startswith("80") and digits[2] in "234"
    if digits[0] in "6789" and not is_bengaluru_landline:
        return f"+91 {digits[:5]} {digits[5:]}"
    if std and digits.startswith(std):
        return f"+91 {std} {digits[2:6]} {digits[6:]}"
    return f"+91 {digits[:3]} {digits[3:6]} {digits[6:]}"


# ---------------------------------------------------------------- cleaning steps
def step_tidy_whitespace(df):
    before = df[TEXT_COLUMNS].copy()
    df = df.assign(**{c: df[c].map(tidy_spaces) for c in TEXT_COLUMNS})
    changed = int((before.fillna("") != df[TEXT_COLUMNS].fillna("")).any(axis=1).sum())
    return df, f"{changed} rows had extra/missing spaces or stray commas fixed"


def step_fix_capitals(df):
    names = df["business_name"].map(fix_caps)
    addresses = df["address"].map(fix_caps)
    n_names = int((names != df["business_name"]).sum())
    n_addr = int((addresses.fillna("") != df["address"].fillna("")).sum())
    return df.assign(business_name=names, address=addresses), f"{n_names} names and {n_addr} addresses converted from ALL CAPS"


def step_trim_address_country(df):
    trimmed = df["address"].str.replace(r",\s*India$", "", regex=True)
    n = int((trimmed.fillna("") != df["address"].fillna("")).sum())
    return df.assign(address=trimmed), f"{n} addresses had the redundant ', India' suffix removed"


def step_normalise_phones(df):
    had_phone = df["phone"].notna()
    multi = int(df["phone"].str.contains(r"[;,/]", na=False).sum())
    phones = [normalise_phone(p, c) for p, c in zip(df["phone"], df["city"])]
    df = df.assign(phone=phones)
    invalid = int((had_phone & df["phone"].isna()).sum())
    return df, f"{int(had_phone.sum())} phones put in one +91 format ({multi} had several numbers, first kept); {invalid} invalid numbers set to empty"


def step_drop_missing_required(df):
    mask = df[REQUIRED].notna().all(axis=1)
    return df[mask].copy(), f"{int((~mask).sum())} rows dropped for a missing name, category, city or source"


def step_validate_values(df):
    valid_city = df["city"].isin(CITIES)
    n_bad = int((~valid_city).sum())
    return df[valid_city].copy(), f"{n_bad} rows dropped with a city outside the 6 target cities"


def _key(name, address, city, source):
    # Same normalisation as the API's dedupe key (backend/app/dedupe.py)
    norm = lambda v: re.sub(r"\s+", " ", v if isinstance(v, str) else "").strip().casefold()
    return "|".join(norm(v) for v in (name, address, city, source))


def step_drop_exact_duplicates(df):
    keys = [_key(*r) for r in df[["business_name", "address", "city", "source"]].itertuples(index=False)]
    dup = pd.Series(keys, index=df.index).duplicated()
    return df[~dup].copy(), f"{int(dup.sum())} exact duplicates removed (same name, address, city and source)"


def _distance_m(lat1, lon1, lat2, lon2) -> float:
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_000 * asin(sqrt(a))


def step_drop_cross_source_duplicates(df):
    """Same business listed by two sources: same name + city and within SAME_PLACE_METRES.

    Keeps the more complete record (has phone, then has address).
    """
    df = df.assign(
        _name=df["business_name"].str.casefold().str.replace(r"[^\w]", "", regex=True),
        _lat=pd.to_numeric(df["latitude"], errors="coerce"),
        _lon=pd.to_numeric(df["longitude"], errors="coerce"),
        _score=df["phone"].notna().astype(int) * 2 + df["address"].notna().astype(int),
    )
    drop = set()
    for _, group in df[df["_lat"].notna()].groupby(["_name", "city"]):
        if group["source"].nunique() < 2:
            continue
        rows = group.sort_values("_score", ascending=False)
        kept = []
        for idx, r in rows.iterrows():
            if any(_distance_m(r._lat, r._lon, k._lat, k._lon) <= SAME_PLACE_METRES and r.source != k.source for k in kept):
                drop.add(idx)
            else:
                kept.append(r)
    df = df.drop(index=list(drop)).drop(columns=["_name", "_lat", "_lon", "_score"])
    return df, f"{len(drop)} cross-source duplicates removed (same name and city, within {SAME_PLACE_METRES} m)"


STEPS = [
    ("Tidy whitespace", step_tidy_whitespace),
    ("Fix ALL-CAPS text", step_fix_capitals),
    ("Trim ', India'", step_trim_address_country),
    ("Normalise phones", step_normalise_phones),
    ("Drop rows missing required fields", step_drop_missing_required),
    ("Validate cities", step_validate_values),
    ("Remove exact duplicates", step_drop_exact_duplicates),
    ("Remove cross-source duplicates", step_drop_cross_source_duplicates),
]


def run_pipeline(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Apply every step in order; return the clean data and a per-step report."""
    report = []
    for name, step in STEPS:
        rows_before = len(df)
        df, note = step(df)
        report.append({"step": name, "rows_before": rows_before, "rows_after": len(df), "note": note})
    df = df.sort_values(["source", "city", "category", "business_name"]).reset_index(drop=True)
    return df, report


def save(df: pd.DataFrame) -> None:
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df[OUTPUT_COLUMNS].to_csv(CLEAN_PATH, index=False, encoding="utf-8-sig")


def main() -> None:
    raw = load_raw()
    clean, report = run_pipeline(raw)
    for r in report:
        log.info("%-34s %4d -> %4d  %s", r["step"], r["rows_before"], r["rows_after"], r["note"])
    save(clean)
    log.info("Saved %d clean rows -> %s", len(clean), CLEAN_PATH)
    log.info("Per source: %s", clean["source"].value_counts().to_dict())


if __name__ == "__main__":
    main()
