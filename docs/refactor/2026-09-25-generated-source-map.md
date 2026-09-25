# Generated BETA source inventory — 25 September 2026

Generated from the **full checked-out repository files**, not a truncated connector response. This is a read-only source map; regex matches identify investigation candidates, **not** proven dead code or permission to delete anything.

## Full-file source fingerprints

| File | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `beta/clubfinder-beta.html` | 4,616,151 | 1,812 | `aef5737e7a54e66b9754c11c2796ea2586f5f70c2d4239cba9d8767d70dfb858` |
| `beta/challenges-beta.html` | 88,761 | 2,045 | `68690a7b1bd5e3d15648acb66979715fe01fb7c88fca9f0e1388c31aab23ffa7` |
| `clubfinder.html` | 4,024,034 | 1,595 | `dffced6783eac8659fb58840c14e1b782b46405e7b9dd5127ccdb3cbb25a9989` |
| `competition.json` | 3,038,810 | 94,837 | `1c40bd480f8f685c8eaca72918a25d76cf25d5a88a55f793f04a877ffa244af6` |

## BETA structure

| Measurement | BETA Clubfinder | BETA Challenges |
|---|---:|---:|
| Embedded CSS blocks | 3 | 5 |
| Embedded CSS bytes | 14,394 | 46,426 |
| Inline JS blocks | 2 | 1 |
| Behavioural JS bytes (excluding Clubfinder embedded competition payload) | 2,400,766 | 35,096 |
| Named function declarations (unique) | 150 | 30 |
| Unique markup IDs | 13 | 40 |

### BETA Clubfinder named functions

`add`, `addClub`, `appendHistory`, `applyLiveRoundDates`, `buildJourney`, `candidateClubByName`, `candidateIsActive`, `canonicalClubKey`, `canonicalResultWinner`, `carrierHtml`, `certEsc`, `chooseJourney`, `clubByDisplayName`, `clubObjectForWinner`, `clubStillActive`, `competitionState`, `completedResultDateLabel`, `completedResultVenue`, `currentDisplayFixture`, `dateLabel`, `displayedRound`, `drawAlternatives`, `drawIdentityCompatible`, `endMyJourney`, `esc`, `findGround`, `finish`, `fixture`, `fixtureMapUrl`, `fixtureVenue`, `fixtureVenueText`, `fixtureVenueVerification`, `formatDateGB`, `geocodeClubPostcodes`, `go`, `groundByClubName`, `hardResetFinder`, `hav`, `historicalResultsForClub`, `iconSvg`, `journeyCertificate`, `journeyMapAction`, `journeyMapUrl`, `liveConditionalFixtureForClub`, `liveLookup`, `liveResultHistory`, `loadSavedJourney`, `lookup`, `maps`, `nextProgressHtml`, `nextRoundInfo`, `norm`, `onKey`, `openChallenges`, `parseKickoff`, `previousRoundsHtml`, `refreshCompetitionData`, `replayFixtureFor`, `replayVenue`, `resetFinder`, `resolveChain`, `resolveConditionalSide`, `resolveLiveFixtureForCarrier`, `resolveSide`, `resolvedFixture`, `resultFor`, `resultLineFromResult`, `resultLinePlain`, `resultNeedsReplay`, `resultSortValue`, `resultTeamLine`, `resumeMyJourney`, `returnToMyJourney`, `sameClubIdentity`, `sameMatchResult`, `samePostcode`, `sameSemanticResult`, `saveJourney`, `savedOrigin`, `stateActions`, `stateHtml`, `tinFoilBackfillChosenCampaignIdentity`, `tinFoilBackfillExistingCampaignIdentity`, `tinFoilBeginSearchIdentity`, `tinFoilBetaCompetitionClubKey`, `tinFoilBetaCompletedKickoff`, `tinFoilBetaHolmesdale2026Ready`, `tinFoilBetaPenaltyResultNote`, `tinFoilBetaVerifiedThameNextFixture`, `tinFoilBetaVerifiedWimborneReplay`, `tinFoilCallSignFromSearchNumber`, `tinFoilCampaignIdentityCandidateMatches`, `tinFoilCampaignIdentityForSave`, `tinFoilCampaignIdentityHtml`, `tinFoilCampaignIdentityInnerHtml`, `tinFoilCampaignPostcodeKey`, `tinFoilCertificateWinner`, `tinFoilChallengeRoundIndex`, `tinFoilChallengeStatsSnapshot`, `tinFoilClearCampaignIdentityBackup`, `tinFoilClearCurrentSearchIdentity`, `tinFoilConfirm`, `tinFoilCounterIncrementUrl`, `tinFoilCurrentSearchNumber`, `tinFoilDisplayDate`, `tinFoilHealthKey`, `tinFoilHealthTextHasClub`, `tinFoilIdentityStorageSnapshot`, `tinFoilIssueSearchNumber`, `tinFoilMaybeOpenCanonicalStatsRoute`, `tinFoilNormaliseSearchNumber`, `tinFoilPersistCampaignIdentityBackup`, `tinFoilPigeonCoords`, `tinFoilPigeonMilesForStats`, `tinFoilPigeonNameInputHtml`, `tinFoilRecoverCampaignIdentity`, `tinFoilRefreshCampaignIdentityDisplay`, `tinFoilRegisterPendingCampaignIdentity`, `tinFoilRenderResultHealthNotice`, `tinFoilRepairStatsCustodyRows`, `tinFoilRestoreClubfinderReturnSnapshot`, `tinFoilRestoreSavedCampaignOnLoad`, `tinFoilResultHealthMatches`, `tinFoilResultHealthRenderedText`, `tinFoilResultHealthTarget`, `tinFoilSaveClubfinderReturnSnapshot`, `tinFoilSavePigeonName`, `tinFoilSavedCallSign`, `tinFoilSavedPigeonName`, `tinFoilSearchNumberDigits`, `tinFoilSearchNumberLabel`, `tinFoilSetCurrentSearchNumber`, `tinFoilStartResultHealthNotice`, `tinFoilStartStatsIntegrity`, `tinFoilStatsDisplayClubKey`, `tinFoilStatsFindRenderedRow`, `tinFoilStatsFixtureCount`, `tinFoilStatsFixtureParts`, `tinFoilStatsLeafElements`, `tinFoilStatsRepairRenderedRow`, `tinFoilStatsReturnPending`, `tinFoilStatsWinnerFromFixture`, `updateLiveDataBadge`, `updateSavedJourney`, `venueForChallenge`, `venueForResult`, `venueForStats`, `verification`, `verifiedConditionalWinner`, `viewOriginalJourneys`

### BETA Challenges named functions

`advanceTrophy`, `applyClubfinderCampaignTruth`, `applySimulationChange`, `awardCampaignChallenges`, `blankState`, `bluePeterDone`, `buildFace`, `campaignConditionMet`, `close`, `closeTrophy`, `finish`, `flipMat`, `hideVerificationHelp`, `isUnlocked`, `loadState`, `lockedMessage`, `onKey`, `openAt`, `openTrophy`, `preloadArt`, `preloadMatAt`, `render`, `renderStats`, `save`, `showVerificationHelp`, `tinFoilConfirm`, `tinFoilReturnToClubfinder`, `verificationHelp`, `verificationLabel`, `warmChallengeArt`

### Storage key candidates (string scan; validate each read/write before editing)

**Clubfinder:** `tffc.challengeOrigin`, `tffc.clubfinderCampaign.v1`, `tffc.clubfinderCampaignIdentity.v1`, `tffc.clubfinderReturnSnapshot.v1`, `tffc.openStatsOnReturn`

**Challenges:** `tffc.challengeDeck.v1`, `tffc.challengeOrigin`, `tffc.challengeReturnIndex`, `tffc.clubfinderCampaign.v1`, `tffc.clubfinderCampaignIdentity.v1`

### Investigation candidates (presence only)

- Challenge `renderStats` declaration: **True**; separate Challenges Stats UI was removed by PR #84. Follow its references before removing.
- Challenge simulator `applySimulationChange`: **True**; preserve until an independent test mechanism is proved.
- Trophy inspection `openTrophy`: **True**; preserve the three-tap experience.
- BETA Clubfinder `refreshCompetitionData`: **True**; preserve canonical live fetch and offline fallback.
- 680px mobile breakpoint detected: Clubfinder **True**, Challenges **True**.

## Embedded competition fallback freshness

- Snapshot comparison against checked-out canonical JSON: **STALE**.
- Embedded timestamp: `2026-09-25T07:49:01.065159+00:00`.
- Current canonical timestamp: `2026-09-25T12:45:37.316822+00:00`.
- **Do not modify either data source as part of this report.** If stale, run the separate guarded BETA snapshot repair on a new branch; leave live competition updates intact.

## Next manual analysis

1. Cross-reference candidate function calls, DOM IDs and CSS selectors; prove no listeners/storage/legacy URLs depend on any proposed deletion.
2. Capture before/after source fingerprints for each narrow cleanup PR; pass Deck, Trophy, identity, Petts Wood, Exmouth, Weston and replay regressions.
3. Preserve the checkpoint branch `checkpoint/accepted-beta-20260925` at `89f0338e5f11f8e7a36d3bf69e57e3be88fc264f`.
