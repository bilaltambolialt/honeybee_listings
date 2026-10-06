# Project roadmap

Each step ends with a verifiable acceptance check and its own commit.

| # | Step | Acceptance check |
|---|------|------------------|
| 0 | Environment check: git, Python, Node/npm, MySQL server | All tools report versions; app DB user can log in |
| 1 | Repository scaffold, `.gitignore`, `.env.example`, docs | Folder tree exists, first commit |
| 2 | MySQL schema: `database/schema.sql` | `DESCRIBE listing_master;` shows all columns and indexes |
| 3 | Backend skeleton: config, DB connection, `/health` | `/health` and `/docs` respond |
| 4 | Bulk insert API with de-duplication | Sample rows stored; re-run skips duplicates |
| 5 | Dashboard APIs (cities, categories, sources, summary) | JSON matches SQL `GROUP BY` results |
| 6 | Source review + collector 1 (OpenStreetMap Overpass) | 150+ raw rows in `data/raw/` |
| 7 | Collector 2 (Geoapify Places API) | 150+ raw rows |
| 8 | Collector 3 (third permitted source) | 150+ raw rows |
| 9 | Cleaning script + notebook → `listings_clean.csv` | 500+ clean rows, 100+ per source |
| 10 | Loader: POST clean CSV in batches to the API | MySQL row count matches CSV |
| 11 | Frontend scaffold (Vite + React) fetching from the API | Live numbers render in the browser |
| 12 | Charts, KPI cards, loading/error states, styling | Clean on desktop and mobile widths |
| 13 | README, `mysqldump`, tests, tidy-up | Fresh-clone setup works |
| 14 | Deployment (optional) | Live URL works |
| 15 | Demo video + submission | Checklist complete |

Before any data collection (steps 6-8), each source's robots.txt, terms of use and rate limits are reviewed and documented.
