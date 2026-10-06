# Decisions and trade-offs (use these in README "Challenges" and in the video)

- **MySQL, not Supabase:** the brief mandates MySQL; Supabase is Postgres, so it would fail the stack requirement.
- **Sources:** OpenStreetMap Overpass (open data, legal) + a places API + a ToS-permitted directory. Google Maps and Justdial avoided because their terms prohibit scraping and they block bots.
- **Dedupe key:** sha256 hash column, because a UNIQUE index on long text columns is awkward in MySQL utf8mb4.
- **Data goes through the Insert API,** not directly into MySQL, to prove the API works end to end.
- **Single codebase for both roles;** only the submission email and video emphasis differ.
(Add more as we decide.)
