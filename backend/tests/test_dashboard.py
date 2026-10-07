"""Dashboard aggregate endpoints and the health check."""
from conftest import listing


def seed(client):
    rows = (
        [listing(business_name=f"Mumbai cafe {i}", city="Mumbai") for i in range(3)]
        + [listing(business_name=f"Pune gym {i}", city="Pune", category="Gym", source="Geoapify") for i in range(2)]
        + [listing(business_name="Delhi gym", city="Delhi", category="Gym", source="Geoapify", phone=None)]
    )
    assert client.post("/api/listings/bulk", json=rows).json()["inserted"] == 6


def test_city_counts_sorted_by_count(client):
    seed(client)
    assert client.get("/api/dashboard/cities").json() == [
        {"label": "Mumbai", "count": 3},
        {"label": "Pune", "count": 2},
        {"label": "Delhi", "count": 1},
    ]


def test_ties_are_broken_alphabetically(client):
    seed(client)
    # Cafe and Gym both have 3 listings
    assert [row["label"] for row in client.get("/api/dashboard/categories").json()] == ["Cafe", "Gym"]


def test_source_counts(client):
    seed(client)
    assert client.get("/api/dashboard/sources").json() == [
        {"label": "Geoapify", "count": 3},
        {"label": "OpenStreetMap", "count": 3},
    ]


def test_summary(client):
    seed(client)
    assert client.get("/api/dashboard/summary").json() == {
        "total_listings": 6,
        "cities": 3,
        "categories": 2,
        "sources": 2,
        "with_phone": 5,
    }


def test_empty_database_returns_zeros_and_empty_lists(client):
    assert client.get("/api/dashboard/summary").json()["total_listings"] == 0
    assert client.get("/api/dashboard/cities").json() == []


def test_health_reports_database_connected(client):
    assert client.get("/health").json() == {"status": "ok", "database": "connected"}
