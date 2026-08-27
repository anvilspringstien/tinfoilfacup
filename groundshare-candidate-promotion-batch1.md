# Tin Foil FA Cup — Groundshare Candidate Promotion — Batch 1

Last checked: **27/08/2026, 12:17:31 UTC**

Mode: **DRY RUN**

- Confirmed relationships: **4**
- Directed relationships: **3**
- Undirected shared venues: **1**
- Canonical club records ready to add: **8**
- Existing canonical club records: **0**
- Groundshare ledger relationships ready: **4**
- Held relationships: **1**
- Existing canonical records overwritten: **0**
- Published: **NO**

## Promotion plan

### #2 — Hackney Wick FC ↔ Witham Town FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **Simarco Stadium • CM8 1UN**
- **Hackney Wick FC** — ready to add from validated coordinates
- **Witham Town FC** — ready to add from validated coordinates

### #3 — Faversham Strike Force FC ↔ Whitstable Town FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **The Belmont Stadium / YMS Stadium • CT5 1QP**
- **Faversham Strike Force FC** — ready to add from validated coordinates
- **Whitstable Town FC** — ready to add from validated coordinates

### #4 — Bedworth United FC ↔ Nuneaton Town FC

- Relationship: **DIRECTED_HOST_TENANT**
- Venue: **The Oval • CV12 8NN**
- **Bedworth United FC** — ready to add from validated coordinates
- **Nuneaton Town FC** — ready to add from validated coordinates

### #5 — Soul Tower Hamlets FC ↔ Sporting Bengal United FC

- Relationship: **CONFIRMED_SHARED_VENUE_UNDIRECTED**
- Venue: **Mile End Stadium • E14 7TW**
- **Soul Tower Hamlets FC** — ready to add from validated coordinates
- **Sporting Bengal United FC** — ready to add from validated coordinates

## Held

- **Romulus FC ↔ Sutton Coldfield Town FC** — remains HELD_FOR_MORE_EVIDENCE; not promotion-eligible.

## Safety

- Only v7.8.3 `HUMAN_CONFIRMED` Batch 1 relationships are eligible.
- Romulus FC ↔ Sutton Coldfield Town FC remains excluded.
- Existing canonical `GROUNDS` records are never overwritten.
- Every missing club requires one matching machine-readable verification candidate with FCHD coordinates and `SHARED_POSTCODE` evidence.
- Directed relationships preserve explicit host/tenant direction.
- Soul Tower Hamlets FC ↔ Sporting Bengal United FC remains an undirected shared-venue relationship; no host is invented.
- Ledger counts and canonical-record counts are calculated from current repository state, not hard-coded.
- `competition.json` is untouched.
