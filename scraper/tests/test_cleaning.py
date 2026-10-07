"""Unit tests for the cleaning rules in clean_listings.py."""
import pandas as pd
import pytest

import clean_listings as cl
from common import prefer_english


@pytest.mark.parametrize(
    ("raw", "city", "expected"),
    [
        ("08130420037", "Delhi", "+91 81304 20037"),            # trunk 0 + mobile
        ("+91-09767642070", "Pune", "+91 97676 42070"),         # country code + trunk 0
        ("+91 011 2616 5060", "Delhi", "+91 11 2616 5060"),     # landline with both prefixes
        ("00918041205444", "Bengaluru", "+91 80 4120 5444"),    # 00 international prefix
        ("26165060", "Delhi", "+91 11 2616 5060"),              # local number gets area code
        ("+918022203333", "Bengaluru", "+91 80 2220 3333"),     # Bengaluru landline, not a mobile
        ("+919845012345", "Bengaluru", "+91 98450 12345"),      # Bengaluru mobile
        ("+91 70450 04488;+91 82918 16108", "Mumbai", "+91 70450 04488"),  # first of several
    ],
)
def test_phone_numbers_are_normalised(raw, city, expected):
    assert cl.normalise_phone(raw, city) == expected


@pytest.mark.parametrize("raw", ["1800 425 3800", "1.13E+42", "54789754754238", "2550283", None, ""])
def test_invalid_phone_numbers_become_empty(raw):
    # Toll-free lines, spreadsheet corruption, wrong digit counts: never guessed
    assert cl.normalise_phone(raw, "Mumbai") is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Axis Bank - BRAHMAND THANE", "Axis Bank - Brahmand Thane"),
        ("SATYA NARAYANA CAFE", "Satya Narayana Cafe"),
        ("BANK OF INDIA", "Bank of India"),
        ("OYO", "OYO"),                                  # single upper-case word = brand
        ("MW ENTERPRISES", "MW Enterprises"),            # vowel-less abbreviation kept
        ("Cafe Coffee Day", "Cafe Coffee Day"),          # mixed case left alone
    ],
)
def test_capitalisation_only_fixes_all_caps(raw, expected):
    assert cl.fix_caps(raw) == expected


def test_tidy_spaces():
    assert cl.tidy_spaces("  12,MG  Road ,  Pune ,, ") == "12, MG Road, Pune"


def test_prefer_english_only_replaces_indian_scripts():
    assert prefer_english("रिलायंस स्मार्ट", "Reliance Smart") == "Reliance Smart"
    assert prefer_english("Café Mondegar", "Cafe Mondegar") == "Café Mondegar"
    assert prefer_english("ராஜா சலூன்", None) == "ராஜா சலூன்"


def _rows(*names, **extra):
    base = {"category": "Cafe", "city": "Mumbai", "address": "1 MG Road", "phone": None,
            "source": "OpenStreetMap", "source_id": None, "latitude": None, "longitude": None}
    return pd.DataFrame([{**base, **extra, "business_name": n} for n in names])


def test_pipeline_removes_exact_duplicates_and_keeps_distinct_rows():
    clean, report = cl.run_pipeline(_rows("Cafe Madras", "CAFE  MADRAS", "Cafe Mysore"))
    assert sorted(clean["business_name"]) == ["Cafe Madras", "Cafe Mysore"]
    assert report[-2]["rows_before"] - report[-2]["rows_after"] == 1


def test_pipeline_drops_rows_outside_target_cities():
    clean, _ = cl.run_pipeline(_rows("Cafe A", city="Goa"))
    assert clean.empty


def test_cross_source_duplicate_keeps_most_complete_record():
    df = pd.concat([
        _rows("Cafe Madras", source="OpenStreetMap", latitude="19.0270", longitude="72.8550", phone="+91 22 2401 4419"),
        _rows("Cafe Madras", source="Geoapify", latitude="19.0271", longitude="72.8551", address="Matunga"),
    ], ignore_index=True)
    clean, _ = cl.run_pipeline(df)
    assert len(clean) == 1
    assert clean.iloc[0]["source"] == "OpenStreetMap"  # the one with a phone number
