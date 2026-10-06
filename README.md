# Business Listings Dashboard

An end-to-end data pipeline: business listings are collected from multiple open sources, cleaned and de-duplicated, loaded into **MySQL** through a **FastAPI** bulk-insert API, and visualised in a **React + Recharts** dashboard.

> 🚧 Work in progress. Full setup instructions, architecture diagram, screenshots and challenges will be added as the project is completed.

## Tech stack
| Layer | Technology |
|-------|------------|
| Data collection | Python, requests, BeautifulSoup, pandas |
| Database | MySQL 8+ (developed on 9.7) |
| Backend | FastAPI, SQLAlchemy 2.x, PyMySQL, Pydantic v2 |
| Frontend | React (Vite), Recharts |

## Repository layout
```
backend/     FastAPI application (insert + dashboard APIs)
frontend/    React dashboard (Vite + Recharts)
scraper/     Data collection scripts, one per source
data/raw/    Raw scraped CSVs
data/clean/  Cleaned, de-duplicated dataset (listings_clean.csv)
notebooks/   Cleaning steps + exploratory data analysis
database/    Schema and MySQL dump of listing_master
docs/        Plan, decisions, progress log
```
