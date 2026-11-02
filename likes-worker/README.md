# Like TFFAC — opt-in Shed

One site-wide appreciation per browser, independent of Campaign identity. A second tap removes it. Same-origin pages share one random local-storage token. No total is displayed publicly. `GET /admin/count` is protected by a separately configured `ADMIN_TOKEN`.

## Current state

The shared control is publicly enabled in Campaign, Challenges and Barry Air. The independent service is deployed at `https://tffac-likes-shed.anvilspringstien.workers.dev`. The owner confirmed Workers Free, deployed from GitHub, saved the private count token as an encrypted runtime Secret, and verified health, unauthorized count rejection, Like/unlike and refresh persistence from the real site. Automated service probes from the development environment received Cloudflare error 1010; do not mistake that for an application response.

A fresh visit reads any existing browser identifier but creates no identifier, writes no Like storage and makes no Like-service request. Only the first heart tap creates and saves the random identifier. Existing identifiers query the service to restore the saved choice. A real service response is required before the heart becomes liked; failure preserves the last confirmed state. Clearing storage cannot remove a previously counted Like without its identifier.

The three footer blocks on `beta/likes-shed.html` are layout samples. Campaign and Challenges insert their Magic rows dynamically; the shared component observes those rows and restores handlers after saved HTML snapshots. Privacy wording is shared with Barry Air through the footer generator.

## Storage and free plan

The independent `tffac-likes-shed` Worker uses a new SQLite-backed Durable Object binding and namespace, not the existing Clubfinder counter. Only a SHA-256 hash of a random browser UUID and a shared integer are stored. Unlike deletes that hash. No postcode, Campaign number, pigeon name, email, IP address or user-agent is stored by this application. Cloudflare necessarily processes network metadata. Clearing browser storage or using another browser can permit another Like; this is informal feedback, not a verified people count. UUIDs are not authentication or a robust anti-bot mechanism.

Cloudflare documentation checked 2 November 2026: SQLite Durable Objects are on Workers Free; limits include 100,000 requests/day, 100,000 row writes/day and 5GB storage. Free-plan excess operations fail instead of becoming overage charges. Verify the **actual account is Workers Free** before deploying: this repository cannot prove account billing state. Do not upgrade plans or use paid storage. No account, subscription, external analytics, or paid widget is required by this implementation.

Sources:
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/durable-objects/platform/limits/

## Checks and local preview

Node 24 is used for built-in SQLite:

```sh
node --test tests/likes-worker.test.mjs tests/likes-client.test.mjs
node likes-worker/dev-server.mjs
```

The local server serves this checkout and `/__likes/{state,reaction}` using a separate database in the OS temporary directory under `tffac-likes-shed/likes.sqlite`. It does not write Campaign data or issue production Campaign numbers. Its `/__shed/count` endpoint is a **development-only diagnostic**, absent from the Cloudflare Worker. This is a real persisted local count, not the public count.

## Deployment and rollback

Cloudflare Git integration deploys from `main` with repository root `/` and command `npx wrangler@4.156.1 deploy --config likes-worker/wrangler.jsonc`. The Worker is independent of the search counter and competition machinery. `ADMIN_TOKEN` is a runtime Secret, never a build variable, frontend setting or Git file. The owner retains it in their password manager.

For rollback, set `enabled:false` in `beta/like-config.json`; ordinary pages then mount no control and make no Like-service requests. The existing explicit `?likePreview=1` remains available for Shed diagnostics. Do not upgrade plans or change the identity counter when maintaining this service.

## Service contract

- `POST /state` with `{token}` returns `{liked}`.
- `POST /reaction` with `{token,liked:boolean}` sets a desired state idempotently and returns `{liked}`. No public total.
- Both require an exact allowed Origin and JSON; bodies are limited to 512 bytes and unexpected fields are rejected.
- `GET /admin/count` with private Bearer token returns `{total}`.
- `GET /health` returns only service readiness/contract version.
