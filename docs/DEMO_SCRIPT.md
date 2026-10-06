# Demo video script (target 4:00, hard limit 5:00)

| Time | Show | Say |
|------|------|-----|
| 0:00-0:20 | Title / repo tree | Who I am, what the project is, stack |
| 0:20-1:20 | Scraper code + raw CSV | Sources chosen and why, ToS/robots handling, rate limiting, fields captured, challenges |
| 1:20-1:50 | Cleaning notebook/CSV | What I cleaned (names, cities, phones, duplicates), final row counts per source |
| 1:50-2:30 | MySQL table in Workbench/CLI | Schema, indexes, dedupe key, row count |
| 2:30-3:20 | FastAPI `/docs` | Run bulk insert, then city/category/source endpoints, show JSON |
| 3:20-4:00 | Dashboard in browser | KPI cards, three charts, loading/error states, refresh after new data |
| 4:00-4:20 | README / repo | Setup steps, challenges, what I would improve |

Role-specific emphasis (same video body, change only intro and outro, or record a second take):
- Data Science: lead with data quality, cleaning steps, CSV, notebook/EDA.
- Python Development: lead with API design, validation, DB schema, code structure.
Tips: rehearse once, 1080p screen recording (OBS or Loom), zoom the browser to 125%, no secrets on screen.
