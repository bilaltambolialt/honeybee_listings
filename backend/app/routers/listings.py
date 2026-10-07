"""Read and write endpoints for listings."""
import csv
import io
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, insert, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dedupe import compute_dedupe_key
from app.models import Listing
from app.schemas import BulkInsertResult, ListingIn, ListingPage

router = APIRouter(prefix="/api/listings", tags=["listings"])

MAX_BATCH_SIZE = 1000
EXPORT_COLUMNS = ["business_name", "category", "city", "address", "phone", "source"]


class ListingFilters:
    """Optional filters shared by the list and export endpoints (all combined with AND)."""

    def __init__(
        self,
        city: str | None = None,
        category: str | None = None,
        source: str | None = None,
        q: Annotated[str | None, Query(max_length=100, description="Search in name and address")] = None,
    ):
        self.city, self.category, self.source = city, category, source
        self.q = q.strip() if q else None

    def apply(self, stmt):
        for column, value in ((Listing.city, self.city), (Listing.category, self.category), (Listing.source, self.source)):
            if value:
                stmt = stmt.where(column == value)
        if self.q:
            # MySQL's utf8mb4_unicode_ci collation makes LIKE case-insensitive
            pattern = f"%{self.q}%"
            stmt = stmt.where(or_(Listing.business_name.like(pattern), Listing.address.like(pattern)))
        return stmt


@router.get("", response_model=ListingPage, summary="Browse listings with filters, search and pagination")
def list_listings(
    filters: Annotated[ListingFilters, Depends()],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    db: Session = Depends(get_db),
) -> ListingPage:
    total = db.scalar(filters.apply(select(func.count()).select_from(Listing)))
    rows = db.scalars(
        filters.apply(select(Listing))
        .order_by(Listing.business_name, Listing.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ListingPage(items=rows, total=total, page=page, page_size=page_size)


@router.get(
    "/export.csv",
    summary="Download the (filtered) listings as CSV",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/csv": {}}}},
)
def export_listings(filters: Annotated[ListingFilters, Depends()], db: Session = Depends(get_db)):
    rows = db.execute(filters.apply(select(*[getattr(Listing, c) for c in EXPORT_COLUMNS])).order_by(Listing.business_name, Listing.id))
    buffer = io.StringIO()
    buffer.write("﻿")  # byte-order mark so Excel opens names in Indian scripts correctly
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(EXPORT_COLUMNS)
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="listings.csv"'},
    )


@router.post(
    "/bulk",
    response_model=BulkInsertResult,
    summary="Bulk insert listings (duplicates are skipped)",
)
def bulk_insert(
    listings: Annotated[list[ListingIn], Body(min_length=1, max_length=MAX_BATCH_SIZE)],
    db: Session = Depends(get_db),
) -> BulkInsertResult:
    # 1. Fingerprint every row; a dict keeps only the first occurrence of each key
    unique_rows: dict[str, ListingIn] = {}
    for listing in listings:
        unique_rows.setdefault(compute_dedupe_key(listing), listing)

    # 2. Drop rows whose fingerprint is already stored (one indexed lookup for the whole batch)
    existing = set(
        db.scalars(select(Listing.dedupe_key).where(Listing.dedupe_key.in_(unique_rows.keys())))
    )
    new_rows = [
        {**listing.model_dump(), "dedupe_key": key}
        for key, listing in unique_rows.items()
        if key not in existing
    ]

    # 3. Insert all new rows in one transaction: the whole batch is saved, or none of it.
    #    (The SELECT above already opened the transaction; commit ends it.)
    if new_rows:
        try:
            db.execute(insert(Listing), new_rows)
            db.commit()
        except IntegrityError:
            db.rollback()
            # Another request inserted one of these rows between steps 2 and 3
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A concurrent insert created duplicates; retry this batch.",
            )

    return BulkInsertResult(
        received=len(listings),
        inserted=len(new_rows),
        skipped=len(listings) - len(new_rows),
    )
