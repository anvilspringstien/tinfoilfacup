# Clubfinder Size Audit

Read-only structural audit of the current production `clubfinder.html`. No Clubfinder behaviour is changed by this audit.

## Headline

- **clubfinder.html:** 3,064,657 bytes (2992.8 KiB, 2.92 MiB)
- **gzip level 9:** 969,478 bytes (946.8 KiB, 0.92 MiB)
- **competition.json:** 1,820,286 bytes (1777.6 KiB, 1.74 MiB)

## Broad composition

- Inline `<script>` content: **3,057,170 bytes (2985.5 KiB, 2.92 MiB)** (99.8% of file)
- Outer-page `<style>` content: **6,078 bytes (5.9 KiB, 0.01 MiB)** (0.2% of file)
- Remaining HTML/tag shell: **1,409 bytes (1.4 KiB, 0.00 MiB)** (0.0% of file)
- Embedded base64 data URIs: **1,112,624 bytes (1086.5 KiB, 1.06 MiB)** across **8** URI(s) (36.3% of file)

## Largest JavaScript assignments (heuristic)

- `EMBEDDED_COMPETITION_DATA` — **1,353,221 bytes (1321.5 KiB, 1.29 MiB)**
- `doc` — **581,071 bytes (567.5 KiB, 0.55 MiB)**
- `GROUNDS` — **179,737 bytes (175.5 KiB, 0.17 MiB)**
- `ELIGIBLE` — **155,107 bytes (151.5 KiB, 0.15 MiB)**
- `PRELIM_FIXTURES_BY_CLUB` — **76,638 bytes (74.8 KiB, 0.07 MiB)**
- `LAW2_ORIGIN_LOCATIONS` — **73,204 bytes (71.5 KiB, 0.07 MiB)**
- `EPR_RESULTS_BY_TIE` — **35,440 bytes (34.6 KiB, 0.03 MiB)**
- `CLUB_WEBSITES` — **2,050 bytes (2.0 KiB, 0.00 MiB)**
- `CURRENT_RESULT_OVERRIDES` — **1,628 bytes (1.6 KiB, 0.00 MiB)**
- `NEXT_FIXTURE_OVERRIDES` — **1,077 bytes (1.1 KiB, 0.00 MiB)**

## Embedded base64 payloads

- Data URI #7 `image/png` — **293,250 bytes (286.4 KiB, 0.28 MiB)**
- Data URI #1 `image/png` — **286,854 bytes (280.1 KiB, 0.27 MiB)**
- Data URI #8 `image/png` — **247,282 bytes (241.5 KiB, 0.24 MiB)**
- Data URI #5 `image/png` — **65,606 bytes (64.1 KiB, 0.06 MiB)**
- Data URI #6 `image/png` — **61,414 bytes (60.0 KiB, 0.06 MiB)**
- Data URI #4 `image/png` — **55,154 bytes (53.9 KiB, 0.05 MiB)**
- Data URI #2 `image/png` — **54,274 bytes (53.0 KiB, 0.05 MiB)**
- Data URI #3 `image/png` — **48,790 bytes (47.6 KiB, 0.05 MiB)**

## Large quoted literals

- **268,514 bytes (262.2 KiB, 0.26 MiB)** — `s Stortford","away":"Berkhamsted","home_score":2,"away_score":3,"winner":"Berkha…`
- **89,927 bytes (87.8 KiB, 0.09 MiB)** — `s Stortford","away":"Berkhamsted","home_score":2,"away_score":3,"winner":"Berkha…`
- **17,394 bytes (17.0 KiB, 0.02 MiB)** — `s Energy Stadium","postcode":"GL52 3PD","source":"https://fchd.info/maps/GAZ.htm…`

## What this means

This report deliberately separates **payload weight** from **application logic**. A large standalone HTML file is not automatically bloated code: embedded competition snapshots and inline image assets can dominate the byte count while the actual UI/logic remains comparatively small.

The next step should be to classify the largest assignments and embedded payloads as one of: **required standalone payload**, **replaceable external/static asset**, **duplicated/evolutionary baggage**, or **live application logic**. Only then should a clean-sheet smaller build be attempted.
