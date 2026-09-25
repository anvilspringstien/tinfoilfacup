# Tin Foil FA Cup — CURRENT BETA refactor checkpoint

**Last verified:** 25 September 2026 (BST), after merged PR #93.  
**Source-of-truth for source code:** current `main`; **recovery source:** the pinned accepted BETA branch below.  
**Last green BETA CSS-cleanup merge:** `bc52268d04f00e9e0bf4f4e8b56a997f0144c58d` (PR #93).  
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

All three functional cleanup PRs changed **only** `beta/challenges-beta.html` and `tests/test_beta_challenges_direct_entry.js`. Production Clubfinder, BETA Clubfinder, canonical competition data, updater, challenge mechanics and persisted storage schemas were **not** changed by these PRs. The original accepted source is still available at its pinned checkpoint.

## Critical audited dependencies — protect during the next stage

- `renderStats()` is **NOT dead code**. It is still called by `save()`, startup and actions; it updates simulator counters, the new Call Sign / Pigeon Name / Pigeon Miles Flown / Current Campaign Round frame, and Trophy Cabinet contents. Its legacy name is misleading, but removing it will break the Deck.
- `applySimulationChange()` and BETA simulator controls are active testing machinery. Do not remove them until a tested replacement provides equivalent coverage and the live bridge is validated.
- `openTrophy()`, `advanceTrophy()`, saved-state keys and bridge identity matching are active and regression-protected. Preserve the iPhone mat-height and full Pigeon McPigeonface fixes.
- BETA Clubfinder is a ~4.6 MB source file; use **in-repository full-file tooling**, not a potentially truncated connector result, for any substantive code audit or patch.
- The initial inventory found the BETA embedded offline competition snapshot **stale** against a later canonical main update. Live `../competition.json` remains authoritative. Run `updater/refresh_beta_embedded_snapshot.py` in its **own** guarded data-fallback PR whenever a strict current-canonical smoke check requires freshness; normal competition ingestion can advance in the meantime.

## Next isolated task

Perform a **read-only dependency map** of the remaining Challenge Deck script/CSS and the BETA Clubfinder campaign bridge, identifying genuinely unused styles/functions, explicit dynamic references and active storage contracts. Only then choose the next tiny functional change. Use a fresh branch from then-current `main`, run the established guards, and add its exact green merge SHA to this document.

**Manual acceptance distinction:** the user accepted the pre-refactor BETA on iPhone 14 on 25 September; PRs #91–#93 passed automated gates but have not been represented as fresh manual phone acceptance.
