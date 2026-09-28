# Generated BETA source inventory — 25 September 2026

Generated from the **full checked-out repository files**, not a truncated connector response. This is a read-only source map; regex matches identify investigation candidates, **not** proven dead code or permission to delete anything.

## Full-file source fingerprints

| File | Bytes | Lines | SHA-256 |
|---|---:|---:|---|
| `beta/clubfinder-beta.html` | 561,853 | 1,863 | `d4d9d689fe2ee17d1bd242de688f0774629025163997f4a4655423bb3e9ab8c9` |
| `beta/challenges-beta.html` | 82,344 | 1,871 | `061dea095343da1380e71b3a517b0930af1c25035b123e71bf608566163e8d0a` |
| `clubfinder.html` | 4,024,034 | 1,595 | `42eba68b60b2682a44a66a629df32fd85c55bd12c45d85db7d6a7515dee51825` |
| `competition.json` | 3,038,810 | 94,837 | `dcd3524cfc5d729824583e8a04ccbd9f24b41bb0bd3ecfce6c08553061534b41` |

## BETA structure

| Measurement | BETA Clubfinder | BETA Challenges |
|---|---:|---:|
| Embedded CSS blocks | 3 | 4 |
| Embedded CSS bytes | 15,143 | 38,838 |
| Inline JS blocks | 3 | 1 |
| Behavioural JS bytes (excluding Clubfinder embedded competition payload) | 552,600 | 36,282 |
| Named function declarations (unique) | 152 | 38 |
| Unique markup IDs | 13 | 40 |

### BETA Clubfinder named functions

`add`, `addClub`, `appendHistory`, `applyLiveRoundDates`, `buildJourney`, `candidateClubByName`, `candidateIsActive`, `canonicalClubKey`, `canonicalResultWinner`, `carrierHtml`, `certEsc`, `chooseJourney`, `clubByDisplayName`, `clubObjectForWinner`, `clubStillActive`, `competitionState`, `completedResultDateLabel`, `completedResultVenue`, `currentDisplayFixture`, `dateLabel`, `displayedRound`, `drawAlternatives`, `drawIdentityCompatible`, `endMyJourney`, `esc`, `findGround`, `finish`, `fixture`, `fixtureMapUrl`, `fixtureVenue`, `fixtureVenueText`, `fixtureVenueVerification`, `formatDateGB`, `geocodeClubPostcodes`, `go`, `groundByClubName`, `hardResetFinder`, `hav`, `historicalResultsForClub`, `iconSvg`, `journeyCertificate`, `journeyMapAction`, `journeyMapUrl`, `liveConditionalFixtureForClub`, `liveLookup`, `liveResultHistory`, `loadSavedJourney`, `lookup`, `maps`, `nextProgressHtml`, `nextRoundInfo`, `norm`, `onKey`, `openChallenges`, `parseKickoff`, `previousRoundsHtml`, `refreshCompetitionData`, `replayFixtureFor`, `replayVenue`, `resetFinder`, `resolveChain`, `resolveConditionalSide`, `resolveLiveFixtureForCarrier`, `resolveSide`, `resolvedFixture`, `resultFor`, `resultLineFromResult`, `resultLinePlain`, `resultNeedsReplay`, `resultSortValue`, `resultTeamLine`, `resumeMyJourney`, `returnToMyJourney`, `sameClubIdentity`, `sameMatchResult`, `samePostcode`, `sameSemanticResult`, `saveJourney`, `savedOrigin`, `stateActions`, `stateHtml`, `tinFoilBackfillChosenCampaignIdentity`, `tinFoilBackfillExistingCampaignIdentity`, `tinFoilBeginSearchIdentity`, `tinFoilBetaCompetitionClubKey`, `tinFoilBetaCompletedKickoff`, `tinFoilBetaHolmesdale2026Ready`, `tinFoilBetaPenaltyResultNote`, `tinFoilBetaVerifiedThameNextFixture`, `tinFoilBetaVerifiedWimborneReplay`, `tinFoilBuildChallengeBridgeRecord`, `tinFoilCallSignFromSearchNumber`, `tinFoilCampaignIdentityCandidateMatches`, `tinFoilCampaignIdentityForSave`, `tinFoilCampaignIdentityHtml`, `tinFoilCampaignIdentityInnerHtml`, `tinFoilCampaignPostcodeKey`, `tinFoilCertificateWinner`, `tinFoilChallengeRoundIndex`, `tinFoilChallengeStatsSnapshot`, `tinFoilClearCampaignIdentityBackup`, `tinFoilClearCurrentSearchIdentity`, `tinFoilConfirm`, `tinFoilCounterIncrementUrl`, `tinFoilCurrentSearchNumber`, `tinFoilDisplayDate`, `tinFoilHealthKey`, `tinFoilHealthTextHasClub`, `tinFoilIdentityStorageSnapshot`, `tinFoilIssueSearchNumber`, `tinFoilMaybeOpenCanonicalStatsRoute`, `tinFoilNormaliseSearchNumber`, `tinFoilPersistCampaignIdentityBackup`, `tinFoilPigeonCoords`, `tinFoilPigeonMilesForStats`, `tinFoilPigeonNameInputHtml`, `tinFoilRecoverCampaignIdentity`, `tinFoilRefreshCampaignIdentityDisplay`, `tinFoilRegisterPendingCampaignIdentity`, `tinFoilRenderResultHealthNotice`, `tinFoilRenderStatsFromOpener`, `tinFoilRepairStatsCustodyRows`, `tinFoilRestoreClubfinderReturnSnapshot`, `tinFoilRestoreSavedCampaignOnLoad`, `tinFoilResultHealthMatches`, `tinFoilResultHealthRenderedText`, `tinFoilResultHealthTarget`, `tinFoilSaveClubfinderReturnSnapshot`, `tinFoilSavePigeonName`, `tinFoilSavedCallSign`, `tinFoilSavedPigeonName`, `tinFoilSearchNumberDigits`, `tinFoilSearchNumberLabel`, `tinFoilSetCurrentSearchNumber`, `tinFoilStartResultHealthNotice`, `tinFoilStartStatsIntegrity`, `tinFoilStatsDisplayClubKey`, `tinFoilStatsFindRenderedRow`, `tinFoilStatsFixtureCount`, `tinFoilStatsFixtureParts`, `tinFoilStatsLeafElements`, `tinFoilStatsRepairRenderedRow`, `tinFoilStatsReturnPending`, `tinFoilStatsWinnerFromFixture`, `updateLiveDataBadge`, `updateSavedJourney`, `venueForChallenge`, `venueForResult`, `venueForStats`, `verification`, `verifiedConditionalWinner`, `viewOriginalJourneys`

### BETA Challenges named functions

`advanceTrophy`, `applyClubfinderCampaignTruth`, `applySimulationChange`, `awardCampaignChallenges`, `blankState`, `bluePeterDone`, `buildFace`, `campaignConditionMet`, `close`, `closeTrophy`, `finish`, `flipMat`, `hideVerificationHelp`, `isUnlocked`, `loadState`, `lockedMessage`, `matchingCampaignIdentityBackup`, `normalizeBridgeIdentity`, `normalizeBridgeProgress`, `onKey`, `openAt`, `openTrophy`, `preloadArt`, `preloadMatAt`, `readChallengeStorageJSON`, `render`, `renderCampaignTruthFrame`, `renderSimulatorControls`, `renderSimulatorCounters`, `renderStats`, `renderTrophyCabinet`, `save`, `showVerificationHelp`, `tinFoilConfirm`, `tinFoilReturnToClubfinder`, `verificationHelp`, `verificationLabel`, `warmChallengeArt`

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

- Snapshot comparison against checked-out canonical JSON: **MATCH**.
- Embedded timestamp: `2026-09-25T13:47:51.590346+00:00`.
- Current canonical timestamp: `2026-09-25T13:47:51.590346+00:00`.
- **Do not modify either data source as part of this report.** If stale, run the separate guarded BETA snapshot repair on a new branch; leave live competition updates intact.

## Next manual analysis

1. Cross-reference candidate function calls, DOM IDs and CSS selectors; prove no listeners/storage/legacy URLs depend on any proposed deletion.
2. Capture before/after source fingerprints for each narrow cleanup PR; pass Deck, Trophy, identity, Petts Wood, Exmouth, Weston and replay regressions.
3. Preserve the checkpoint branch `checkpoint/accepted-beta-20260925` at `89f0338e5f11f8e7a36d3bf69e57e3be88fc264f`.
