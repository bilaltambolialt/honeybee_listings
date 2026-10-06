"""Duplicate detection: a stable fingerprint for each listing."""
import hashlib
import re

from app.schemas import ListingIn

_WHITESPACE = re.compile(r"\s+")


def _normalise(value: str | None) -> str:
    # "  Cafe   MADRAS " and "cafe madras" must produce the same key
    return _WHITESPACE.sub(" ", value or "").strip().casefold()


def compute_dedupe_key(listing: ListingIn) -> str:
    """sha256 hex (64 chars) of normalised name|address|city|source."""
    parts = (listing.business_name, listing.address, listing.city, listing.source)
    raw = "|".join(_normalise(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
