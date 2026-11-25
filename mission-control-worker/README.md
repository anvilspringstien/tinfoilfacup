# Mission Control Worker baseline

The project owner recovered this source directly from the active Cloudflare editor on 25 November 2026. [worker.mjs](worker.mjs) is the complete export of `TFFAC-Mission-Control-LIVE-d4a21101-BACKUP-2026-11-25.js`, with its original CRLF line endings. The import was compared byte-for-byte with the owner-supplied file. [SHA256SUMS](SHA256SUMS) records the independently calculated fingerprint.

| Existing setting | Recovered baseline |
| --- | --- |
| Worker | `tffac-mission-control` |
| Active deployment reference | `d4a21101` |
| Previous version reference | `abf1928e` |
| Earlier rollback reference | `6a69b0e5` |
| Compatibility date | `2026-11-18` |
| Compatibility flags | None |
| Placement | Default |
| Cache | Disabled |
| Host | `tffac-mission-control.anvilspringstien.workers.dev` |
| Google OAuth callback | `/oauth/callback` on that exact host |
| Service binding | `OMBUDSMAN_SERVICE` → `tffc-ombudsman`, default entrypoint |

Source review covered embedded credential patterns, literals and payloads, browser workspace initialisation, and the worker-side routes that handle OAuth, Gmail, Radar and the health binding. The sign-in allowlist names the same public project mailbox used by the [Shed contact form](../beta/post-office.js). The dashboard includes a small fallback from public club data and initialises the local workspace empty. The import contains no saved workspace, mailbox export or secret values.

| Encrypted binding | Use |
| --- | --- |
| `GITHUB_RADAR_TOKEN` | Read-only GitHub Radar artifact retrieval |
| `GOOGLE_CLIENT_ID` | Existing Google OAuth client identifier |
| `GOOGLE_CLIENT_SECRET` | Existing OAuth code exchange |
| `OMBUDSMAN_STATUS_TOKEN` | Authentication for the existing health binding |
| `SESSION_SECRET` | Session signing and encryption of the Gmail grant cookie |

No local secret files are required. The binding names above identify the existing encrypted bindings. Keep them as-is. The [Wrangler reference](wrangler.baseline.toml) leaves the service entrypoint unspecified to select the default and omits a placement override to retain default placement. Record the dashboard cache setting in release review separately. The application already returns private, no-store responses on protected routes.

## Local regression checks

From the repository root, using Node.js 24:

```sh
(cd mission-control-worker && sha256sum -c SHA256SUMS)
node --check mission-control-worker/worker.mjs
node --test mission-control-worker/worker.test.mjs
```

The tests cover the source fingerprint, Google sign-in and exact hostname, deny-by-default HTTP routing, same-origin session controls, separate Gmail consent and read-only queries, Radar artifact selection and credential separation, and Ombudsman freshness and response filtering. The dashboard's actual inline scripts run against a small DOM, fetch and browser-storage harness to check navigation and workspace restoration. These checks use synthetic bindings, tokens and service responses. They do not validate real Google consent, the actual Cloudflare bindings or Chrome installation.

## Source-import deployment isolation

This PR adds no deployment workflow, Git integration, deployment hooks or root-level Wrangler configuration. The reference file has a non-default name and is selected only with `--config`. The import commit uses the CI-skip marker so the documentation and source can be reviewed without triggering GitHub Actions or Cloudflare Pages preview deployment. Run the tests locally for this import. Existing Workers Builds integrations are managed separately in Cloudflare and are left as configured. Keep this branch off the production branch until separately approved. See [Pages CI-skip behaviour](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/) and [Workers build branch controls](https://developers.cloudflare.com/workers/ci-cd/builds/build-branches/).

## Future release and rollback

Approval of the source-import PR and approval to change the live Worker are distinct decisions. Perform the following only when the project owner approves a specific release. Use the existing Worker, account, host, encrypted bindings and service binding. Resolve the short references in the table to full Cloudflare IDs from the existing deployment history before a release.

1. Record the currently serving version and its traffic percentage. Export the existing Worker source and have the site operator export their browser-local workspace through **Sources & safety**. The Worker source export does not include browser data.
2. In the approved checkout, run the local checks and compare the reference config to the existing Worker settings. Confirm the exact host, callback, bindings, compatibility, placement, cache, and existing route and preview settings in Cloudflare. Resolve any drift before an upload. Keep the reference config scoped to the existing Worker, with no secrets file or route changes.
3. After authorisation, use the approved Wrangler CLI and explicit config from the repository root. Inspect the active deployment, then upload the reviewed version. Uploading creates a version without moving production traffic. Obtain its full version ID and compare its settings with the recorded baseline before promoting it. [Cloudflare Worker versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/).

```sh
wrangler deployments status --config mission-control-worker/wrangler.baseline.toml
wrangler versions upload --config mission-control-worker/wrangler.baseline.toml
```

4. After approval to shift traffic, deploy the exact uploaded version. Replace the example value with its full ID. Confirm the target and percentage in Wrangler's prompt. Then check the original hostname, sign-in, Gmail read-only views, Radar automatic and manual loading, Ombudsman health, navigation and existing local workspace.

```sh
wrangler versions deploy '<approved-version-id>@100' --config mission-control-worker/wrangler.baseline.toml
wrangler deployments status --config mission-control-worker/wrangler.baseline.toml
```

5. For an approved rollback, target the verified last known-good full version ID. Check that it remains available and compatible with the existing bindings. Use the deployment recorded in step 1 first. The owner-supplied references `abf1928e` and `6a69b0e5` are historical fallbacks. Rollback changes serving traffic immediately. Verify the serving version and repeat the Smoke checks from step 4. [Wrangler Worker commands](https://developers.cloudflare.com/workers/wrangler/commands/workers/).

```sh
wrangler rollback '<verified-rollback-version-id>' --config mission-control-worker/wrangler.baseline.toml
wrangler deployments status --config mission-control-worker/wrangler.baseline.toml
```

## Known issues carried forward

- Gmail permission expiry.
- Failed **Disconnect Gmail** action in the deployed browser flow. The mocked tests exercise the Worker endpoint and its expected request headers.
- Last successful Gmail count not retained.
- Approved Mission Control icon not used by Chrome.
- Club Audit integration outstanding.
