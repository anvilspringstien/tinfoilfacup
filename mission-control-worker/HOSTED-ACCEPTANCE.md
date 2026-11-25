# Mission Control Phase 2C.4 hosted acceptance

The target is the existing [Radar TEST Worker](https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/). This PR prepares it for a controlled acceptance window. Upload, traffic changes and rollback are owner operations performed only within a separately authorised window.

## Custody and target

| Item | Baseline |
| --- | --- |
| GitHub source | PR [#740](https://github.com/anvilspringstien/tinfoilfacup/pull/740) merged as `e960ca36d830977e2a47955985243a23005a6bb9`. |
| Cloudflare Worker | `tffac-mission-control-radar-test` |
| Historical source | `271cbcc5`, before the dedicated credential configuration. Historical reference only. |
| Currently serving version and traffic | **Unverified**. Read and record the full current version ID and percentage from the authenticated account. Those values are required for rollback. |
| Latest upload | **Unverified**. It may differ from the serving version. Inspect before uploading any candidate. |
| Runtime | Compatibility date `2026-11-21`, no flags, Default placement, cache disabled, as supplied by the owner. Verify settings against Cloudflare before upload. |
| OAuth | Dedicated test client. Exact callback `https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/oauth/callback`. The owner verified fresh Chrome Incognito sign-in on the existing configuration. |
| Secret binding names | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SESSION_SECRET`, `GITHUB_RADAR_TOKEN`. Verify names and types only. Keep the installed test client and independent signing secret. |
| Service | `OMBUDSMAN_SERVICE` → `tffc-ombudsman`, default entrypoint. With `OMBUDSMAN_STATUS_TOKEN` absent, the candidate reports the feed unavailable and skips the service call. |

The [explicit Wrangler target](wrangler.radar-test.toml) builds from the reviewed `worker.mjs` into a git-ignored directory. The [builder](build-radar-test.mjs) stops when an expected integration point changes. The candidate pins the Radar test origin, labels both sign-in and dashboard pages **TEST**, and keeps the existing Google dashboard sign-in checks and `openid email` scopes. The authenticated test form issues a short-lived, synthetic grant bound to the dashboard session. Gmail requests use the [local synthetic transport](test/hosted-gmail-fixture.mjs) through the same parser, pagination, audit, status and Disconnect logic. The generated Worker has no Gmail OAuth handler or Gmail network fallback. Radar remains a read-only GitHub integration.

## Preflight and rollback baseline

Use a clean checkout of the approved commit from the repository root. Use the owner's existing authenticated Cloudflare session and verify the selected account. The commands below assume a POSIX shell, Node 24 and the pinned Wrangler release. Use the explicit target for every Wrangler command.

```sh
radar() {
  WRANGLER_SEND_METRICS=false npx --yes wrangler@4.156.1 "$@" \
    --cwd mission-control-worker --config wrangler.radar-test.toml
}
git rev-parse HEAD
git status --short
(cd mission-control-worker && sha256sum --check SHA256SUMS)
node --test mission-control-worker/worker.test.mjs
TFFAC_MC_TEST_TARGET=isolated node --test mission-control-worker/worker.test.mjs
node --test mission-control-worker/test/hosted-target.test.mjs
radar versions upload --dry-run
radar deployments status --json
radar deployments list --json
radar versions list --json
radar secret list
```

Record the full currently serving version ID, deployment ID, traffic percentage, latest uploaded version ID and the observed time in the acceptance record. Use the authenticated dashboard to confirm routes, preview settings, cache and placement, and the approved redirect URI in the Google test client. Keep output private if it includes account or binding metadata. Omit all credentials, codes, cookies, mailbox details and raw CLI output from the PR.

Proceed only with one confirmed post-credential baseline at 100%, the expected host and settings, and a verified rollback version that includes the dedicated configuration. If the deployment is split, the most recent upload differs from the serving baseline, any settings drift, or the baseline is unavailable, stop for owner reconciliation. Use `radar versions view "$RADAR_ROLLBACK_VERSION"` to inspect the confirmed version. The short historical source reference is insufficient for this gate.

## Upload and serving traffic

After specific upload authorisation, set `RADAR_ROLLBACK_VERSION` to the recorded full ID, then upload a separately versioned candidate from the reviewed checkout:

```sh
radar versions view "$RADAR_ROLLBACK_VERSION"
radar deployments status --json
radar versions upload --message "Mission Control Phase 2C.4 synthetic Gmail acceptance $(git rev-parse --short HEAD)"
radar versions list --json
radar deployments status --json
```

Record the full uploaded ID as `RADAR_CANDIDATE_VERSION`. Use `radar versions view "$RADAR_CANDIDATE_VERSION"` to compare binding **names and types**, compatibility and placement with the approved baseline. Confirm the existing version still serves 100%. The upload uses the installed encrypted bindings. Supply no secrets file, preview alias, route override, new binding or settings command. Use the exact registered test hostname for the browser session.

After separate authorisation to serve the candidate, confirm the full test version in Wrangler's interactive prompt:

```sh
radar versions deploy "${RADAR_CANDIDATE_VERSION}@100" --message "Mission Control Phase 2C.4 controlled hosted acceptance"
radar deployments status --json
```

Use the window for testing only. Record outcomes and restore the known-good version at the end of the window or immediately after a stop condition:

```sh
radar rollback "$RADAR_ROLLBACK_VERSION" --message "Restore verified post-credential Radar test baseline"
radar deployments status --json
```

Verify the recorded version is back at 100%, the original test gate still requires authentication, and fresh Incognito sign-in works. Close the temporary browser session after recording results. Rollback changes the serving Worker version. Browser-local test state is disposable and is reset separately.

## Hosted browser acceptance

Use a fresh Chrome Incognito window for the Radar host and two tabs in that same window for shared-cookie tests. A separate browser profile can check isolation if needed. Sign in to the dashboard using the already approved Google identity and test client. When using the Outreach connection link, the page must say **Connect synthetic Gmail**. Stop immediately if any Gmail consent, live redirect, live data or unexpected binding appears.

| Check | Action and expected result |
| --- | --- |
| Host, OAuth and TEST identity | Confirm the exact test hostname, protected initial page, the dedicated callback and **TEST** in the tab title and dashboard. An unauthenticated API request is denied. Preview and alternate origins are covered in the automated suite. |
| First count and true zero | Start with **Clear Data** on the test origin. Run **Unresolved introduction** first and expect **Unknown** with an unresolved status. Run **Complete zero** and expect a current zero and timestamp. |
| Complete, stale and partial | Run **Complete scan** and expect two unique clubs after both query families, deduplication and reply exclusion. Reload and confirm the retained aggregate. Run **Unresolved introduction**, **Provider rate limit**, **Provider permission error** and **Simulated network failure**. Expect distinct statuses and the saved count and timestamp retained. **Partial drafts** must leave a complete contacted count with drafts unknown. |
| Session versus grant expiry | Use **Synthetic grant expires after 20 seconds** or **Provider rejects the synthetic grant**. After expiry or rejection, refresh and check that Gmail reconnection is offered and the saved count is stale. For dashboard expiry, leave the test window until the one-hour session expires, or delete only the test session cookie using DevTools. Refresh from the existing page and expect Mission Control sign-in guidance. Cookie deletion simulates the absent-session response. |
| Disconnect and shared state | Open two tabs with a completed count. Disconnect in tab A and check its confirmation and preserved dashboard session. Refresh or reload tab B and check disconnected status and the stale count. Reconnect in tab B, refresh tab A and verify both can run a new synthetic scan. An idle tab reflects the most recent check until refreshed. |
| In-flight success | Start a **Slow successful scan** in tab A. Disconnect before it finishes, then repeat with Disconnect in tab B. Tab A's own Disconnect must discard obsolete results. With two tabs, check whether an older completion updates the display or saved aggregate after Disconnect, and whether Clear Data in one tab is undone by the other. Older scans crossing a shared connection or Clear Data boundary are stop conditions for release. |
| In-flight provider rejection | Start **Slow rejected grant** in tab A. Select **Complete scan** in tab B while A's request is pending. Observe the late 401 in A, then check B's status and grant after the response. If the new grant was cleared, stop. The local regression confirms the older response still emits a cookie deletion for the shared grant name. |
| Radar and Ombudsman | Verify Radar reads an existing successful main-branch artifact and shows provenance. A missing or expired artifact should be reported as unavailable. The Ombudsman feed must report unavailable because the status token is absent. Do not add the token. |
| Workspace and closure | Add a synthetic local workspace item and verify reload. Clear Data resets the browser-local workspace and saved count. Record the tested version, outcomes and any exceptions, then restore and verify the post-credential baseline. |

The automated hosted tests use synthetic sessions and model responses and cookie changes. They do not exercise Google consent, real Cloudflare routing, actual browser cross-tab cookie application or true mailbox contents. The existing in-page cancellation protects a single tab. A shared-cookie response and the browser's local storage can outlive a different tab's action. Record those cases explicitly and hold any live promotion if they reproduce.

References: [Cloudflare versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/), [Wrangler Worker commands](https://developers.cloudflare.com/workers/wrangler/commands/workers/), and [Wrangler configuration and encrypted bindings](https://developers.cloudflare.com/workers/wrangler/configuration/).
