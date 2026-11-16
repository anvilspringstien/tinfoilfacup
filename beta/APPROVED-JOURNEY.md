# Tin Foil FA Cup — approved BETA journey

**Approved:** 16 October 2026, after PRs #449–#460 (visual sign-off from the user).

## Public front door and canonical BETA entrance

- **https://tinfoilfacup.com/** is the official public front door (`/index.html`), now showing the byte-for-byte approved Splash body with root-correct image/button paths, while preserving canonical and social-sharing metadata.
- **https://tinfoilfacup.com/beta/** remains the independent, permanent Splash-first BETA entrance (`beta/index.html`). It is the reference and rollback route.
- **https://tinfoilfacup.com/beta/clubfinder-journey.html** contains the approved Four Laws → Findings → original BETA Campaign presentation, loaded only after Splash.
- Do not present the second URL as a normal direct-test entry: tests **start at Splash**.
- The original `beta/clubfinder-beta.html` remains the active, updateable competition engine and direct legacy BETA route, including `?stats=1`. The promoted journey fetches its **entire** live BETA document, including dynamic competition data, CSS, scripts, Campaigns, and Challenges/Stats integration. Never freeze BETA's dynamic data.
- The root `/index.html` now links to `beta/clubfinder-journey.html`. The old root design was replaced in a separate, explicitly approved promotion after BETA sign-off. **Production `clubfinder.html` and the updateable original BETA `beta/clubfinder-beta.html` remain unchanged**, as do the ingestion machinery and competition datasets.

## Frozen visual masters

- `two-rooms-splash-locked.html`, `two-rooms-splash-locked.css`
- `two-rooms-clubfinder.html`, `two-rooms.css`
- The accepted integration sources remain `two-rooms-splash-iframe-proof.html`, `two-rooms-iframe-engine-proof.html`, `two-rooms-iframe-engine.css`, and `two-rooms-shed-scrollbar.css` for read-only comparison/rollback.
- Permanent promoted copies: `beta/index.html`, `beta/clubfinder-journey.html`, `beta/clubfinder-journey.css`. They must remain byte-equivalent to the accepted proof except for permanent filenames, page titles, and one session marker needed to return from Challenges.
- `tests/beta-approved-journey-lock.mjs` guards the accepted original blobs and parity. Changing expected SHA values requires a **new, explicit visual approval**, not a routine test-fix.
- `tests/beta-approved-journey-browser.mjs` tests **public and BETA** Splash-first geometry, matching three-frame widths/gaps, Frame 2 landing, Reset placeholder, across four desktop/tablet/phone viewports. CI: `beta-approved-journey.yml` (now watches root `index.html` too).

## Preserved behaviour

1. Splash → the approved *actual* Four Laws master in its isolated same-origin iframe.
2. Find My Club → original BETA postcode search, Campaign cards and competition data.
3. Three bordered fields of the same responsive width: Four Laws, findings summary, Campaigns.
4. Every Campaign action (Find, Choose, View Original, My Campaign) scrolls to the top of the findings (Frame 2).
5. Reset/Hard Reset return to the top of Four Laws and clear the visible postcode placeholder, **without losing unrelated saved data on ordinary Reset**.
6. Desktop stable scrollbar gutter; phone/tablet natural scrolling.
7. The `tffc.beta.approved-journey` **sessionStorage-only** marker routes Challenges Exit back to `clubfinder-journey.html?from=challenges-exit-v3` when launched through the new BETA entrance. Direct/legacy BETA Challenges users still return to their original BETA URL. Stats' original `?stats=1` route and opener-based return are unchanged.

## Acceptance and rollback

**The public homepage `index.html` is now promoted and guarded.** Before accepting future edits, start from both `/` (public) and `/beta/` (reference) on Big Boy, iPhone and iPad; test three choices, chosen Campaign, Stats, Challenges Exit, View Original, Reset/Hard Reset and status/fixtures. Geometry CI cannot replace the visual acceptance.

If the public front door has a regression, revert **only the public homepage promotion PR** to restore the former root entry; keep the validated `/beta/` journey available. For a BETA regression, revert the earlier BETA promotion separately; its original `beta/clubfinder-beta.html` and locked masters remain intact. Do not modify the live competition scanner or production `clubfinder.html` as part of either rollback.
