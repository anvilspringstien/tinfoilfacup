# Tin Foil FA Cup — BETA refactor recovery checkpoint and initial inventory

Status: **Stage 1 / read-only inventory. No functional refactor authorised or applied.**  
Date: **25 September 2026 (BST)**

## Immutable recovery anchors

- **User-accepted BETA snapshot:** `89f0338e5f11f8e7a36d3bf69e57e3be88fc264f` (merged PR #88, following #89 and #87). GitHub branch: [checkpoint/accepted-beta-20260925](../../tree/checkpoint/accepted-beta-20260925). The user manually accepted the iPhone 14 results on 25 September: full `Pigeon McPigeonface` and corrected Deck-to-feedback spacing.
- **Refactor inventory starting point:** `1ab8276ba18d43513ef50c922fbbbe737ff23e72` on `main`, used as the parent of `refactor/beta-inventory-20260925`. Since the accepted BETA snapshot, routine pipeline commits `3abf3776` (canonical competition chronology, production and health report) and `1ab8276b` (ground-health output) advanced main. **Do not revert those live updates when restoring BETA presentation.**
- **Known accepted BETA Clubfinder blob:** `11a8af24cffcf2432c085f7d1bab88531dd71202`. **Known accepted BETA Challenges blob:** `85bf65ee637f7ff96576128ddf58ffb60ede51a4`.
- Recovery: restore or compare the two BETA files from the accepted commit/branch; do **not** replace current `competition.json` or production `clubfinder.html` with September 25's frozen competition data. Always inspect current main and replay any subsequent verified ingestion first.

## Protected boundaries

1. Keep production `clubfinder.html`, canonical `competition.json`, ingest/updater pipeline, and existing campaign storage untouched by Stage 1.
2. Keep BETA challenges and BETA clubfinder code unchanged until the inventory and call/dependency checks are reviewed.
3. Every future small PR must explicitly list changed files, an exact source commit, regression checks, and rollback SHA; run the established regression guards. No wholesale copy from production into BETA.
4. A fresh live canonical update can make BETA's embedded offline fallback stale; the **live data URL remains authoritative**. Use the existing guarded `updater/refresh_beta_embedded_snapshot.py` for a separate, isolated snapshot refresh; never bundle that large data update with a behaviour refactor.
5. If interrupted: inspect this document, accepted checkpoint, current `main`, latest refactor PR and Actions run before changing files.

## Initial verified Challenges inventory (from accepted source and existing tests)

- `beta/challenges-beta.html`: 88,615 UTF-8 characters, 2,045 lines, five embedded CSS blocks, one inline JavaScript block (~35 KB), ~30 named functions. Key functions include `loadState`, `save`, `applyClubfinderCampaignTruth`, `awardCampaignChallenges`, `isUnlocked`, `render`, `openTrophy`, `advanceTrophy`, `closeTrophy`, `tinFoilReturnToClubfinder`, `renderStats`, and `applySimulationChange`.
- Persistent state contracts from the existing tests: `tffc.challengeDeck.v1`, `tffc.clubfinderCampaign.v1`, and `tffc.clubfinderCampaignIdentity.v1`. The Deck also stores navigation context. Do not change storage key names/schema or the Clubfinder-to-Challenges bridge during cleanup.
- PRs #84–#87 replaced splash and detached Challenge Stats UI, added the three-line truth frame, three-tap Trophy Cabinet, and fixed phone-only mat spacing. `renderStats` and historic splash references still appear in source; these are **inspection candidates, not proven safe-to-delete code**.
- The BETA simulator is present and remains the only manual progression harness until an explicitly tested replacement is ready.
- `tests/test_beta_challenges_direct_entry.js` and `tests/test_beta_trophy_viewer.js` boot standalone embedded scripts with stubbed browser/storage and exercise Deck entry, navigation, persisted state, cabinet and three-tap viewer. `.github/workflows/beta-challenges-direct-entry.yml` additionally runs identity, Petts Wood, Exmouth and Weston regressions and guards the protected files.

## Initial verified BETA Clubfinder boundary (from guarded PR #88 and tests)

- `beta/clubfinder-beta.html` is a large source file; a full-file **in-repository audit** is preferable to a truncated connector response. Existing `updater/beta_campaign_identity_regression.js` covers the 20-character name cap, full 19-character `Pigeon McPigeonface` across save/redraw/refresh, the separate mobile Call Sign and Pigeon Name rows, 680px phone break, Stats presentation, canonical Pigeon Miles Flown naming and historic-venue/replay behaviour.
- `updater/patch_beta_mobile_pigeon_name.py --check` is idempotent; preserve its guarded patch boundary until the associated markup/CSS is deliberately refactored and its tests rewritten together.
- `updater/refresh_beta_embedded_snapshot.py --check` requires the embedded fallback to equal current canonical competition data. Given the routine main chronology update **after** the accepted BETA merge, freshness must be checked against the current canonical file before claiming the standard BETA smoke is green.

## Proposed small, reversible stages

1. **Read-only full source inventory and dependency map:** names, scripts/CSS footprint, storage keys, navigation contracts, dead-code candidates, full-file SHA and snapshot freshness.
2. **Challenge-only inert cleanup:** remove proved-unreachable splash/Stats styles and routines in isolated PRs; maintain simulator and all existing tests.
3. **Campaign/bridge consolidation:** preserve all storage schemas and challenge unlock rules; eliminate only verified duplication, with saved-campaign migration regression coverage.
4. **Simulator separation and performance:** remove BETA simulator only when live bridge and independent manual test control are demonstrated; independently assess CSS/JS and asset performance.
5. **Post-change parity:** full Petts Wood, Exmouth, Weston, replay, venue and Stats checks, manual desktop/iPad/iPhone 14 acceptance, and read-only comparison to production. No production promotion is implied.

## Resumption checklist

- Check whether `refactor/beta-inventory-20260925` has a draft PR and review its exact diff and workflow conclusions.
- Read the latest inventory document and compare its recorded SHAs with `main`.
- Run the guards on the **current** canonical chronology, refreshing the BETA fallback in a **separate** guarded PR if necessary.
- Implement only the next isolated item after confirming the previous PR's complete green checkpoint.
