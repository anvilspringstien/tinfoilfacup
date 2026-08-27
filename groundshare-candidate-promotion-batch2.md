# Tin Foil FA Cup — Groundshare Candidate Promotion — Batch 2

Last checked: **27/08/2026, 13:13:16 UTC**

Mode: **DRY RUN**

- Confirmed relationships: **3**
- Directed relationships: **2**
- Undirected shared venues: **1**
- Rejected / not-current relationships excluded: **2**
- Canonical club records ready to add: **6**
- Existing canonical club records: **0**
- Groundshare ledger relationships ready: **3**
- Existing canonical records overwritten: **0**
- Published: **NO**

## Promotion plan

### #6 — Walthamstow FC ↔ West Essex FC

- Relationship: **CONFIRMED_SHARED_VENUE_UNDIRECTED**
- Venue: **Wadham Lodge Stadium / Wadham Lodge Sports Ground (Match Day Centres) • E17 4JP**
- **Walthamstow FC** — ready to add from validated coordinates
- **West Essex FC** — ready to add from validated coordinates

### #7 — Broadfields United FC ↔ Rayners Lane FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **Tithe Farm Sports & Social Club • HA2 0XH**
- **Broadfields United FC** — ready to add from validated coordinates
- **Rayners Lane FC** — ready to add from validated coordinates

### #9 — Barwell FC ↔ Hinckley AFC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **Kirkby Road • LE9 8FQ**
- **Barwell FC** — ready to add from validated coordinates
- **Hinckley AFC** — ready to add from validated coordinates

## Explicitly excluded as not current

- **#8 — Cobham FC ↔ Epsom & Ewell FC** — `HUMAN_REJECTED_NOT_CURRENT`; excluded from this and later groundshare promotion. Current venue research points to **Chalky Lane, Chessington**.
- **#10 — Belper United FC ↔ Eastwood Community FC** — `HUMAN_REJECTED_NOT_CURRENT`; excluded from this and later groundshare promotion. Current venue research points to **Don Amott Arena, Mickleover**.

## Safety

- Only v7.8.6 Batch 2 `HUMAN_CONFIRMED` relationships #6, #7 and #9 are eligible.
- Pairs #8 and #10 are hard-excluded because v7.8.6 marks them `HUMAN_REJECTED_NOT_CURRENT`.
- Existing canonical `GROUNDS` records are never overwritten.
- Every missing club requires one matching machine-readable verification candidate with FCHD coordinates and `SHARED_POSTCODE` review evidence.
- Current venue names come from the human-confirmed evidence record; coordinates come from the persisted validated FCHD candidate.
- Directed relationships preserve explicit host/tenant direction.
- Walthamstow FC ↔ West Essex FC remains an undirected shared-venue relationship; no host is invented.
- Ledger and canonical-record counts are calculated from current repository state, not hard-coded.
- Epsom & Ewell FC and Belper United FC current-venue corrections are deliberately left for a separate correction pipeline.
- `competition.json` is untouched.
