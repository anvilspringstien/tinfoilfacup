# Tin Foil FA Cup — CURRENT BETA refactor checkpoint

**Last verified:** 25 September 2026 (BST), after completed and guarded **BETA bridge Stage A PR #103**; [structural plan](./2026-09-25-bridge-render-structural-plan.md) remains the staged roadmap.  
**Source-of-truth for source code:** current `main`; **recovery source:** the pinned accepted BETA branch below.  
**Last green BETA source change:** `4f7793b4e36d419d66dc7fd28b873d28be9a5ed6` (PR #103). **Latest green test-only change:** `c02c5aea26963b006150d995413b3c0563c8f184` (PR #99). **Latest green CI preparation:** `9d7e449b6a69e41d7233e38ff6027071aa528bed` (PR #101). **Read-only dependency audit:** `65a4e0f4d17535b69f5d00ba638799a76708d880` (PR #95).  
**Current BETA Challenges file blob at that merge:** `dd929516698137548c82a2de437e18ab44811c73`.

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
| [#97](https://github.com/anvilspringstien/tinfoilfacup/pull/97) | `88eecd8` | Delete 893 characters of retired launch-only CSS for `#openChallenges`, `.challenge-launch` and `.challenges-btn`; add a regression guard | Deck, Trophy, identity, Petts Wood, Exmouth, Weston and protected-file CI passed |
| [#99](https://github.com/anvilspringstien/tinfoilfacup/pull/99) | `c02c5ae` | BETA tests for existing saved Challenges, legacy migration, protected Pigeon identity and actual Clubfinder → Deck → Clubfinder handover; expand CI trigger and protected-file guard | Challenges/Deck/Trophy/identity/Petts Wood/Exmouth/Weston and mobile Pigeon Name workflows passed; no app/data files changed |
| [#101](https://github.com/anvilspringstien/tinfoilfacup/pull/101) | `9d7e449` | Permit intentional tested BETA Deck refactor PRs in the full bridge/Trophy CI, while preserving guards on production, canonical data and independent BETA Clubfinder | Full BETA direct-entry and historic regressions passed; workflow-only change |
| [#103](https://github.com/anvilspringstien/tinfoilfacup/pull/103) | `4f7793b` | Stage A: isolate BETA Deck JSON storage reader, progress normalization and origin/selection-matched identity backup; add malformed/undated/negative/nonfinite bridge tests | [Full direct BETA Challenges workflow](https://github.com/anvilspringstien/tinfoilfacup/actions/runs/36150801246) passed Deck, Trophy, bridge, identity, Petts Wood, Exmouth, Weston and protected-file checks |


All four functional cleanup PRs changed **only** `beta/challenges-beta.html` and `tests/test_beta_challenges_direct_entry.js`. Production Clubfinder, BETA Clubfinder, canonical competition data, updater, challenge mechanics and persisted storage schemas were **not** changed by these PRs. The original accepted source is still available at its pinned checkpoint.

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

## Reviewed CSS candidate: retired launch buttons (#97)

Manual source inspection proved that `#openChallenges`, `.challenge-launch` and `.challenges-btn` were used only in one historic styling block: no matching DOM elements, generated markup or JavaScript references remain in BETA Challenges. PR #97 removed **exactly 893 characters** of this CSS and introduced a regression guard. Its GitHub Actions workflow passed the direct Deck, Trophy Cabinet, campaign identity, Petts Wood, Exmouth, Weston and protected-file checks before merge. This was a BETA Challenges CSS-only change with no update to the live simulator, phone mat sizing, original checkpoint or the competition updater.

**Do not assume all 47 original CSS candidates are dead:** their names come from a conservative textual scan, and the simulator's earlier overlays/skins have interdependent or dynamically generated styles. Each additional deletion needs its own targeted source and CSS-cascade review.

## Completed cross-page campaign contract safety net (#99)

The [new standalone bridge regression](../../tests/test_beta_campaign_bridge_contract.js) boots the **actual** BETA Challenges script against isolated saved browser data. It checks long Pigeon Names, Call Signs, verified mileage and round, previously completed Trophy Cabinet entries, persisted Honour records, Exit/re-entry/refresh, and award of new verified campaign achievements. It prevents mismatched-origin and mismatched-selection backups from leaking into another campaign; protects legacy `journeyTies` migration, rejects malformed/foreign bridges, disables progression of ended campaigns, and preserves old Stats-return index compatibility.

The [expanded Clubfinder identity regression](../../updater/beta_campaign_identity_regression.js) executes the actual Clubfinder `openChallenges()` path and checks the complete bridge payload, exact rendered Campaign return snapshot, postcode/Pigeon Name restoration and **no additional counter allocation**. The [CI workflow](../../.github/workflows/beta-challenges-direct-entry.yml) runs the new tests alongside established Deck/Trophy, Petts Wood, Exmouth and Weston regressions, and now guards **both BETA HTML files** as well as protected production and canonical data.

PR #99's Challenges workflow and independent mobile Pigeon Name workflow were both **green** before squash merge at `c02c5ae`. This was **tests and CI only**: no new app UI acceptance is implied, and the manually approved BETA recovery branch remains pinned at `89f0338`.

## Structural refactor prepared (plan only)

The [guarded bridge/render refactoring plan](./2026-09-25-bridge-render-structural-plan.md) defines four independent stages: (A) Deck-only pure bridge/identity helpers behind the existing `applyClubfinderCampaignTruth()` interface; (B) decompose the **active** `renderStats()` display into truth-frame, simulator and Trophy Cabinet helpers while retaining its wrapper; (C) separately investigate the huge BETA Clubfinder producer and use a dedicated safe workflow **before editing it**; (D) consider an external shared script only if it has a measured benefit and no Wix/GitHub Pages loading regression. Every stage preserves the v1 storage, identity/date matching, historical trophy migration, venue-derived Pigeon Miles and old Stats-tab navigation. This is a plan, not authorisation to change production.

## Completed structural Stage A — BETA bridge reader (#103)

PR #103 separated the actual Deck bridge reader into four small internal helpers: `readChallengeStorageJSON`, `normalizeBridgeProgress`, `normalizeBridgeIdentity` and `matchingCampaignIdentityBackup`. The existing `applyClubfinderCampaignTruth()` entry point and all v1 keys, legacy `journeyTies` save migration, trophy award sequence, origin/date identity-backup semantics, simulator and active `renderStats()` were preserved. The backup remains unread when the current bridge has its own usable Pigeon Name. A deliberate defensive improvement converts invalid/nonfinite numbers to zero while preserving existing finite numeric and numeric-string values and negative-to-zero clamping. The new tests also exercise absent/malformed backups and legacy undated matching-origin records. The CI workflow run [36150801246](https://github.com/anvilspringstien/tinfoilfacup/actions/runs/36150801246) **passed** all Deck/bridge/Trophy/identity and historic venue/replay regressions plus the current production/canonical/BETA Clubfinder guard before merge. The resulting Deck blob is `dd929516698137548c82a2de437e18ab44811c73` and the exact green merge is `4f7793b4e36d419d66dc7fd28b873d28be9a5ed6`. No production, BETA Clubfinder, competition data or updater changes were part of #103.

**Current CI clarification:** PR #101 intentionally relaxed the #99 *Deck-specific* workflow's final guard to allow tested changes to `beta/challenges-beta.html`; it **continues** prohibiting edits to production, canonical data and the separate BETA Clubfinder. The old #99 section above describes its historical test-only checkpoint, not the latest guard configuration.

## Next isolated task

Take **Stage B** from the [structural plan](./2026-09-25-bridge-render-structural-plan.md): preserve `renderStats()` as a stable wrapper, split the *active* truth frame, simulator and Trophy Cabinet presentation into small internal helpers, and add display-focused regression cases before changing the Deck. Do not change its DOM/CSS or remove the simulator. Existing bridge and browser-storage contracts remain non-negotiable. Refine remaining CSS candidates only in separate, proven-dead cleanup PRs; refresh the offline competition snapshot only in a separate guarded data PR. Check current `main` and the last green CI run before branching.

**Manual acceptance distinction:** the user accepted the pre-refactor BETA on iPhone 14 on 25 September; PRs #91–#93, #97 and #103 passed automated gates but have not been represented as fresh manual phone acceptance.
