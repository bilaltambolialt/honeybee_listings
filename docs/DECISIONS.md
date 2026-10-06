# Decisions and trade-offs (use these in README "Challenges" and in the video)

- **MySQL, not Supabase:** the brief mandates MySQL; Supabase is Postgres, so it would fail the stack requirement.
- **Sources:** OpenStreetMap Overpass (open data, legal) + a places API + a ToS-permitted directory. Google Maps and Justdial avoided because their terms prohibit scraping and they block bots.
- **Dedupe key:** sha256 hash column, because a UNIQUE index on long text columns is awkward in MySQL utf8mb4.
- **Data goes through the Insert API,** not directly into MySQL, to prove the API works end to end.
- **Single codebase for both roles;** only the submission email and video emphasis differ.
- **Duplicate handling in the API:** one indexed `SELECT ... IN (...)` to find existing keys, then insert only new rows; the UNIQUE index is the safety net (409 on a race). Chosen over `INSERT IGNORE`, which also silences unrelated errors such as truncation.
- **Request body is a plain JSON array,** capped at 1000 rows per batch, so the loader sends data in manageable chunks.
- **API trims, cleaning normalises:** the API only trims whitespace and stores blanks as NULL; heavier normalisation (casing, inner spaces, phone formats) happens in the cleaning step, keeping each stage's job clear.
- **Aggregation happens in MySQL, not Python:** `GROUP BY` on indexed columns returns a few small rows instead of shipping every listing to the API; it scales to millions of rows.
- **Stable ordering:** counts sorted descending with alphabetical tie-break, so the charts never reshuffle between refreshes.
- **`with_phone` KPI in the summary:** a simple data-quality signal (contact coverage) alongside the volume totals.
- **OpenStreetMap via the official Overpass API** (not HTML scraping): open data under ODbL, explicit fair-use limits (~10,000 requests/day, 1 GB/day). The collector sends 6 requests in total, identifies itself with a descriptive User-Agent, pauses 15 s between cities and backs off on HTTP 429. Attribution: "(c) OpenStreetMap contributors".
- **Balanced sampling:** OSM returned 22,365 matching places, heavily skewed (e.g. Bengaluru alone had 8,748). The collector keeps up to 5 per city x category, preferring records with an address and phone, giving 390 evenly spread rows so the charts compare like with like.
- **Common raw format:** every collector writes the same columns (plus `source_id`, coordinates and `scraped_at` for traceability), so cleaning can combine sources directly.
- **Geoapify Places API as source 2:** official keyed API; its terms allow results to be cached, stored and redistributed. Free plan: 3,000 credits/day, 5 req/s; the collector uses ~156 credits with a 0.5 s pause. Attribution: "Powered by Geoapify" and "(c) OpenStreetMap contributors".
- **Keeping sources distinct:** Geoapify builds much of its places data on OpenStreetMap, so the collector skips any place whose OSM id was already collected in source 1 (111 of 2,952 candidates) and keeps each place once even if it sits in two categories. Result: zero shared records between the two files. Same-name rows in the same city (e.g. chain branches) are kept because their addresses differ.
(Add more as we decide.)
