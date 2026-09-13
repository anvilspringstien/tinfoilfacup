# Clubfinder Payload Classification

Read-only second-stage audit. Production Clubfinder is not modified. Reference counts below are identifier uses outside each declaration, so zero would be a strong dead-code signal; non-zero means only that the payload is still wired somewhere, not that it is irreducible.

## Key finding

- Embedded competition snapshot exactly matches `competition.json`: **YES**.
- The largest obvious saving is therefore architectural, not algorithmic: the same canonical competition state exists both as a live JSON file and as an inline offline fallback.
- The second large saving is static certificate artwork embedded as base64 data URIs.

## Payload classification

### `EMBEDDED_COMPETITION_DATA`
- Size: **1,353,221 bytes (1321.5 KiB)**
- References outside declaration: **4**
- Embedded data URIs inside assignment: **0**
- Classification: **required standalone fallback, but duplicated canonical payload**
- Semantically identical to competition.json; retained so Clubfinder still works when the live JSON fetch fails.

### `doc`
- Size: **581,071 bytes (567.5 KiB)**
- References outside declaration: **1**
- Embedded data URIs inside assignment: **6**
- Classification: **live application output mixed with replaceable static assets**
- Stats certificate HTML is live behaviour, but large inline image data can be externalised without changing certificate logic.

### `GROUNDS`
- Size: **179,737 bytes (175.5 KiB)**
- References outside declaration: **16**
- Embedded data URIs inside assignment: **0**
- Classification: **live core/static location payload**
- Used by current venue, map and journey fallback logic; candidate for extraction to a generated data file, not deletion.

### `ELIGIBLE`
- Size: **155,107 bytes (151.5 KiB)**
- References outside declaration: **7**
- Embedded data URIs inside assignment: **0**
- Classification: **live core/static origin payload**
- Drives the postcode nearest-club search and entry-round metadata; candidate for extraction, not deletion.

### `PRELIM_FIXTURES_BY_CLUB`
- Size: **76,638 bytes (74.8 KiB)**
- References outside declaration: **4**
- Embedded data URIs inside assignment: **0**
- Classification: **evolutionary fallback candidate**
- Older preliminary-round lookup still referenced. Must prove behavioural equivalence against competition.json before removal.

### `LAW2_ORIGIN_LOCATIONS`
- Size: **73,204 bytes (71.5 KiB)**
- References outside declaration: **2**
- Embedded data URIs inside assignment: **0**
- Classification: **live protected origin payload**
- Current Law 2 origin-location protection. Candidate for generated external data once validation is complete.

### `EPR_RESULTS_BY_TIE`
- Size: **35,440 bytes (34.6 KiB)**
- References outside declaration: **2**
- Embedded data URIs inside assignment: **0**
- Classification: **evolutionary fallback candidate**
- Hard-coded early-round results still referenced. Likely removable only after proving canonical competition data fully covers every protected journey.

### `CLUB_WEBSITES`
- Size: **2,050 bytes (2.0 KiB)**
- References outside declaration: **5**
- Embedded data URIs inside assignment: **0**
- Classification: **small live static payload**
- Negligible size; no reason to optimise first.

### `CURRENT_RESULT_OVERRIDES`
- Size: **1,628 bytes (1.6 KiB)**
- References outside declaration: **4**
- Embedded data URIs inside assignment: **0**
- Classification: **small compatibility layer**
- Tiny guarded override layer; keep until its cases are absorbed into canonical data and regression-tested.

### `NEXT_FIXTURE_OVERRIDES`
- Size: **1,077 bytes (1.1 KiB)**
- References outside declaration: **4**
- Embedded data URIs inside assignment: **0**
- Classification: **small compatibility layer**
- Tiny guarded override layer; keep until canonical fixtures make it redundant.

## Embedded image ownership

- `doc`: **6 image(s), 572,092 bytes (558.7 KiB)**
- `unassigned/global`: **2 image(s), 540,532 bytes (527.9 KiB)**

## Clean-sheet implication

A smaller Clubfinder should be built beside v7.6 from the settled requirements, with generated data separated from application code. The safest target architecture is: a small HTML/CSS/JS shell; canonical competition data loaded from `competition.json`; compact generated origin/ground data; certificate images as ordinary static assets; and an optional explicit offline snapshot only if offline/fetch-failure resilience remains a requirement.

Before deleting the preliminary/EPR fallback tables, run the full journey/replay/render regression suite with those tables deliberately disabled. That is the proof point for whether they are genuine evolutionary baggage or still required compatibility data.
