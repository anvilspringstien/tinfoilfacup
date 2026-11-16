# Keep the Magic

The installed identity and entry remain `/beta/keep-the-magic-shed` and
`/beta/keep-the-magic-shed.html`. The manifest, icon, approved Splash and
competition machinery are unchanged. Browser visits show Share/Keep guidance;
installed launches enter `/beta/`, then the existing Clubfinder journey.
Share/Keep close returns to the originating view; Back returns to Share.

## Browser to Home Screen handover

The first full physical iPhone cycle on 20 October exposed the storage boundary:
Campaign #01755, Pigeon Checky and Challenge progress were in browser localStorage,
while the installed app started empty and allocated #01756. The earlier test
reopened already-populated localStorage; it did not exercise installation.

WebKit documents that iOS/iPadOS 17.2+ copies cookies when creating a Home Screen
app, but does not copy localStorage:
https://webkit.org/blog/14787/webkit-features-in-safari-17-2/#web-apps

Opening Keep now prepares a compressed snapshot of the four existing allowlisted
Campaign/Challenge keys. The snapshot uses at most two first-party cookies,
under 6KB total, scoped to the installed entry path, with a seven-day expiry.
Cookies accompany requests to that entry path; the payload is not placed in
Share links, QR codes, the manifest or other site URLs. This is an installation
snapshot, not ongoing synchronisation between the app and browser.

On first standalone launch the page remains hidden until the snapshot is
validated and restored into empty localStorage. Successful transfer consumes
the cookies before entering Splash. Any existing Campaign/Challenge key in the
installed app takes precedence: stale cookies never overwrite later progress.
Malformed, incomplete, expired or failed writes do not permit a partial restore
or silently start a fresh Campaign. A failed launch explains how to return to
the browser. An oversized history or blocked preparation offers the existing
backup/restore page rather than dropping Challenge history to fit.

## Automated evidence

- `node tests/keep-the-magic-regression.js`: allowlisted backups and restore.
- `node tests/keep-magic-install-regression.js`: cookie-only transfer, exact
  record preservation, existing progress, corruption, missing chunks, expiry,
  quota rollback, size limits and blocked cookies.
- `node tests/keep-the-magic-shed.mjs`: actual Share/Keep navigation and geometry;
  real Campaign/Challenges save, then a new context receiving cookies only,
  starting with empty localStorage. Checks Checky, #01755, Cabinet awards and
  mileage through the real application, repeat launch and zero new counters.

The GitHub preview workflow runs these checks and captures phone/desktop images.
It also runs the isolated cookies-only handover in WebKit, in addition to Chromium.
Browser contexts model the documented storage boundary; they do not automate
Apple's installation sheet or prove physical OS cookie copying.

## Device acceptance

Use the original browser Campaign, remove the test icon and add it again through
Share > Keep. Do not hard reset the original browser Campaign. The already-created
#01756 app has its own progress and is deliberately not overwritten automatically.
Verify #01755, Checky, four Cabinet mats, 0766 miles and Fourth Qualifying after
Start Campaign, plus Stats, Challenges and repeated icon launches. Until this
physical cycle passes, describe transfer as awaiting device acceptance.

No service worker, fixture cache, notifications or competition data edits are
introduced. Unsupported browser/version cookie copying remains a device limit;
the existing private backup/restore page is the manual alternative.
