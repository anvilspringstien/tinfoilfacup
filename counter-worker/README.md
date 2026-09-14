# Tin Foil FA Cup — private Clubfinder usage counter

This Worker is the deliberately tiny shared "biscuit jar" for Clubfinder usage.

## What it counts

One successful Clubfinder search should call `POST /increment` exactly once.

It counts uses, not people. Repeating a successful search counts again because that is another real use of Clubfinder.

Page loads, invalid searches, Stats visits, resets and other UI actions must not increment it.

## Privacy

The application stores only one integer: the cumulative count.

Clubfinder must not send the entered postcode, club choices, Campaign data, user identity or any other payload to this service. The increment endpoint accepts no application data and returns no count.

Cloudflare will necessarily receive normal network request metadata while serving the request, but this Worker does not persist that metadata.

## Endpoints

- `POST /increment` — atomically adds one; returns `204` and never exposes the total.
- `GET /admin/count` — returns `{ "total": N }`; requires the private bearer token.
- `GET /health` — simple deployment health check; exposes no usage data.

The count is held by a single SQLite-backed Durable Object so simultaneous successful searches cannot overwrite one another.

## Deploy

From `counter-worker/`:

```sh
npm install
npx wrangler secret put ADMIN_TOKEN
npm run deploy
```

Choose a long random value for `ADMIN_TOKEN`. It must never be embedded in Clubfinder.

After deployment, set `ALLOWED_ORIGINS` in `wrangler.jsonc` to the exact origin(s) from which the embedded Clubfinder is served, comma-separated, then deploy again. While `ALLOWED_ORIGINS` is blank, cross-origin increments are accepted from any origin; this is convenient for setup but should not be the final production setting.

## Read the private count

```sh
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  https://YOUR-WORKER.workers.dev/admin/count
```

## Clubfinder integration contract

Clubfinder should make a fire-and-forget request only after a valid postcode search has successfully produced the three initial Clubfinder returns:

```js
fetch("https://YOUR-WORKER.workers.dev/increment", {
  method: "POST",
  mode: "cors",
  keepalive: true
}).catch(() => {});
```

The `.catch(() => {})` is intentional. Counter failure must never block, alter or break Clubfinder.

Do not call the endpoint merely because the Find My Club button was pressed. The increment belongs after the successful-return condition has been met.
