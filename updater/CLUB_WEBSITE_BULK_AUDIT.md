# Club website bulk audit (candidate triage)

The source directory at https://www.thenon-leaguenetwork.co.uk/clubs-directory lists club websites and postcodes. It explicitly says its data uses AI-assisted research and may be outdated. Treat **all** third-party URLs as unverified candidates, never as publish-ready facts.

1. Obtain a permitted CSV export with headings `Club Name`, `Website`, `Postcode` (other columns ignored). Do not bypass website controls or scrape against site terms.
2. Run `node updater/club_website_bulk_audit.js --source directory.csv --out /tmp/tffc-websites`.
3. Review `/tmp/tffc-websites.csv` and JSON counts. Existing website keys are excluded from candidate review. An exact normalised name plus matching postcode earns **high_confidence_candidate**, *not verified*. Without postcode agreement or with collisions, candidate is `needs_review`.
4. Independently confirm the candidate website belongs to the **same senior football club** using official site club identification, contact/ground information, or club/league cross-links. Record verification URL and date in a reviewed ledger. Never promote from candidate score alone.
5. Publish reviewed links in a **single substantial BETA PR**, retaining audit evidence and checking all 651 club names, existing links, and identity aliases. No production or competition-data changes.

CSV input is deliberately separate from the live Clubfinder. This script performs no network requests and cannot change a website link. For club names with collisions, require human review. The source's `Last Verified` field describes its own league allocation research, not a guarantee that a website is correct.

**Next integration:** add a controlled reviewed-ledger promotion step and regression tests before enabling any bulk website updates.
