# Mission Control Radar TEST hosted acceptance

The target is the existing [Radar TEST Worker](https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/). This PR prepares it for a controlled acceptance window. Upload, traffic changes and rollback are owner operations performed only within a separately authorised window.

## Custody and target

| Item | Baseline |
| --- | --- |
| GitHub source | PR [#742](https://github.com/anvilspringstien/tinfoilfacup/pull/742) is included in the owner’s clean checkout at `d4c6d84e40ef05a16d7cee7d5c650278304968f8`. The reviewed Worker SHA-256 matched. |
| Cloudflare Worker | `tffac-mission-control-radar-test` |
| Verified serving and candidate rollback version | `54793580-0f82-441c-970a-4b9997ba4de0` at 100%, observed by the owner on 26 November 2026. |
| Credential history | Previous serving version `271cbcc5-737e-4ec5-ac9f-4560fe96f805`. Dashboard updates were `63bc39a1` for `GOOGLE_CLIENT_ID`, `e665aa81` for `GOOGLE_CLIENT_SECRET` and `54793580` for `SESSION_SECRET`. |
| Runtime | Compatibility date `2026-11-21`, no compatibility flags, Default placement, cache disabled. The exact `workers.dev` host remains enabled and preview URLs remain disabled. Observability and logs are enabled. |
| OAuth | The owner verified dedicated test-client sign-in and refresh on the serving credential baseline. Exact callback `https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/oauth/callback`. Rejection of a stale session from before the credential change remains untested. |
| Dashboard bindings | `GOOGLE_CLIENT_ID` is a plain-text variable. `GOOGLE_CLIENT_SECRET`, `SESSION_SECRET` and `GITHUB_RADAR_TOKEN` are encrypted. Inspect names and types only. |
| Service | `OMBUDSMAN_SERVICE` → `tffc-ombudsman`, environment `production`, entrypoint `default`. With `OMBUDSMAN_STATUS_TOKEN` absent, the candidate reports the feed unavailable and skips the service call. |
| CLI access | The owner verified a temporary account-owned API token with **Individual Workers Editor** permission scoped exclusively to the existing Radar TEST Worker. |
| Hosted finding 01 | The owner uploaded candidate `0e17ffd8-5afa-4265-b2b2-e4f179677e31` from `218dd45fea5793b6c3536990f85e286d209e3460` with Wrangler 4.156.2 and confirmed its five bindings, runtime, Observability and disabled preview URLs at 100%. Sign-in passed, Outreach began at Unknown and Ombudsman showed unavailable. Acceptance stopped before either Gmail control was clicked after the inherited live drafts shortcut was found. The owner restored the verified rollback baseline above to 100%. |

The [explicit Wrangler target](wrangler.radar-test.toml) builds from the reviewed `worker.mjs` into a git-ignored directory. The [builder](build-radar-test.mjs) stops when an expected integration point changes. The candidate pins the Radar test origin, labels both sign-in and dashboard pages **TEST**, and keeps the existing Google dashboard sign-in checks and `openid email` scopes. The authenticated test form issues a short-lived, synthetic grant bound to the dashboard session. Gmail requests use the [local synthetic transport](test/hosted-gmail-fixture.mjs) through the same parser, pagination, audit, status and Disconnect logic. The generated Worker has no Gmail OAuth handler or Gmail network fallback. Radar remains a read-only GitHub integration.

## Read-only deployment inspection

Recheck the serving version, latest upload and traffic in the owner dashboard before any authorised action. The dashboard is sufficient for read-only inspection.

If the owner separately approves API inspection, Cloudflare documents an API token with **Metadata Read-Only** scoped to **Individual Workers**, selecting only `tffac-mission-control-radar-test`. Both inventory endpoints explicitly accept that scope. The token has no script-content or deployment permission. If the individual-Worker scope is unavailable, use the owner dashboard. Do not broaden to a product-wide or write role to make this check work. Use the editor token only for an explicitly authorised operation in the existing TEST Worker. [Workers permission scopes](https://developers.cloudflare.com/workers/authorization/workers/) · [List deployments](https://developers.cloudflare.com/api/resources/workers/subresources/scripts/subresources/deployments/methods/list/) · [List versions](https://developers.cloudflare.com/api/resources/workers/subresources/scripts/subresources/versions/methods/list/).

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

## Local verification

A dry run needs no Cloudflare login. Start from the repository root of a clean checkout with Node 24 and Bash. Use the explicit target for every Wrangler command.

Wrangler is pinned to **4.156.2** for this target. On the owner’s checkout, both 4.156.1 and 4.156.2 passed the dry run with identical reported build sizes. Only 4.156.2 got past the remote metadata retrieval that blocked 4.156.1 with the restricted token. The candidate upload was then cancelled for configuration review.

```sh
radar() {
  WRANGLER_SEND_METRICS=false npx --yes wrangler@4.156.2 "$@" \
    --cwd mission-control-worker --config wrangler.radar-test.toml
}
git rev-parse HEAD
git status --short
node --check mission-control-worker/worker.mjs
(cd mission-control-worker && sha256sum --check SHA256SUMS)
node --test mission-control-worker/worker.test.mjs
TFFAC_MC_TEST_TARGET=isolated node --test mission-control-worker/worker.test.mjs
node --test mission-control-worker/test/hosted-target.test.mjs
radar versions upload --dry-run
```

## Wrangler 4.156.2 configuration reconciliation

The published [Wrangler 4.156.2 package](https://www.npmjs.com/package/wrangler/v/4.156.2) is the reference for the command behaviour below. The local dry run builds the same upload metadata without making the remote preflight requests.

| Remote observation | Reviewed local representation and effect |
| --- | --- |
| Preview URLs disabled | `preview_urls = false` prevents Wrangler’s comparison from inferring enabled previews from `workers_dev = true`. Version upload reads the remote subdomain settings when reporting URLs and does not change them. Use only the exact registered TEST hostname. |
| Dashboard-only `GOOGLE_CLIENT_ID` | `keep_vars = true` adds `plain_text` and `json` to `keep_bindings` in the version upload payload. The upload also includes `secret_text` and `secret_key` for unchanged secrets. Wrangler sends `bindings_inherit=strict` to the versions API. A dashboard variable can still appear in the configuration comparison because the comparison does not apply the upload’s inheritance rules. Keep its value out of TOML and verify its name and type on the candidate before serving it. |
| `OMBUDSMAN_SERVICE`, production, default | The service binding encodes `environment = "production"` and `entrypoint = "default"`, matching the observed remote binding metadata. Wrangler 4.156.2 accepts and serializes both fields. |
| Observability and logs enabled | Both are explicit in TOML. Wrangler compares them before upload but omits observability from the version payload. `versions deploy` can separately sync it after changing traffic. Before any CLI deployment, verify the complete Observability configuration in the owner dashboard, including sampling, invocation logs, persistence and traces. If any unrecorded settings differ, stop and reconcile them before scheduling CLI deployment. |
| Cache disabled | `[cache] enabled = false` retains the disabled state in the versioned upload metadata. |

## Upload and serving traffic

Immediately before a separately authorised upload, confirm that `54793580-0f82-441c-970a-4b9997ba4de0` still serves 100% and is the intended rollback version. Confirm the account, exact TEST hostname and callback, placement, cache and all binding names and types in the owner dashboard. Stop on unexpected state or a newer upload so the version from which Cloudflare inherits bindings can be confirmed.

Use an interactive private shell with the existing authorised TEST-only token set outside the command line. Keep shell tracing, debug logs and session recording off. Review the prompt privately because Wrangler’s comparison may display dashboard variable values. Cancel on any unexplained difference. Proceed past a known dashboard-only `GOOGLE_CLIENT_ID` difference only once the owner has approved the inherited-variable approach. Use the owner dashboard for settings and binding inspection where the restricted token cannot read the required metadata. Do not broaden access.

```sh
RADAR_ROLLBACK_VERSION=54793580-0f82-441c-970a-4b9997ba4de0
radar deployments status --json
radar versions upload --message "Mission Control synthetic Gmail acceptance $(git rev-parse --short HEAD)"
radar versions list --json
radar deployments status --json
```

Record the full uploaded ID as `RADAR_CANDIDATE_VERSION`. In the dashboard, compare the candidate’s binding names, types and service target, compatibility and placement with the verified baseline. Confirm that the candidate inherited `GOOGLE_CLIENT_ID` and all three encrypted bindings and that the rollback version still serves 100%. Upload from the reviewed commit with no secrets file, preview alias, environment or route override. No triggers or settings command is required for acceptance.

After separate authorisation to serve the candidate and verification of the full observability settings, confirm the full TEST candidate ID in Wrangler’s interactive prompt:

```sh
radar versions deploy "${RADAR_CANDIDATE_VERSION}@100" --message "Mission Control controlled hosted acceptance"
radar deployments status --json
```

Verify the traffic and dashboard settings after that command, including if a settings sync fails after the traffic change. Use the window for testing only. Restore the verified baseline at the end of the window or immediately after a stop condition:

```sh
radar rollback "$RADAR_ROLLBACK_VERSION" --message "Restore verified post-credential Radar test baseline"
radar deployments status --json
```

Verify the recorded version is back at 100%, preview URLs are still disabled, observability and logs are still enabled, the TEST gate requires authentication, and fresh Incognito sign-in and refresh work. Close the temporary browser session after recording results. Browser-local test state is disposable and is reset separately.

## Hosted browser acceptance

Use a fresh Chrome Incognito window for the Radar host and two tabs in that same window for shared-cookie tests. A separate browser profile can check isolation if needed. Sign in to the dashboard using the already approved Google identity and test client. Check the Overview and Outreach Desk for the **Synthetic Gmail** panel and a clearly labelled **Connect synthetic Gmail** or **Reconnect synthetic Gmail** action. The fixture selection page must say **Connect synthetic Gmail**. Check the Overview shortcuts and Links Desk for absence of mailbox links. Stop immediately if any live mailbox shortcut, Gmail consent, live redirect, live data or unexpected binding appears.

| Check | Action and expected result |
| --- | --- |
| Host, OAuth and TEST identity | Confirm the exact test hostname, protected initial page, the dedicated callback and **TEST** in the tab title and dashboard. An unauthenticated API request is denied. Preview and alternate origins are covered in the automated suite. |
| First count and true zero | Start with **Clear Data** on the test origin. Run **Unresolved introduction** first and expect **Synthetic clubs contacted: Unknown** with an unresolved status. Run **Complete zero** and expect a current zero and timestamp. |
| Complete, stale and partial | Run **Complete scan** and expect two unique clubs after both query families, deduplication and reply exclusion. Reload and confirm the retained aggregate. Run **Unresolved introduction**, **Provider rate limit**, **Provider permission error** and **Simulated network failure**. Expect distinct statuses and the saved count and timestamp retained. **Partial drafts** must leave a complete contacted count with drafts unknown. |
| Session versus grant expiry | Use **Synthetic grant expires after 20 seconds** or **Provider rejects the synthetic grant**. After expiry or rejection, refresh and check for **Reconnect synthetic Gmail** and a stale synthetic count. For dashboard expiry, leave the test window until the one-hour session expires, or delete only the test session cookie using DevTools. Refresh from the existing page and expect Mission Control sign-in guidance. Cookie deletion simulates the absent-session response. |
| Disconnect and shared state | Open two tabs with a completed count. Disconnect in tab A and check its confirmation and preserved dashboard session. Refresh or reload tab B and check disconnected status and the stale count. Reconnect in tab B, refresh tab A and verify both can run a new synthetic scan. Storage events should invalidate the idle tab promptly. Recheck on refresh if the browser suspended the tab. |
| In-flight success | Start a **Slow successful scan** in tab A. Disconnect before it finishes, then repeat with Disconnect in tab B. Tab A's own Disconnect must discard obsolete results. With two tabs, check whether an older completion updates the display or saved aggregate after Disconnect, and whether Clear Data in one tab is undone by the other. Older scans crossing a shared connection or Clear Data boundary are stop conditions for release. |
| In-flight provider rejection | Start **Slow rejected grant** in tab A. Select **Complete scan** in tab B while A's request is pending. Observe the late 401 in A, then check B's status and grant after the response. If the new grant was cleared, stop. The old response must carry no cookie mutation, and B must remain connected. |
| Radar and Ombudsman | Verify Radar reads an existing successful main-branch artifact and shows provenance. A missing or expired artifact should be reported as unavailable. The Ombudsman feed must report unavailable because the status token is absent. Do not add the token. |
| Workspace and closure | Add a synthetic local workspace item and verify reload. Clear Data resets the browser-local workspace and saved count. Record the tested version, outcomes and any exceptions, then restore and verify the post-credential baseline. |

The two-tab coordination uses origin-local storage and Web Locks in secure browser contexts. Read failures carry no cookie mutation. The dashboard binds each read to the checked grant and rechecks that grant before publishing. Disconnect and Clear Data fence earlier operations, and the most recently started scan takes precedence. When Web Locks or browser storage cannot provide coordination, refresh, Disconnect and count clearing report that limitation rather than publishing across an unprotected boundary. The Phase 2C.5 local Chromium check used two tabs, loopback HTTPS, synthetic sessions and the generated fixture. It confirmed that a late 401 leaves a newer grant active, another tab’s Disconnect retains a stale count and dashboard session, and another tab’s Clear Data stays cleared after a held response finishes. Candidate authentication, Cloudflare routing and the synthetic Gmail browser scenarios remain for the hosted window. Test stale pre-credential session rejection only if such a session is already available on the TEST origin. Keep the cookie inside that browser.

References: [Cloudflare versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/), [Wrangler Worker commands](https://developers.cloudflare.com/workers/wrangler/commands/workers/), and [Wrangler configuration and encrypted bindings](https://developers.cloudflare.com/workers/wrangler/configuration/).
