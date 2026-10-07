"""Load the clean dataset into MySQL through the FastAPI bulk-insert endpoint.

Reads data/clean/listings_clean.csv and POSTs it in batches to /api/listings/bulk.
The API validates and de-duplicates every row, so the loader is safe to run again:
already-stored listings are reported as "skipped", not inserted twice.

Needs the API running (cd backend; .\\venv\\Scripts\\python -m uvicorn app.main:app).
Run from the project root:
    scraper\\venv\\Scripts\\python scraper\\load_to_api.py [--api-url http://localhost:8000] [--batch-size 200]
"""
import argparse
import os
import sys
import time

import pandas as pd
import requests
from dotenv import load_dotenv

from common import ROOT_DIR, get_logger

CLEAN_PATH = ROOT_DIR / "data" / "clean" / "listings_clean.csv"
API_FIELDS = ["business_name", "category", "city", "address", "phone", "source"]

log = get_logger("loader")


def parse_args() -> argparse.Namespace:
    load_dotenv(ROOT_DIR / ".env")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--api-url", default=os.getenv("API_URL", "http://localhost:8000"))
    parser.add_argument("--batch-size", type=int, default=200, help="rows per request (API maximum: 1000)")
    return parser.parse_args()


def load_rows() -> list[dict]:
    df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", dtype=str)
    # Empty CSV cells become NaN; the API expects JSON null for missing address/phone
    return df[API_FIELDS].astype(object).where(df[API_FIELDS].notna(), None).to_dict(orient="records")


def check_api(api_url: str) -> None:
    try:
        resp = requests.get(f"{api_url}/health", timeout=10)
    except requests.ConnectionError:
        sys.exit(f"Cannot reach the API at {api_url}. Start it first (see the docstring).")
    if resp.status_code != 200:
        sys.exit(f"API is up but unhealthy: HTTP {resp.status_code} {resp.text}")


def post_batch(api_url: str, batch: list[dict]) -> dict:
    """POST one batch, retrying on network errors and 409 (concurrent insert) responses."""
    for attempt in range(1, 4):
        try:
            resp = requests.post(f"{api_url}/api/listings/bulk", json=batch, timeout=60)
        except requests.RequestException as exc:
            log.warning("Network error (attempt %d): %s", attempt, exc)
        else:
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 422:
                # Validation errors are data problems: retrying won't help, so show them and stop
                sys.exit(f"API rejected the batch (HTTP 422): {resp.json()['detail'][:3]}")
            log.warning("HTTP %s (attempt %d): %s", resp.status_code, attempt, resp.text[:200])
        time.sleep(2 * attempt)
    sys.exit("Giving up after 3 attempts")


def main() -> None:
    args = parse_args()
    check_api(args.api_url)
    rows = load_rows()
    log.info("Loading %d rows from %s in batches of %d", len(rows), CLEAN_PATH.name, args.batch_size)

    totals = {"received": 0, "inserted": 0, "skipped": 0}
    for start in range(0, len(rows), args.batch_size):
        batch = rows[start:start + args.batch_size]
        result = post_batch(args.api_url, batch)
        for key in totals:
            totals[key] += result[key]
        log.info("Rows %4d-%4d: inserted %3d, skipped %3d", start + 1, start + len(batch), result["inserted"], result["skipped"])

    log.info("Done: received %(received)d, inserted %(inserted)d, skipped %(skipped)d", totals)
    summary = requests.get(f"{args.api_url}/api/dashboard/summary", timeout=10).json()
    log.info("Database now holds %d listings", summary["total_listings"])


if __name__ == "__main__":
    main()
