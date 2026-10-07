# Decisions and trade-offs (use these in README "Challenges" and in the video)

- **MySQL, not Supabase:** the brief mandates MySQL; Supabase is Postgres, so it would fail the stack requirement.
- **Sources:** OpenStreetMap (Overpass API), Geoapify Places API and the RBI bank-branch directory: all openly licensed or explicitly permitting storage. Google Maps, Justdial and Sulekha avoided because their terms prohibit scraping (see `docs/DATA_SOURCES.md`).
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
- **Named platforms not scraped:** Justdial, Sulekha and Google Maps (and five other Indian directories) forbid scraping or republishing in their terms; the brief says to avoid ToS violations. Evidence with quotes is in `docs/DATA_SOURCES.md`.
- **RBI bank-branch directory as source 3:** fully independent of OpenStreetMap, MIT-licensed, official origin. Downloaded once (36 MB) into a git-ignored cache; only the 150-row sample is committed.
- **Accuracy over volume for bank data:** sponsor-bank registrations made ~1,100 "banks" appear in Mumbai. Filters (15+ local branches, address must match city by PIN prefix or name, helpline/toll-free numbers dropped) raised landline area-code agreement to 67/72 before cleaning.
- **Round-robin sampling across banks:** one branch per bank in turn, so 150 rows cover 49 banks instead of mostly the largest one.
- **Cleaning as a script plus a notebook:** `scraper/clean_listings.py` holds the logic (re-runnable with one command); `notebooks/cleaning_eda.ipynb` calls the same functions step by step and shows before/after evidence, so there is one source of truth.
- **Never guess data:** invalid phones (toll-free, wrong digit count, a spreadsheet-corrupted `1.13E+42`) are set to empty rather than "repaired"; phone completeness falls slightly (e.g. OSM 87.4% to 84.3%) in exchange for trustworthy values.
- **Phone standard:** first number kept when several are listed; prefixes stripped in dialling order (00, 91, 0); 8-digit local landlines get the city's area code. 107 raw formats became 3 (`+91 98765 43210`, `+91 22 2401 4419`, `+91 XXX XXX XXXX`).
- **Careful capitalisation:** only ALL-CAPS text is title-cased; a leading single upper-case word is kept (brands such as OYO, VLCC) and vowel-less abbreviations stay upper case.
- **English names preferred at collection time:** 6 names in Devanagari/Tamil script were replaced by their `name:en` equivalents in the collectors (not patched by hand), so re-running the pipeline reproduces them.
- **Loader goes through the API, in batches of 200:** small enough for clear progress and cheap retries, well under the API's 1,000-row cap. Network errors and 409 conflicts are retried; 422 validation errors stop the run because retrying cannot fix bad data.
- **Verified end to end:** after loading, every dashboard endpoint was compared with counts computed from the CSV (all match: 928 rows, 6 cities, 13 categories, 3 sources, 642 with phone), and a second run inserted 0 rows.
(Add more as we decide.)
