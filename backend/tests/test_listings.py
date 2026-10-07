"""POST /api/listings/bulk: validation, insertion and de-duplication."""
from conftest import listing

URL = "/api/listings/bulk"


def test_inserts_new_listings(client):
    rows = [listing(business_name=f"Cafe {i}") for i in range(5)]
    response = client.post(URL, json=rows)
    assert response.status_code == 200
    assert response.json() == {"received": 5, "inserted": 5, "skipped": 0}


def test_rerun_skips_everything(client):
    rows = [listing(business_name=f"Cafe {i}") for i in range(5)]
    client.post(URL, json=rows)
    assert client.post(URL, json=rows).json() == {"received": 5, "inserted": 0, "skipped": 5}


def test_duplicates_within_one_batch_are_skipped(client):
    response = client.post(URL, json=[listing(), listing()])
    assert response.json() == {"received": 2, "inserted": 1, "skipped": 1}


def test_case_and_spacing_variants_count_as_duplicates(client):
    client.post(URL, json=[listing()])
    variant = listing(business_name="  CAFE   madras ", city="mumbai")
    assert client.post(URL, json=[variant]).json()["skipped"] == 1


def test_same_business_from_another_source_is_kept(client):
    client.post(URL, json=[listing()])
    assert client.post(URL, json=[listing(source="Geoapify")]).json()["inserted"] == 1


def test_blank_phone_and_address_are_stored_as_null(client):
    client.post(URL, json=[listing(phone="", address="   ")])
    summary = client.get("/api/dashboard/summary").json()
    assert summary["with_phone"] == 0


def test_missing_required_field_is_rejected(client):
    response = client.post(URL, json=[listing(business_name="")])
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", 0, "business_name"]


def test_empty_list_is_rejected(client):
    assert client.post(URL, json=[]).status_code == 422


def test_batch_larger_than_limit_is_rejected(client):
    rows = [listing(business_name=f"Shop {i}") for i in range(1001)]
    assert client.post(URL, json=rows).status_code == 422
