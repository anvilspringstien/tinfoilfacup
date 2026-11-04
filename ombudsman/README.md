# Tin Foil FA Cup — Independent Ombudsman (Shed prototype)

An external, read-only watchdog for GitHub Actions. **Not deployed** by this PR.

## Independence
Runs on Cloudflare Cron, not GitHub Actions. Reads GitHub Actions workflow run history through GitHub's REST API. Never dispatches workflows, changes competition data, or writes to the repository. Uses the *scheduled* event runs rather than manual runs as proof of scheduling.

## Configuration
1. Create a Cloudflare Worker from `worker.mjs` and configure a Cron Trigger (e.g. hourly at minute 20, away from GitHub scanner schedules).
2. Set `RESULTS_WORKFLOW_ID` and `DRAW_WORKFLOW_ID` to the **verified actual GitHub workflow numeric IDs or filenames**. Do not guess them.
3. Bind a Cloudflare KV namespace as `OMBUDSMAN_KV` for persistent report/alert state.
4. Set secret `STATUS_TOKEN` for authenticated `GET /health`.
5. Optionally set secret `GITHUB_TOKEN` for GitHub API quota/restricted repo access.
6. Optionally set secret `ALERT_WEBHOOK_URL` for a compatible JSON webhook. Verify the receiving service accepts `{text,report}` before enabling. Never commit secrets.
7. Optionally set `MAX_AGE_HOURS` (default 3). Tune this **only after confirming each scanner's intended cadence and permissible GitHub schedule delay**.

## States
- healthy: newest scheduled run completed successfully and started recently
- warning: no scheduled run in configured window, or no scheduled runs
- critical: newest scheduled run completed with a non-success conclusion
- pending: newest scheduled run has started but is not completed
- unknown: missing config, invalid timestamps, GitHub API unavailable/error

## Safety / limitations before deployment
- **Do not deploy yet**: confirm workflow IDs, real scanner cadence, webhook contract, and access permissions.
- Initial notification may be generated on first run if webhook configured.
- The first implementation checks most recent scheduled run per workflow, not every missed expected slot; delayed GitHub starts may warrant more granular schedule-slot checks.
- A pending run is not automatically healthy; stuck-run detection should be added.
- KV write/alert delivery errors should be separately surfaced and tested.
- GitHub API failures are `unknown`, not scanner failures.
- Run unit tests and injected outage/failure/recovery simulations before deployment.
- Cloudflare itself can fail; this is independent of GitHub Actions, not infallible.

## Git-connected deployment
Cloudflare Builds is connected to this branch with root directory `/ombudsman` and deploy command `npx wrangler deploy`. The existing KV namespace is declared in `wrangler.toml`; the hourly Cron Trigger remains `20 * * * *`. Relay credentials and health token remain encrypted Cloudflare Worker secrets, never repository variables. Verify the first build and Worker bindings before relying on email alerts.

## Notification policy — 4 November 2026

This branch is already connected to the live `tffc-ombudsman` Worker (successful Cloudflare check on 34d6157). The prototype deployment warnings above describe its original introduction, not its current deployment state. Do not change scanner workflow IDs, health classification, KV namespace, secrets or Cron for this notification-only update.

Raw health still warns after the configured three-hour scheduling window. Email is separate: a schedule-only gap waits until the newest scheduled run is six hours old; missing history waits three hours from first observation; unknown/API status waits thirty minutes. Failures and stuck runs alert immediately. Alternating late scanners and pending launches stay within one incident. A new failed run escalates immediately; an unchanged failure does not repeat. Still-unresolved incidents get at most one reminder per 24 hours. Only a fully healthy observation closes an incident; send one recovery only if an alert was delivered. Brief unnotified gaps therefore produce neither warning nor recovery email. This is not an overnight blanket mute.

`last_report` always records the actual observation. `notification_state_v2` holds incident/delivery state and migrates a legacy warning without repeating it. Delivery still requires the relay's exact `OK`; failed delivery does not consume an alert or recovery. Tests use fake KV/relay/clock and send no real messages. Rollback is the preceding source commit; keep KV and credentials. KV is eventually consistent, so overlapping runs or a crash after relay delivery and before state write can still duplicate an alert; this policy does not promise exactly-once email.
