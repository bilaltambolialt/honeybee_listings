"""Test fixtures: each test gets a fresh in-memory SQLite database instead of MySQL."""
import os

# Settings require a DB password; tests never connect to MySQL, so any value works
os.environ.setdefault("MYSQL_PASSWORD", "test-only")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  (registers the listing_master table on Base)
from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    # StaticPool keeps one connection, so the in-memory database survives across requests
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def listing(**overrides):
    """A valid listing payload; override any field per test."""
    data = {
        "business_name": "Cafe Madras",
        "category": "Cafe",
        "city": "Mumbai",
        "address": "38-B King's Circle, Matunga East",
        "phone": "+91 22 2401 4419",
        "source": "OpenStreetMap",
    }
    data.update(overrides)
    return data
