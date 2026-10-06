"""Pydantic models: the shape of data entering and leaving the API."""
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
