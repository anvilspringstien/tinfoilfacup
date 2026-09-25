# Tin Foil FA Cup — CURRENT BETA refactor checkpoint

**Last verified:** 25 September 2026 (BST), after merged dependency-map PR #95.  
**Source-of-truth for source code:** current `main`; **recovery source:** the pinned accepted BETA branch below.  
**Last green BETA source change:** `bc52268d04f00e9e0bf4f4e8b56a997f0144c58d` (PR #93). **Latest completed, guarded read-only audit:** `65a4e0f4d17535b69f5d00ba638799a76708d880` (PR #95).  
**Current BETA Challenges file blob at that merge:** `4383b17a4c38d10559016e06455b0869860eff9d`.

## Restore precisely if the chat or a working branch is interrupted

1. Open [the manually accepted BETA checkpoint](https://github.com/anvilspringstien/tinfoilfacup/tree/checkpoint/accepted-beta-20260925) pinned to `89f0338e5f11f8e7a36d3bf69e57e3be88fc264f`; accepted on iPhone 14 after PRs #87–#89. This is a **source-code recovery point**, not a replacement for subsequent live competition updates.
2. Inspect current `main` and its newest automatic competition-data commits *before* rebasing any working branch. Never restore an old `competition.json` or production `clubfinder.html` wholesale.
3. Open the [initial recovery and inventory document](./2026-09-25-recovery-and-inventory.md) and the [historical full-source map](./2026-09-25-generated-source-map.md). The source map deliberately records the **pre-cleanup audit commit**; its hashes and competition timestamps are **not** a continuously updated status page.
4. Inspect the latest refactoring PR(s), verify exact file diffs and GitHub Actions steps, and resume from the last green merge listed below. For any new BETA HTML changes, run the established direct-entry/Trophy and identity/historical regression guards; keep each PR narrow.

## Completed, guarded work

| PR | Merge commit | Change | Automated gate |
|---|---|---|---|
| [#90](https://github.com/anvilspringstien/tinfoilfacup/pull/90) | `1ec8c11` | Initial recovery document, full-file inventory runner and reproducible source map | Stage 1 inventory workflow passed |
| [#91](https://github.com/anvilspringstien/tinfoilfacup/pull/91) | `a621897` | Remove the orphaned 4,109-character newer splash CSS block from BETA Challenges | Deck, Trophy, identity, Petts Wood, Exmouth, Weston and protected-file gate passed |
| [#92](https://github.com/anvilspringstien/tinfoilfacup/pull/92) | `6faf970` | Remove another 1,317 characters of unused **original** splash CSS | Same full BETA direct-entry guard passed |
| [#93](https://github.com/anvilspringstien/tinfoilfacup/pull/93) | `bc52268` | Remove 1,274 characters of detached Challenges Stats CSS; strengthen CSS guard self-tests | Same full BETA direct-entry guard passed |
| [#95](https://github.com/anvilspringstien/tinfoilfacup/pull/95) | `65a4e0f` | Full untruncated BETA Deck/Clubfinder dependency map and storage/compatibility inventory (no app changes) | Deck, Trophy, identity, Petts Wood, Exmouth, Weston, accepted mobile patch guard, reproducible report and protected-file gates passed |

All three functional cleanup PRs changed **only** `beta/challenges-beta.html` and `tests/test_beta_challenges_direct_entry.js`. Production Clubfinder, BETA Clubfinder, canonical competition data, updater, challenge mechanics and persisted storage schemas were **not** changed by these PRs. The original accepted source is still available at its pinned checkpoint.

## Critical audited dependencies — protect during the next stage

- `renderStats()` is **NOT dead code**. It is still called by `save()`, startup and actions; it updates simulator counters, the new Call Sign / Pigeon Name / Pigeon Miles Flown / Current Campaign Round frame, and Trophy Cabinet contents. Its legacy name is misleading, but removing it will break the Deck.
- `applySimulationChange()` and BETA simulator controls are active testing machinery. Do not remove them until a tested replacement provides equivalent coverage and the live bridge is validated.
- `openTrophy()`, `advanceTrophy()`, saved-state keys and bridge identity matching are active and regression-protected. Preserve the iPhone mat-height and full Pigeon McPigeonface fixes.
- BETA Clubfinder is a ~4.6 MB source file; use **in-repository full-file tooling**, not a potentially truncated connector result, for any substantive code audit or patch.
- The initial inventory found the BETA embedded offline competition snapshot **stale** against a later canonical main update. Live `../competition.json` remains authoritative. Run `updater/refresh_beta_embedded_snapshot.py` in its **own** guarded data-fallback PR whenever a strict current-canonical smoke check requires freshness; normal competition ingestion can advance in the meantime.

## Latest read-only dependency audit (#95)

The [full-source dependency report](./2026-09-25-dependency-map.md) is a **historical, commit-scoped** artifact, generated on the repository runner from the complete files. It records **30** Deck and **150** Clubfinder named functions and maps seven key persistent/session browser-storage contracts. The scanner found **47 CSS class candidates** with no exact static markup/JS references, but dynamic markup produces false positives: no CSS is approved for removal without manual checks.

The audit confirmed (a) `journeyTies` migration on load; (b) the Clubfinder bridge's counters, mileage, round, Call Sign and Pigeon Name; (c) origin-and-selection-date identity-backup matching; (d) old Stats-tab return-index compatibility; and (e) explicit Challenges-to-Clubfinder return. **Preserve all five.** `renderStats()` remains active. Production and both BETA HTML files were unchanged by #95.

The offline fallback in this specific audit was **STALE**: embedded `2026-09-25T07:49:01.065159+00:00`, canonical `2026-09-25T13:47:51.590346+00:00`. This is a historical observation, not necessarily the latest canonical timestamp. The live canonical fetch is authoritative; refresh offline data in a **separate guarded PR** if strict fallback parity is required.

## Next isolated task

Manually cross-check the 47 candidate classes against generated Deck markup and browser-side selectors, then choose only **proved unreachable** CSS for a small guarded PR. Add focused regression assertions for all active storage/identity/return contracts **before** renaming the progress renderer or splitting campaign-bridge code. Never delete the simulator or legacy save migration merely because their names are historical. For each new PR inspect current `main` first—normal competition ingestion may have advanced again—and append exact merged SHA and green checks here.

**Manual acceptance distinction:** the user accepted the pre-refactor BETA on iPhone 14 on 25 September; PRs #91–#93 passed automated gates but have not been represented as fresh manual phone acceptance.
