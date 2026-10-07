"""Pydantic models: the shape of data entering and leaving the API."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ListingIn(BaseModel):
    """One listing as sent by the loader. Whitespace is trimmed automatically."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "business_name": "Cafe Madras",
                "category": "Cafe",
                "city": "Mumbai",
                "address": "38-B, King's Circle, Matunga East",
                "phone": "+91 22 2401 4419",
                "source": "OpenStreetMap",
            }
        },
    )

    business_name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=32)
    source: str = Field(min_length=1, max_length=50)

    @field_validator("address", "phone", mode="after")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        # Store "no value" as NULL rather than an empty string, so NULL counts are meaningful
        return value or None


class BulkInsertResult(BaseModel):
    received: int = Field(description="Rows in the request")
    inserted: int = Field(description="New rows written to MySQL")
    skipped: int = Field(description="Duplicates (within the batch or already stored)")


class ListingOut(BaseModel):
    """One stored listing, as returned by GET /api/listings."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    business_name: str
    category: str
    city: str
    address: str | None
    phone: str | None
    source: str
    created_at: datetime


class ListingPage(BaseModel):
    """One page of listings plus what the client needs to paginate."""

    items: list[ListingOut]
    total: int = Field(description="Listings matching the filters (all pages)")
    page: int
    page_size: int


class CountItem(BaseModel):
    """One bar/slice in a dashboard chart."""

    label: str
    count: int


class DashboardSummary(BaseModel):
    """Headline numbers for the dashboard KPI cards."""

    total_listings: int
    cities: int = Field(description="Distinct cities")
    categories: int = Field(description="Distinct categories")
    sources: int = Field(description="Distinct data sources")
    with_phone: int = Field(description="Listings that have a phone number")
