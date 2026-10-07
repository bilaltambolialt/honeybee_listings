"""Database engine and session handling (SQLAlchemy 2.x)."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # transparently replace connections MySQL has closed while idle
    pool_recycle=3600,
    # Encrypt the connection and verify the server's certificate when a CA file is configured
    connect_args={"ssl": {"ca": settings.mysql_ssl_ca}} if settings.mysql_ssl_ca else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for ORM models."""


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request, always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
