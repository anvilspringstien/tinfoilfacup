# Like TFFAC — opt-in Shed

One site-wide appreciation per browser, independent of Campaign identity. A second tap removes it. Same-origin pages share one random local-storage token. No total is displayed publicly. `GET /admin/count` is protected by a separately configured `ADMIN_TOKEN`.

## Current state

The frontend is **opt-in only**: visit `beta/likes-shed.html` or append `?likePreview=1`. The flag is remembered for that tab's session across Campaign, Challenges and Barry Air. Normal visitors return before any Like config, stylesheet or service requests. `beta/like-config.json` has no deployed endpoint and remains disabled. A real service response is required before the heart becomes liked; failure preserves the last confirmed state.

The three footer blocks on the overview are layout samples. Links underneath open the actual app pages with the same Like component. Campaign and Challenges insert their Magic rows dynamically; the component observes those rows and restores handlers after saved HTML snapshots.

## Storage and free plan

The independent `tffac-likes-shed` Worker uses a new SQLite-backed Durable Object binding and namespace, not the existing Clubfinder counter. Only a SHA-256 hash of a random browser UUID and a shared integer are stored. Unlike deletes that hash. No postcode, Campaign number, pigeon name, email, IP address or user-agent is stored by this application. Cloudflare necessarily processes network metadata. Clearing browser storage or using another browser can permit another Like; this is informal feedback, not a verified people count. UUIDs are not authentication or a robust anti-bot mechanism.

Cloudflare documentation checked 2 November 2026: SQLite Durable Objects are on Workers Free; limits include 100,000 requests/day, 100,000 row writes/day and 5GB storage. Free-plan excess operations fail instead of becoming overage charges. Verify the **actual account is Workers Free** before deploying: this repository cannot prove account billing state. Do not upgrade plans or use paid storage. No account, subscription, external analytics, or paid widget is required by this implementation.

Sources:
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/durable-objects/platform/limits/

## Checks and local preview

Node 24 is used for built-in SQLite:

```sh
node --test tests/likes-worker.test.mjs
node likes-worker/dev-server.mjs
```

The local server serves this checkout and `/__likes/{state,reaction}` using a separate database in the OS temporary directory under `tffac-likes-shed/likes.sqlite`. It does not write Campaign data or issue production Campaign numbers. Its `/__shed/count` endpoint is a **development-only diagnostic**, absent from the Cloudflare Worker. This is a real persisted local count, not the public count.

## Deploy separately after review

1. Verify Cloudflare account/Free plan and authenticate Wrangler. Deployment access was unavailable when this change was prepared.
2. From `likes-worker`, use the pinned Wrangler in the check workflow to dry-run; configure `ADMIN_TOKEN` with `wrangler secret put ADMIN_TOKEN`, then deploy the new independent Worker. Never place that secret in frontend config or Git.
3. Verify health, exact allowed origins, private count authorization and test Like/unlike returning the count to its initial value. No unapproved live mutations by CI.
4. Set `beta/like-config.json` endpoint to the returned verified Worker URL. Keep `enabled:false` and the opt-in frontend gate until the Shed has been reviewed. Do not invent an endpoint or show a fake success without it.
5. Before public activation, update the site's Privacy copy to explain the browser token and central reaction hash. Public activation is a separate reviewed change: remove the early opt-in return and switch config only after the Worker is verified. Leave the search counter, competition machinery and protected `clubfinder.html` unchanged.

## Service contract

- `POST /state` with `{token}` returns `{liked}`.
- `POST /reaction` with `{token,liked:boolean}` sets a desired state idempotently and returns `{liked}`. No public total.
- Both require an exact allowed Origin and JSON; bodies are limited to 512 bytes and unexpected fields are rejected.
- `GET /admin/count` with private Bearer token returns `{total}`.
- `GET /health` returns only service readiness/contract version.
