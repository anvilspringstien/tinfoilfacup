# Two Rooms → Campaigns: doorway audit (16 October 2026)

Read-only investigation. The approved Two Rooms geometry and furniture are frozen. iPad landscape inner scrolling is accepted for now. No production, competition, or scanner changes.

## Confirmed code paths
- `beta/two-rooms-splash.html` links to `two-rooms-clubfinder.html`.
- `beta/two-rooms-clubfinder.html` Find My Club only changes a status label: **no search yet**.
- `beta/clubfinder-beta.html` function `go(explicitPostcodeSearch=false,scrollAfterRender=explicitPostcodeSearch)` (around line 2334) ensures competition data, validates `#postcode`, calls `lookup(pc)`, geocodes and ranks eligible clubs, then renders three nearest Campaigns.
- Only `go(true)` invokes `tinFoilBeginSearchIdentity()`. Existing Find My Club click and Enter key invoke `go(true)` (around line 2460).
- `chooseJourney(name,postcode)` (around line 1806) checks whether an existing Campaign is being replaced, confirms if needed, saves the Campaign, then calls `go(false,true)`.
- Saved Campaigns use `tinFoilFACupJourney_v7`; the existing BETA engine also owns identity backups and return snapshots. Restore on load uses `go(false)`, not an explicit search.
- Existing Campaign navigation includes My Campaign, My Stats, My Challenges, View Original Campaigns, Reset and Hard Reset.

## Non-negotiable boundary
Do not duplicate postcode lookup, nearest-club selection, Campaign rendering, counter allocation, or storage writes in Two Rooms. Do not assume a query-string postcode is already supported: the inspected BETA code reads the form input and its own click handler. Distinguish fresh explicit searches from refreshes, saved-Campaign restoration, and Stats/Challenges returns.

## Proposed next proof (separate from locked rooms)
Build an opt-in BETA doorway proof with a narrow, one-time handover contract to the **existing** BETA engine. Compare same-document reveal versus page navigation before committing to the final transition. No production modifications.

## Acceptance gates
1. Valid/invalid postcode parity with existing BETA; three nearest choices.
2. Exactly one search identity per explicit search; none on refresh, restore, Campaign choice or return.
3. Saved club, postcode, call sign, pigeon name, replacement confirmation and navigation preserved.
4. iPhone keyboard/Enter and Frame 2 return position preserved.
5. Seven-viewport shared geometry green; no furniture changes.
6. Visual check iPhone, Big Boy Chrome/DDG, iPad portrait/landscape.

## Design decision still open
Should Campaign choices appear below the Mean Machine within the same document, or should the user cross to the existing BETA Campaign page? Validate the doorway visually in the Shed first.
