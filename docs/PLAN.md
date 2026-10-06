# Step-by-step plan (do ONE step per turn; stop and wait after each)

| # | Step | Done when |
|---|------|-----------|
| 0 | Tool check: git, Python, Node/npm, MySQL server running. Install Python/Node if missing | I paste version outputs, all OK |
| 1 | Repo scaffold, git init, .gitignore, .env.example, docs in place | folder tree exists, first commit |
| 2 | MySQL (Workbench already installed): create database + app user, write `database/schema.sql`, run it in Workbench | `DESCRIBE listing_master;` works |
| 3 | Backend skeleton: venv, requirements, config, DB connection, `/health` | `/health` and `/docs` open |
| 4 | Bulk insert API (+ dedupe) tested with 5 sample rows | rows visible in MySQL, rerun skips dupes |
| 5 | Dashboard APIs (cities, categories, sources, summary) | JSON correct vs SQL GROUP BY |
| 6 | Source check + Scraper 1 (OSM Overpass) | 150+ raw rows in `data/raw/` |
| 7 | Scraper 2 (second approved source) | 150+ raw rows |
| 8 | Scraper 3 (third source, or documented fallback) | 150+ raw rows |
| 9 | Cleaning script + notebook + `listings_clean.csv` | 500+ clean rows, 100+ per source |
| 10 | Loader: POST clean CSV in batches to the API | MySQL count matches CSV |
| 11 | Frontend scaffold (Vite+React), fetch from API | numbers show in browser |
| 12 | Charts + KPI cards + loading/error states + styling | looks clean on desktop and phone width |
| 13 | README, `mysqldump`, light tests, code tidy | fresh-clone setup works |
| 14 | Deploy (optional bonus) | live URL works |
| 15 | Demo video recording + submission emails | checklist ticked |

Pause rule: before steps 6-8 (scraping) and step 14 (deploy), re-confirm sources/accounts with me.
