# BETA dependency map — 25 September 2026

**Historical, commit-scoped audit.** Generated from full checked-out files by `updater/map_beta_dependencies.py`. Counts are static textual observations, **not** proof of dead code. No functional files or live competition data are written.

## Full-source fingerprints and structural size

| File | Bytes | SHA-256 | Named function declarations | Direct storage operations | CSS class tokens |
|---|---:|---|---:|---:|---:|
| `beta/challenges-beta.html` | 82,053 | `5721847c77b9d57f15ca26abdd8dcbbb031989078e55eab5c7bdb489c6d6ab24` | 30 | 8 | 116 |
| `beta/clubfinder-beta.html` | 4,616,151 | `aef5737e7a54e66b9754c11c2796ea2586f5f70c2d4239cba9d8767d70dfb858` | 150 | 15 | 86 |

## Cross-page browser-storage contracts

Direct calls resolve simple quoted constant aliases; indirect helpers, computed keys and dynamic markup require manual review.

| Key | Deck observed access | Clubfinder observed access |
|---|---|---|
| `tffc.challengeDeck.v1` | `localStorage.getItem`, `localStorage.removeItem`, `localStorage.setItem` | No direct match |
| `tffc.clubfinderCampaign.v1` | `localStorage.getItem` | `localStorage.removeItem`, `localStorage.setItem` |
| `tffc.clubfinderCampaignIdentity.v1` | `localStorage.getItem` | `localStorage.removeItem`, `localStorage.setItem` |
| `tffc.clubfinderReturnSnapshot.v1` | No direct match | `sessionStorage.getItem`, `sessionStorage.setItem` |
| `tffc.challengeOrigin` | `sessionStorage.removeItem` | `sessionStorage.setItem` |
| `tffc.challengeReturnIndex` | `sessionStorage.getItem`, `sessionStorage.removeItem` | No direct match |
| `tffc.openStatsOnReturn` | No direct match | `sessionStorage.getItem`, `sessionStorage.removeItem` |

### Behavioural compatibility requirements

| Contract | Static audit |
|---|---|
| Deck persists existing v1 challenge saves | Present |
| Deck reads Clubfinder campaign bridge | Present |
| Deck has conditional identity-backup recovery | Present |
| Deck migrates legacy journeyTies | Present |
| Deck retains old Stats-tab return index | Present |
| Deck returns through explicit Clubfinder route | Present |
| Deck keeps live progress renderer | Present |
| Clubfinder names the campaign bridge | Present |
| Clubfinder has Challenge entry function | Present |

### Producer and consumer entry points

**Clubfinder bridge / return and identity functions:** `openChallenges` (line 1520), `tinFoilChallengeStatsSnapshot` (line 1503), `tinFoilCampaignIdentityForSave` (line 1330), `tinFoilPersistCampaignIdentityBackup` (line 1190), `tinFoilRecoverCampaignIdentity` (line 1204), `tinFoilSavePigeonName` (line 1165), `tinFoilRestoreClubfinderReturnSnapshot` (line 1367)

**Deck saved state / bridge / render / return:** `blankState` (line 1336), `loadState` (line 1339), `save` (line 1363), `applyClubfinderCampaignTruth` (line 1368), `awardCampaignChallenges` (line 1409), `isUnlocked` (line 1419), `renderStats` (line 1729), `openTrophy` (line 1568), `advanceTrophy` (line 1595), `applySimulationChange` (line 1771), `tinFoilReturnToClubfinder` (line 1635)

The campaign bridge carries counters, away ties, pigeon miles, current round and identity; the Deck falls back to an origin-and-selection matched identity backup when the bridge lacks the Pigeon Name. The Deck migrates prototype journeyTies on read. Keep those data and compatibility boundaries intact before any code split.

## Deck named function reference index

The counts below include textual references in the inline script, **excluding the declaration** for the middle column. The final column counts call-shaped expressions and includes the declaration. Do not classify a function as dead from a low number alone.

| Function | Other token references | Call-shaped occurrences |
|---|---:|---:|
| `advanceTrophy` | 2 | 2 |
| `applyClubfinderCampaignTruth` | 2 | 3 |
| `applySimulationChange` | 10 | 11 |
| `awardCampaignChallenges` | 3 | 4 |
| `blankState` | 3 | 4 |
| `bluePeterDone` | 0 | 1 |
| `buildFace` | 2 | 3 |
| `campaignConditionMet` | 5 | 6 |
| `close` | 2 | 3 |
| `closeTrophy` | 3 | 4 |
| `finish` | 4 | 5 |
| `flipMat` | 3 | 4 |
| `hideVerificationHelp` | 5 | 5 |
| `isUnlocked` | 4 | 5 |
| `loadState` | 1 | 2 |
| `lockedMessage` | 6 | 7 |
| `onKey` | 2 | 1 |
| `openAt` | 1 | 2 |
| `openTrophy` | 1 | 2 |
| `preloadArt` | 3 | 4 |
| `preloadMatAt` | 7 | 8 |
| `render` | 10 | 11 |
| `renderStats` | 7 | 8 |
| `save` | 7 | 7 |
| `showVerificationHelp` | 3 | 2 |
| `tinFoilConfirm` | 2 | 3 |
| `tinFoilReturnToClubfinder` | 2 | 3 |
| `verificationHelp` | 1 | 2 |
| `verificationLabel` | 1 | 2 |
| `warmChallengeArt` | 2 | 1 |

## CSS dependency candidates

Deck CSS contains 116 distinct class tokens; 47 lack an exact whole-word occurrence in static markup or inline JS. This is only a candidate scan: computed class names, template-generated markup, pseudo-classes and third-party code can produce false positives.

First 24 candidate names: `actions`, `app`, `beta-badge`, `beta-console-head`, `beta-face`, `beta-hardware`, `beta-panel-label`, `campaign-status`, `challenge-btn`, `challenge-launch`, `challenges-btn`, `giant-kill-sim`, `hw-away`, `hw-away-count`, `hw-feedback`, `hw-home`, `hw-hotspot`, `hw-odo`, `hw-pigeon`, `hw-reset`, `hw-round`, `hw-state`, `hw-ties`, `lab-title`

Preserve the active 680px iPhone Deck height rule, the Call Sign / Pigeon Name / Miles Flown frame, and the three-tap Trophy Cabinet. Treat all further CSS deletions as independent, tested PRs.

## Offline fallback freshness at this source revision

STALE; embedded 2026-09-25T07:49:01.065159+00:00; canonical 2026-09-25T13:47:51.590346+00:00. Live ../competition.json remains authoritative.

## Dependency-safe next steps

1. Preserve prototype migration, v1 storage keys, campaign-origin/date matching, explicit Challenges return and old Stats-tab return; extend regression tests before renaming or extracting their implementations.
2. Keep the currently active renderer named renderStats despite its legacy name until call sites and tests are updated together. It powers the truth frame, simulator and Trophy Cabinet.
3. Do not remove the simulator, its DOM or its callbacks until a separate verified campaign-progression harness exists.
4. Review any zero-textual-reference CSS candidate manually against generated markup, selectors and browser behaviours before selecting a small reversible cleanup.
5. Refresh the embedded offline snapshot in a separate guarded PR if a strict current-canonical fallback check is required. Never bundle large competition-data churn with a structural refactor.
