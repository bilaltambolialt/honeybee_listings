# Data sources and compliance

The assignment asks for 500+ business listings from Google Maps, Justdial, Sulekha *or any other business directory*, and notes: *"Avoid scraping in a way that violates website terms of service. You may use mock/sample data if scraping is blocked (but explain approach)."*

Every candidate source was checked (robots.txt, terms of use, technical access) **before** any data was collected. Checks were made in October 2026.

## Sources used

| # | Source | Access method | Licence / terms | Rows |
|---|--------|---------------|-----------------|------|
| 1 | **OpenStreetMap** | Official Overpass API | ODbL: free reuse with attribution "(c) OpenStreetMap contributors". Fair use ~10,000 requests/day; 6 requests used | 468 |
| 2 | **Geoapify Places** | Official Places API (free key) | Terms allow results to be *"cache[d], store[d], and redistribute[d]… without any additional limits"*; attribution "Powered by Geoapify". ~156 of 3,000 daily credits used | 390 |
| 3 | **RBI bank-branch directory** | Open dataset published by Razorpay ([razorpay/ifsc](https://github.com/razorpay/ifsc)), compiled from Reserve Bank of India NEFT/RTGS lists | MIT licence: free to use, copy and publish | 150 |

Collectors identify themselves with a descriptive User-Agent that links this repository, pause between requests, and back off automatically on HTTP 429 (rate limit).

## Sources considered and rejected

| Site | Finding | Decision |
|------|---------|----------|
| **Justdial** | Terms of Use: *"You are prohibited from data mining, scraping, crawling, or using any process or processes that send automated queries to Just Dial… You may not use the Platforms… to compile a collection of listings."* Plain HTTP requests receive 403 responses. | Rejected |
| **Sulekha** | Terms: *"Any downloading of Content is unauthorised and/or prohibited… If any person/entity is found crawling Sulekha… for any commercial, business or other purposes, the same shall amount to offence and Sulekha shall be entitled to take appropriate action and claim damages."* | Rejected |
| **Google Maps** | robots.txt disallows `/maps/` for crawlers; Google Maps Platform terms prohibit scraping or exporting content. The only permitted route is the paid Places API. | Rejected |
| **Yelu.in** | Terms: users must not *"access [the] Website through any automated means (including… scripts or webcrawlers)."* | Rejected |
| **AskLaila** | Terms forbid users to *"reproduce, duplicate, copy… or redistribute or publish the information… without… prior express written consent… includ[ing] any attempt to incorporate any information… into any other directory."* | Rejected |
| **Cybo** | Terms: *"This information is not to be reused for public display."* | Rejected (this repository is public) |
| **FineLib** | Terms: *"Contents… may not be copied, reproduced, republished… or distributed in any way."* | Rejected |
| **Grotal** | Terms page has no usable content, so permission cannot be confirmed. | Rejected |

## Why this approach

- **Legal and reproducible:** every row can be re-collected by anyone running the collectors, without breaking any site's terms.
- **Same fields as the brief:** business name, category, city, address, phone (where available) and source.
- **City accuracy checks on bank data:** small co-operative banks register branch codes through a sponsor bank's office (often Mumbai), so they appear in cities where they have no branch. The collector keeps only banks with 15+ branches in the city, requires the address to agree with the city (PIN-code prefix or city name), and discards toll-free and shared helpline numbers (any number listed for more than 5 branches).
- **Data lineage is documented:** Geoapify builds on OpenStreetMap, so the Geoapify collector skips any place already collected from OpenStreetMap (matched by OSM id). The two files share zero records.

## Attribution

- Map data (c) OpenStreetMap contributors, available under the [Open Database License](https://www.openstreetmap.org/copyright).
- Places data powered by [Geoapify](https://www.geoapify.com/).
- Bank branch data from the Reserve Bank of India via [razorpay/ifsc](https://github.com/razorpay/ifsc) (MIT).
