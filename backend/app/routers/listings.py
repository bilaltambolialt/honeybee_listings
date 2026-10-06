"""Write endpoints for listings."""
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dedupe import compute_dedupe_key
from app.models import Listing
from app.schemas import BulkInsertResult, ListingIn

router = APIRouter(prefix="/api/listings", tags=["listings"])

MAX_BATCH_SIZE = 1000


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
