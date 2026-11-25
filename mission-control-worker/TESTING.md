# Mission Control regression and isolation

The [GitHub Actions workflow](../.github/workflows/mission-control-regression.yml) runs for Mission Control PR changes and can be started manually. The job checks syntax, the current SHA-256 manifest and the original d4a21101 fingerprint from the pinned Phase 2B merge commit. It runs the regression suite against the Worker and repeats it with the isolated fixture. The job has read-only repository permissions and no schedule, deployment or Cloudflare authentication step.

| Target | Worker host and OAuth callback used by the test | Workspace and credentials |
| --- | --- | --- |
| Baseline | The real source's exact host and callback are exercised through in-process requests. | Fake OAuth responses and bindings. Browser storage is a fresh in-memory map, shared only when a test simulates reopening the same workspace. |
| Isolated fixture | `https://mission-control.test/oauth/callback` using a reserved test hostname. The loader changes the origin declaration in memory for the test process. | The same synthetic upstreams and a fresh in-memory browser workspace. The actual live and Radar test origins are rejected in this mode. |

Run the checks in [README.md](README.md). Select the fixture with `TFFAC_MC_TEST_TARGET=isolated`. The loader accepts only the two test modes and blocks unmocked fetches before loading the Worker. The fixture cannot be deployed through Wrangler. It has no listener, provider registration, live credentials, Cloudflare resource bindings or browser-profile access. The preserved `worker.mjs` file is used directly in baseline mode.

## Existing Radar test Worker

On 25 November 2026, unauthenticated GET requests to [the existing Radar test host](https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/) returned HTTP 403 for `/` and `/api/radar/latest` and 401 for `/api/gmail/status`. The historical Radar handoffs name that distinct Worker and report a previous successful authenticated fetch of a main-branch Radar artifact. The public responses confirm its external access gate. The current deployment revision, OAuth client, installed binding names, and last successful authenticated test require owner-side verification.

The existing Radar test Worker is a candidate for a later owner-approved hosted test. The recovered Worker pins the live hostname and rejects requests to the Radar test hostname, so a copy of the current source would fail closed there. Phase 2C.4 adds an explicit [Radar TEST target and acceptance runbook](HOSTED-ACCEPTANCE.md). Preparation leaves the existing Worker serving its current configuration.

## Owner checks before any hosted smoke test

| Area | Owner decision or verification |
| --- | --- |
| Worker and rollback | Verify the existing Radar test Worker name, active version, rollback version and whether it has a deployment integration. Preserve a backup of that Worker and its local workspace. Approve the exact candidate and test Worker before any upload. |
| OAuth | Confirm a test-only OAuth client and the exact test redirect URI, `https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/oauth/callback`. Keep the live callback and client untouched. Approve a test identity and mailbox containing synthetic data before any real Gmail consent. Use the local mocks if a safe test identity or client is unavailable. |
| Credentials and bindings | Verify isolation by binding names and placement with the owner. A future candidate needs its own session-signing secret and its own permitted test credentials. Keep source-controlled tests synthetic and leave GitHub, Gmail and health mocks in place whenever isolation has not been established. |
| Browser workspace | Use a separate browser profile and the Radar test origin. Start with an empty or synthetic test workspace. Preserve the live workspace independently and keep its export out of the test profile. |
| Limits | Keep existing Gmail access read-only. Use the existing Radar test Worker only after explicit approval. No new Worker, namespaces or paid service are needed for the offline regression runs. |

See [Cloudflare's preview isolation guidance](https://developers.cloudflare.com/workers/previews/) and [Google OAuth redirect URI rules](https://developers.google.com/identity/protocols/oauth2/web-server#authorization-errors). This phase does not create a Cloudflare Preview or change any deployment settings.
