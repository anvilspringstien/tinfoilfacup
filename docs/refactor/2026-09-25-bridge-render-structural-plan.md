# Tin Foil FA Cup — guarded BETA bridge and renderer refactor plan

**Prepared:** 25 September 2026 (BST). **Status:** design and acceptance gates only. No application source changes in this document.
**Starting source:** `beta/challenges-beta.html` blob `7989e3a0d89bb7425837d3474a46eacddc53182e`; `beta/clubfinder-beta.html` blob `11a8af24cffcf2432c085f7d1bab88531dd71202`. Check actual current `main` again before every subsequent branch.
**Accepted recovery:** [checkpoint/accepted-beta-20260925](https://github.com/anvilspringstien/tinfoilfacup/tree/checkpoint/accepted-beta-20260925), pinned at `89f0338`. Never restore its old production or competition data over later verified ingestion.

## Scope and evidence

Read the [complete-file dependency map](./2026-09-25-dependency-map.md) and [current recovery checkpoint](./CURRENT.md) first. The dependency map is commit-scoped; update fingerprints before treating it as a comparison for modified BETA HTML.

The [test-only campaign-bridge safety net](../../tests/test_beta_campaign_bridge_contract.js), introduced in merged [PR #99](https://github.com/anvilspringstien/tinfoilfacup/pull/99), executes the *actual* BETA Challenges script with isolated browser storage. The [Clubfinder identity regression](../../updater/beta_campaign_identity_regression.js) also executes the actual `openChallenges(origin)` producer and checks the return snapshot. The full BETA navigation/Trophy/identity/historical workflow is now enabled for **intentional Deck HTML changes** by [PR #101](https://github.com/anvilspringstien/tinfoilfacup/pull/101), merged at `9d7e449`: production, canonical data and the independent BETA Clubfinder remain protected.

### Behaviours that must not change

1. **Campaign ownership and migration.** Keep `tffc.challengeDeck.v1` and the `accepted`, `completed`, `records` and `version` format. On old saves, migrate `journeyTies` into `tiesPlayed` and preserve already awarded beer mats; do not silently replace the save.
2. **Trusted data and isolation.** The Deck accepts only the existing `source === 'Clubfinder v7.6'` bridge. Invalid, malformed or foreign bridges must not overwrite existing saves. The backup Pigeon Name is used only with the existing matching-origin and matching-`selectedAt` rule; keep the current semantics for missing selection timestamps rather than silently tightening or loosening them.
3. **Identity and metrics.** Preserve the full 19-character `Pigeon McPigeonface` within the current 20-character field cap, its separate Call Sign, verified straight-line Pigeon Miles Flown, away ties, round and campaign-ended status. A Clubfinder → Deck → Clubfinder trip must not allocate a new search number or overwrite the canonical venue-based mileage.
4. **Awards and test controls.** `awardCampaignChallenges()` may add newly verified trophies without deleting Honour records. `applySimulationChange()` remains a BETA testing harness; ended campaigns cannot advance it. Do not call `save()` from a display-only function and create unexpected award or storage loops.
5. **Navigation and display.** Direct Challenges entry shows the first mat; already-open old Stats tabs using `stats-return-v2` can restore their saved index and clear only that token. Exit uses the deterministic `challenges-exit-v3` route and preserves unrelated session data. Keep the current truth frame, three-tap earned Trophy Cabinet, 680px iPhone Deck spacing and Pigeon Name layout unchanged.

## Proposed sequence: one independent pull request per stage

### A. Deck-side bridge reader (logic-only)

Introduce small internal, testable helpers for safely reading/parsing the Clubfinder bridge and resolving the origin/selection-matched identity backup. Leave `applyClubfinderCampaignTruth()` as the existing public entry point and keep its current state-assignment order and return value. Prefer pure normalization of input objects to mixing storage and rendering. Keep the existing storage keys and campaign-award startup sequence. Do **not** introduce a new shared JavaScript asset or network request.

**Required before merge:** add edge-case assertions for invalid numeric fields, absent backup, mismatched campaign identity, already-ended state and existing saved achievements to the #99 VM contract test. Run the complete BETA workflow and inspect the diff to ensure only `beta/challenges-beta.html` and deliberately updated tests changed. Preserve the immediate previous BETA Deck blob as a rollback target.

### B. Deck display decomposition (presentation only)

Keep a stable `renderStats()` wrapper while separating its existing three responsibilities internally: (a) Call Sign/Pigeon Name/Miles Flown/Current Round truth frame, (b) simulator counters/disabled state, and (c) Trophy Cabinet enumeration and earned-mat click targets. Do not change CSS or the element hierarchy in this PR. Keep trophy state and DOM ordering stable; reopening the Deck or finishing a challenge must refresh all three sections.

**Required before merge:** the #99 bridge contract, direct-entry and three-tap Trophy Viewer tests, with focused render-on-save/reset/ended-state assertions; desktop/iPad/iPhone 14 visual comparison if any DOM output changes. Only after that should a separate rename away from the legacy `renderStats` name be considered.

### C. Clubfinder producer (separate, high-guard BETA-only stage)

Only after A and B are green, inspect the entire ~4.6 MB `beta/clubfinder-beta.html` using an in-repository runner rather than truncated connector output. The existing producer is `openChallenges(origin)` and its related `tinFoilChallengeStatsSnapshot`, identity save/recovery and `tinFoilRestoreClubfinderReturnSnapshot` functions. Keep canonical `completedResultVenue` and Pigeon Miles calculation authoritative. Extract duplicated *pure* bridge assembly only if full-file comparison demonstrates duplication; keep the current producer function and v1 keys/shape.

**Important:** PR #101 intentionally continues to prohibit BETA Clubfinder edits in the Deck-only workflow. Before a deliberate Clubfinder BETA edit, introduce an isolated dedicated workflow/guard for that target (with the actual Clubfinder VM, mobile identity, Petts Wood, Exmouth and Weston tests), explicitly limiting changed files. No production promotion follows automatically.

### D. Optional cross-page module, only if justified

Do not create a third shared JavaScript file merely to share a few field names. First demonstrate that both pages need the same proven pure logic, that relative paths and same-origin storage work under GitHub Pages/Wix embedding, and that asset/network loading does not make the already-heavy navigation worse. If a shared module would introduce another failure mode without a measurable benefit, retain the two small page-local adapters.

## Gates and rollback after every stage

- Check current `main` and normal FA Cup ingestion **before creating a branch**. Source changes must never overwrite newer canonical `competition.json`, live `clubfinder.html` or the updater. Keep BETA's embedded offline snapshot refresh a separate, independently guarded data PR.
- Compare the exact base/head source blobs and inspect the GitHub PR diff. Run all Deck/bridge/Trophy/identity/historical tests, with the targeted new assertion appropriate to that stage; wait for a completed green GitHub Actions result rather than a queued or in-progress check.
- Save the exact merged commit, test-run URL, file blob and next target in [CURRENT.md](./CURRENT.md). If something regresses, revert that small BETA-only PR or restore its immediate predecessor, **never** replace the newer live competition data from the old accepted checkpoint.
- Reaccept on desktop, iPad and iPhone 14 before promoting any user-visible layout or navigation changes; automated VM tests do not establish browser visual acceptance.

## Kept outside this sequence

The 47 originally flagged CSS candidates are unproved textual candidates, not an approved deletion list; inspect generated markup and active simulator styles in their own PRs. Automated browser refresh remains a separate planned feature. No Challenge simulator removal, production refactor or full deployment-site migration is implied by these steps.
