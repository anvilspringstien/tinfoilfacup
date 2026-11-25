# Mission Control Radar TEST hosted acceptance

The target is the existing [Radar TEST Worker](https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/). This PR prepares it for a controlled acceptance window. Upload, traffic changes and rollback are owner operations performed only within a separately authorised window.

## Custody and target

| Item | Baseline |
| --- | --- |
| GitHub source | PR [#741](https://github.com/anvilspringstien/tinfoilfacup/pull/741) merged as `2a93526aa27b0ea39e1bcf3b40720d8fff2fdf8e`. |
| Cloudflare Worker | `tffac-mission-control-radar-test` |
| Serving version, owner observation on 25 November 2026 | `271cbcc5-737e-4ec5-ac9f-4560fe96f805` at 100%. This is the original version used by previous successful sign-ins. |
| Latest upload, owner observation on 25 November 2026 | `54793580-0f82-441c-970a-4b9997ba4de0`, staged with no traffic. It has yet to pass hosted sign-in. |
| Staged credential changes, in order | `63bc39a1` updated `GOOGLE_CLIENT_ID`, `e665aa81` updated `GOOGLE_CLIENT_SECRET`, and `54793580` updated `SESSION_SECRET`. Verify the cumulative binding names and the exact test callback in the owner dashboard before activation. |
| Runtime | Compatibility date `2026-11-21`, no flags, Default placement, cache disabled, as supplied by the owner. Verify settings against Cloudflare before upload. |
| OAuth | Dedicated test client. Exact callback `https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/oauth/callback`. The previous Incognito sign-in verified the original serving version. The staged test client and signing configuration still require an independent Incognito sign-in after activation. |
| Secret binding names | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SESSION_SECRET`, `GITHUB_RADAR_TOKEN`. Verify names and types only. Keep the installed test client and independent signing secret. |
| Service | `OMBUDSMAN_SERVICE` → `tffc-ombudsman`, default entrypoint. With `OMBUDSMAN_STATUS_TOKEN` absent, the candidate reports the feed unavailable and skips the service call. |

The [explicit Wrangler target](wrangler.radar-test.toml) builds from the reviewed `worker.mjs` into a git-ignored directory. The [builder](build-radar-test.mjs) stops when an expected integration point changes. The candidate pins the Radar test origin, labels both sign-in and dashboard pages **TEST**, and keeps the existing Google dashboard sign-in checks and `openid email` scopes. The authenticated test form issues a short-lived, synthetic grant bound to the dashboard session. Gmail requests use the [local synthetic transport](test/hosted-gmail-fixture.mjs) through the same parser, pagination, audit, status and Disconnect logic. The generated Worker has no Gmail OAuth handler or Gmail network fallback. Radar remains a read-only GitHub integration.

## Read-only deployment inspection

The owner has already recorded the serving and staged versions through their Cloudflare dashboard. Recheck both immediately before any approved activation. There is no need to authorise Wrangler OAuth for this read-only check.

If the owner separately approves API inspection, Cloudflare documents an API token with **Metadata Read-Only** scoped to **Individual Workers**, selecting only `tffac-mission-control-radar-test`. Both inventory endpoints explicitly accept that scope. The token has no script-content or deployment permission. If the individual-Worker scope is unavailable, use the owner dashboard. Do not broaden to a product-wide or write role to make this check work. No token was created or used for this change. [Workers permission scopes](https://developers.cloudflare.com/workers/authorization/workers/) · [List deployments](https://developers.cloudflare.com/api/resources/workers/subresources/scripts/subresources/deployments/methods/list/) · [List versions](https://developers.cloudflare.com/api/resources/workers/subresources/scripts/subresources/versions/methods/list/).

For an already approved, short-lived, single-Worker token in a private shell, set `CF_RADAR_ACCOUNT_ID` and make these GET requests. Keep the token out of command arguments, logs, transcripts and Git:

```sh
set +x
set -o pipefail
read -rs CF_RADAR_READ_TOKEN
radar_get() {
  printf 'header = "Authorization: Bearer %s"\n' "$CF_RADAR_READ_TOKEN" |
    curl --fail --silent --show-error --config - \
      "https://api.cloudflare.com/client/v4/accounts/$CF_RADAR_ACCOUNT_ID/workers/scripts/tffac-mission-control-radar-test/$1"
}
radar_get deployments | jq -e '.result.deployments[0] | {id, versions: [.versions[] | {version_id, percentage}]}'
radar_get versions | jq -e '.result.items[0] | {id, number}'
unset CF_RADAR_READ_TOKEN
```

Inspect only IDs and traffic. Record the observation time and account/Worker selection privately. Keep client secrets, signing secrets, OAuth codes, cookies and raw inventory out of the PR.

## Prepare and verify the credential baseline

A local dry run needs no Cloudflare login. Start from the repository root of a clean checkout with Node 24 and Bash. Use the explicit target for every Wrangler command.

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
```

**Do not upload the candidate while the credential version is staged.** First reconcile the separation between the two versions:

1. From the owner dashboard or approved metadata-only inspection, confirm the original ID is serving 100% and the staged credential ID is still the expected upload. Verify the account, exact test hostname, compatibility, cache, service binding and Google callback. Record the original ID as the rollback for this credential-only window. Stop if either ID or its configuration differs.
2. After separate owner approval for this activation, use the existing authorised operator session to deploy exactly the staged credential ID at 100% on the Radar test Worker. Use the authenticated dashboard if the operator has not approved equivalent Wrangler permissions. With an already authorised Worker-scoped deployment session, the CLI command is:

   ```sh
   radar versions deploy '54793580-0f82-441c-970a-4b9997ba4de0@100' \
     --message "Activate Radar TEST credential baseline only"
   ```

3. Verify the staged ID now serves 100%. In a new Chrome Incognito window, sign in at the exact Radar test origin. Confirm the redirect uses the dedicated Google client and exact callback, the account is accepted, and reload retains the dashboard session. Exercise only dashboard sign-in, which requests `openid email`. Avoid Gmail Connect on the old executable. An independent session signing configuration should reject a stale session from the original deployment, if one is available to test without exposing a cookie.
4. If sign-in fails, the authorised operator restores `271cbcc5-737e-4ec5-ac9f-4560fe96f805` to 100%, confirms the original sign-in, and stops. The equivalent approved CLI command is `radar rollback '271cbcc5-737e-4ec5-ac9f-4560fe96f805'`. No candidate upload follows a failed credential activation.
5. If sign-in succeeds, record the now-serving `54793580-0f82-441c-970a-4b9997ba4de0` as the known-good credential baseline and candidate rollback ID. Only then request separate candidate upload approval.

## Upload and serving traffic

After specific upload authorisation, set `RADAR_ROLLBACK_VERSION` to the recorded full ID, then upload a separately versioned candidate from the reviewed checkout:

```sh
radar versions view "$RADAR_ROLLBACK_VERSION"
radar deployments status --json
radar versions upload --message "Mission Control synthetic Gmail acceptance $(git rev-parse --short HEAD)"
radar versions list --json
radar deployments status --json
```

Record the full uploaded ID as `RADAR_CANDIDATE_VERSION`. Use `radar versions view "$RADAR_CANDIDATE_VERSION"` to compare binding **names and types**, compatibility and placement with the approved baseline. Confirm the existing version still serves 100%. The upload uses the installed encrypted bindings. Supply no secrets file, preview alias, route override, new binding or settings command. Use the exact registered test hostname for the browser session.

After separate authorisation to serve the candidate, confirm the full test version in Wrangler's interactive prompt:

```sh
radar versions deploy "${RADAR_CANDIDATE_VERSION}@100" --message "Mission Control controlled hosted acceptance"
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
| Disconnect and shared state | Open two tabs with a completed count. Disconnect in tab A and check its confirmation and preserved dashboard session. Refresh or reload tab B and check disconnected status and the stale count. Reconnect in tab B, refresh tab A and verify both can run a new synthetic scan. Storage events should invalidate the idle tab promptly. Recheck on refresh if the browser suspended the tab. |
| In-flight success | Start a **Slow successful scan** in tab A. Disconnect before it finishes, then repeat with Disconnect in tab B. Tab A's own Disconnect must discard obsolete results. With two tabs, check whether an older completion updates the display or saved aggregate after Disconnect, and whether Clear Data in one tab is undone by the other. Older scans crossing a shared connection or Clear Data boundary are stop conditions for release. |
| In-flight provider rejection | Start **Slow rejected grant** in tab A. Select **Complete scan** in tab B while A's request is pending. Observe the late 401 in A, then check B's status and grant after the response. If the new grant was cleared, stop. The old response must carry no cookie mutation, and B must remain connected. |
| Radar and Ombudsman | Verify Radar reads an existing successful main-branch artifact and shows provenance. A missing or expired artifact should be reported as unavailable. The Ombudsman feed must report unavailable because the status token is absent. Do not add the token. |
| Workspace and closure | Add a synthetic local workspace item and verify reload. Clear Data resets the browser-local workspace and saved count. Record the tested version, outcomes and any exceptions, then restore and verify the post-credential baseline. |

The two-tab coordination uses origin-local storage and Web Locks in secure browser contexts. Read failures carry no cookie mutation. The dashboard binds each read to the checked grant and rechecks that grant before publishing. Disconnect and Clear Data fence earlier operations, and the most recently started scan takes precedence. When Web Locks or browser storage cannot provide coordination, refresh, Disconnect and count clearing report that limitation rather than publishing across an unprotected boundary. The Phase 2C.5 local Chromium check used two tabs, loopback HTTPS, synthetic sessions and the generated fixture. It confirmed that a late 401 leaves a newer grant active, another tab’s Disconnect retains a stale count and dashboard session, and another tab’s Clear Data stays cleared after a held response finishes. Google consent, Cloudflare routing and test credential activation remain for the hosted window.

References: [Cloudflare versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/), [Wrangler Worker commands](https://developers.cloudflare.com/workers/wrangler/commands/workers/), and [Wrangler configuration and encrypted bindings](https://developers.cloudflare.com/workers/wrangler/configuration/).
