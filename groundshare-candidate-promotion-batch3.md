# Tin Foil FA Cup — Groundshare Candidate Promotion — Batch 3

Last checked: **27/08/2026, 13:33:44 UTC**

Mode: **DRY RUN**

- Confirmed relationships: **4**
- Directed relationships: **4**
- Undirected shared venues: **0**
- Rejected / not-current relationships excluded: **1**
- Canonical club records ready to add: **8**
- Existing canonical club records: **0**
- Groundshare ledger relationships ready: **4**
- Existing canonical records overwritten: **0**
- Published: **NO**

## Promotion plan

### #11 — Grays Athletic FC ↔ Tilbury FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **The EMR Stadium • RM18 8NL**
- **Grays Athletic FC** — ready to add from validated coordinates
- **Tilbury FC** — ready to add from validated coordinates

### #12 — Enfield FC ↔ Hertford Town FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **Hertingfordbury Park • SG13 8EX**
- **Enfield FC** — ready to add from validated coordinates
- **Hertford Town FC** — ready to add from validated coordinates

### #13 — Balham FC ↔ Tooting & Mitcham United FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **Imperial Fields • SM4 6BF**
- **Balham FC** — ready to add from validated coordinates
- **Tooting & Mitcham United FC** — ready to add from validated coordinates

### #15 — Dudley Town FC ↔ Sporting Khalsa FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **Guardian Warehousing Arena • WV13 3BB**
- **Dudley Town FC** — ready to add from validated coordinates
- **Sporting Khalsa FC** — ready to add from validated coordinates

## Explicitly excluded as not current

- **#14 — Hayes & Yeading United FC ↔ Southall FC** — `HUMAN_REJECTED_NOT_CURRENT`; excluded from this and later groundshare promotion. Current venue research points to **Honeycroft, Uxbridge**.

## Safety

- Only v7.8.9 Batch 3 `HUMAN_CONFIRMED` relationships #11, #12, #13 and #15 are eligible.
- Pair #14 is hard-excluded because v7.8.9 marks it `HUMAN_REJECTED_NOT_CURRENT`.
- Existing canonical `GROUNDS` records are never overwritten.
- Every missing club requires one matching machine-readable verification candidate with FCHD coordinates and `SHARED_POSTCODE` review evidence.
- Current venue names come from the human-confirmed evidence record; coordinates come from the persisted validated FCHD candidate.
- All four promoted relationships preserve explicit host/tenant direction.
- Ledger and canonical-record counts are calculated from current repository state, not hard-coded.
- Southall FC's Honeycroft current-venue correction is deliberately left for a separate correction pipeline.
- `competition.json` is untouched.
