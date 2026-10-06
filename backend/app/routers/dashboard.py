"""Read-only aggregate endpoints that feed the dashboard charts."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.database import get_db
from app.models import Listing
from app.schemas import CountItem, DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _count_by(db: Session, column: InstrumentedAttribute) -> list[CountItem]:
    """SELECT <column>, COUNT(*) ... GROUP BY <column>, largest first (ties alphabetical)."""
    total = func.count().label("total")
    rows = db.execute(
        select(column, total).group_by(column).order_by(total.desc(), column)
    ).all()
    return [CountItem(label=label, count=count) for label, count in rows]


@router.get("/summary", response_model=DashboardSummary, summary="Headline totals for KPI cards")
def summary(db: Session = Depends(get_db)) -> DashboardSummary:
    # One query: COUNT(phone) counts only non-NULL phones
    row = db.execute(
        select(
            func.count(),
            func.count(Listing.city.distinct()),
            func.count(Listing.category.distinct()),
            func.count(Listing.source.distinct()),
            func.count(Listing.phone),
        )
    ).one()
    return DashboardSummary(
        total_listings=row[0], cities=row[1], categories=row[2], sources=row[3], with_phone=row[4]
    )


@router.get("/cities", response_model=list[CountItem], summary="Listing count per city")
def cities(db: Session = Depends(get_db)) -> list[CountItem]:
    return _count_by(db, Listing.city)


@router.get("/categories", response_model=list[CountItem], summary="Listing count per category")
def categories(db: Session = Depends(get_db)) -> list[CountItem]:
    return _count_by(db, Listing.category)


@router.get("/sources", response_model=list[CountItem], summary="Listing count per source")
def sources(db: Session = Depends(get_db)) -> list[CountItem]:
    return _count_by(db, Listing.source)
