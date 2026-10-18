# Keep the Magic — isolated Shed preview

Entry: `/beta/keep-the-magic-shed.html` (available on the website after merge).
No existing landing page, Share iframe, Campaign, Stats, Challenges, ingestion
file or storage key is changed. This prototype is a top-level page because the
existing popup is an iframe and installation belongs to the top-level browser.

The existing Share QR and production URL are preserved. Keep the Magic opens
platform-selectable guidance with the established crest as its icon. A native
install button appears only after a real beforeinstallprompt event. Unsupported
browsers get instructions, and standalone launches get an already-open-as-app
message. Cancellation is not reported as installation success.

The manifest keeps a separate Shed app identity. Browser visits show the preview; installed launches enter the existing BETA Splash. It
must not be represented as an installed production Clubfinder. No service worker,
offline fixture caching, notifications or browser-storage writes are introduced.
The icon assets are deterministic resizes of the current Splash crest: 180px Apple,
192/512px ordinary PNG, plus a separately padded 512px maskable icon.

## Evidence and remaining acceptance

Run `python3 -m http.server 8765 --bind 127.0.0.1`, then
`node tests/keep-the-magic-shed.mjs` with Playwright and Chromium installed.
The read-only GitHub workflow installs these test dependencies and saves phone
and desktop screenshots. Tests simulate prompt dismissal, not real OS installation.

The local executor's browser download returned invalid ZIP data and its separate
cloud browser could not reach localhost. Browser verification therefore runs on
GitHub; do not describe syntax checks as visual or device acceptance.

Before promotion: inspect Share and Keep at 390x669, phone landscape, iPad and
desktop; install on physical iPhone Safari and Android; close/reopen repeatedly;
verify actual icon appearance, standalone navigation, live fixture refresh,
Campaign identity, Pigeon name, Challenges, Trophy Cabinet and mileage. Test
browser-to-installed storage boundaries and embedded-popup-to-top-level guidance.
Do not promise Campaign transfer until these pass. Installed navigation uses the existing BETA Splash/Clubfinder flow. Production
Share-popup integration remains outside this isolated test.

Guidance sources checked 18 October 2026:
- https://support.apple.com/en-gb/guide/iphone/iphea86e5236/27/ios/27
- https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeinstallprompt_event
- https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable


## Stage 2: installed Campaign entry

The existing manifest identity and start URL remain unchanged. Standalone launches
of the preview replace their location with `/beta/`, using the accepted BETA
Splash and original Clubfinder journey. Normal browser visits remain on the
preview; `?instructions=1` permits viewing guidance inside an installed app.
No existing application page, storage key, saved Campaign or counter is rewritten
by the new entry route. iPhone instructions name Safari's square-with-up-arrow
and distinguish it from our own Share button.

The browser test now enters the real BETA journey after restoring the same storage
into a new simulated-standalone browser context. It asserts the saved origin,
postcode, Pigeon name, search number, call sign and selection date survive two
entries, without a counter request. Only the postcode lookup is stubbed; competition
data and BETA restore/rendering code are real committed files. This is not proof of
Safari-to-installed storage sharing. The user's first iPhone icon installation and
preview reopening passed; real Campaign/Stats/Challenges retention remains the
next physical-device acceptance step. Never Reset/Hard Reset for these tests.

## Existing Share entry

The BETA embedded Share popup now links to the tested installation page with `target="_top"` and `?instructions=1&keep=1`. This opens Keep guidance immediately outside the iframe, including when already installed, while retaining the manifest identity and installed launch route. Back to Share returns to the top-level Share view; its QR, Copy Link and Share actions remain available. The original Clubfinder tab is navigated, and the Campaign remains in existing browser storage. No browser-to-app transfer is promised.

Physical iPhone testing confirmed repeated full-screen launches, Campaign and Pigeon-name retention, and working Stats/Challenges after reopening. Transfer of an older Safari Campaign into installed storage remains a separate unverified gate.

### Corrected application return
The embedded entry now passes an allowlisted same-origin application return URL. Back to Share and Close return to that application and reopen its existing Share popup; the separate preview Share screen is used only for standalone preview visits. Browser tests exercise both real application hosts with native sharing available at 390×560, including repeated entry and Close. Phone popup geometry reserves room for all three actions.
