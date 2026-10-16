# Tin Foil FA Cup — approved BETA journey

**Approved:** 16 October 2026, after PRs #449–#460 (visual sign-off from the user).

## Canonical BETA entrance

- **https://tinfoilfacup.com/beta/** is the permanent, Splash-first BETA entrance (`beta/index.html`).
- **https://tinfoilfacup.com/beta/clubfinder-journey.html** contains the approved Four Laws → Findings → original BETA Campaign presentation, loaded only after Splash.
- Do not present the second URL as a normal direct-test entry: tests **start at Splash**.
- The original `beta/clubfinder-beta.html` remains the active, updateable competition engine and direct legacy BETA route, including `?stats=1`. The promoted journey fetches its **entire** live BETA document, including dynamic competition data, CSS, scripts, Campaigns, and Challenges/Stats integration. Never freeze BETA's dynamic data.
- The root `/index.html` still links to `beta/clubfinder-beta.html`, exactly as before. **This promotion does not change the live homepage's route or production `clubfinder.html`.** A separate explicit decision is required to promote the new flow to the live entrance.

## Frozen visual masters

- `two-rooms-splash-locked.html`, `two-rooms-splash-locked.css`
- `two-rooms-clubfinder.html`, `two-rooms.css`
- The accepted integration sources remain `two-rooms-splash-iframe-proof.html`, `two-rooms-iframe-engine-proof.html`, `two-rooms-iframe-engine.css`, and `two-rooms-shed-scrollbar.css` for read-only comparison/rollback.
- Permanent promoted copies: `beta/index.html`, `beta/clubfinder-journey.html`, `beta/clubfinder-journey.css`. They must remain byte-equivalent to the accepted proof except for permanent filenames, page titles, and one session marker needed to return from Challenges.
- `tests/beta-approved-journey-lock.mjs` guards the accepted original blobs and parity. Changing expected SHA values requires a **new, explicit visual approval**, not a routine test-fix.
- `tests/beta-approved-journey-browser.mjs` tests Splash-first geometry, matching three-frame widths/gaps, Frame 2 landing, Reset placeholder, across four desktop/tablet/phone viewports. CI: `beta-approved-journey.yml`.

## Preserved behaviour

1. Splash → the approved *actual* Four Laws master in its isolated same-origin iframe.
2. Find My Club → original BETA postcode search, Campaign cards and competition data.
3. Three bordered fields of the same responsive width: Four Laws, findings summary, Campaigns.
4. Every Campaign action (Find, Choose, View Original, My Campaign) scrolls to the top of the findings (Frame 2).
5. Reset/Hard Reset return to the top of Four Laws and clear the visible postcode placeholder, **without losing unrelated saved data on ordinary Reset**.
6. Desktop stable scrollbar gutter; phone/tablet natural scrolling.
7. The `tffc.beta.approved-journey` **sessionStorage-only** marker routes Challenges Exit back to `clubfinder-journey.html?from=challenges-exit-v3` when launched through the new BETA entrance. Direct/legacy BETA Challenges users still return to their original BETA URL. Stats' original `?stats=1` route and opener-based return are unchanged.

## Acceptance and rollback

**No production changes.** Before accepting a future edit, test from `/beta/` on Big Boy, iPhone and iPad; test three choices, chosen Campaign, Stats, Challenges Exit, View Original, Reset/Hard Reset and status/fixtures. Geometry CI cannot replace the visual acceptance.

Rollback the BETA promotion PR if necessary: the previous `beta/clubfinder-beta.html`, original Challenges fallback, locked masters and production entrance remain intact. Do not edit live production to roll back this BETA-only promotion.
