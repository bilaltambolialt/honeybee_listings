"""GET /api/listings (filters, search, pagination) and the CSV export."""
import csv
import io

from conftest import listing


def seed(client):
    rows = [
        listing(business_name="Cafe Madras", city="Mumbai", address="King's Circle, Matunga"),
        listing(business_name="Toit Brewpub", city="Bengaluru", category="Restaurant", address="Indiranagar"),
        listing(business_name="Apollo Pharmacy", city="Chennai", category="Pharmacy", source="Geoapify", phone=None,
                address="Greams Road"),
        listing(business_name="Brew Room", city="Chennai", address="Mylapore"),
    ]
    client.post("/api/listings/bulk", json=rows)


def test_lists_all_sorted_by_name(client):
    seed(client)
    body = client.get("/api/listings").json()
    assert body["total"] == 4
    assert [item["business_name"] for item in body["items"]] == ["Apollo Pharmacy", "Brew Room", "Cafe Madras", "Toit Brewpub"]
    assert {"id", "address", "phone", "source", "created_at"} <= body["items"][0].keys()


def test_filters_combine(client):
    seed(client)
    body = client.get("/api/listings", params={"city": "Chennai", "category": "Cafe"}).json()
    assert body["total"] == 1
    assert body["items"][0]["business_name"] == "Brew Room"


def test_search_matches_name_or_address_case_insensitively(client):
    seed(client)
    names = lambda q: [i["business_name"] for i in client.get("/api/listings", params={"q": q}).json()["items"]]
    assert names("brew") == ["Brew Room", "Toit Brewpub"]
    assert names("matunga") == ["Cafe Madras"]


def test_pagination(client):
    seed(client)
    page2 = client.get("/api/listings", params={"page": 2, "page_size": 3}).json()
    assert page2["total"] == 4 and page2["page"] == 2
    assert [i["business_name"] for i in page2["items"]] == ["Toit Brewpub"]


def test_invalid_page_size_is_rejected(client):
    assert client.get("/api/listings", params={"page_size": 500}).status_code == 422


def test_export_csv_respects_filters(client):
    seed(client)
    response = client.get("/api/listings/export.csv", params={"city": "Chennai"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    rows = list(csv.DictReader(io.StringIO(response.text.lstrip("﻿"))))
    assert [r["business_name"] for r in rows] == ["Apollo Pharmacy", "Brew Room"]
    assert rows[0]["phone"] == ""  # missing phone exported as an empty cell
