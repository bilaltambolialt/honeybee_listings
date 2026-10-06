"""FastAPI application entry point.

Run from the backend/ folder:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import health, listings

settings = get_settings()

app = FastAPI(
    title="Business Listings API",
    description="Bulk-insert scraped business listings into MySQL and serve aggregated counts for the dashboard.",
    version="1.0.0",
)

# Allow the React dashboard (a different origin/port) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(listings.router)
