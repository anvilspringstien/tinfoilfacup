# Tin Foil FA Cup — private Clubfinder usage counter

This Worker is the deliberately tiny shared "biscuit jar" for Clubfinder usage and Campaign search identities.

## What it counts

One successful Clubfinder search should call `POST /increment` exactly once.

It counts uses, not people. Repeating a successful search counts again because that is another real use of Clubfinder.

Page loads, invalid searches, Stats visits, resets and other UI actions must not increment it.

## Privacy

The application stores only one integer: the cumulative count. The number created by a successful search is returned to that search so Clubfinder can display it and, if a Campaign is chosen, adopt it as that Campaign's identity.

Clubfinder must not send the entered postcode, club choices, Campaign data, user identity or any other payload to this service. The increment endpoint accepts no application data. It returns only the sequential number issued to that successful search; the separate arbitrary total remains private behind the admin endpoint.

Cloudflare will necessarily receive normal network request metadata while serving the request, but this Worker does not persist that metadata.

## Endpoints

- `POST /increment` — atomically adds one and returns `{ "number": N }`, where `N` is the number issued to that successful search. It does not provide a separate read-current-total API.
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
}).then(r => r.ok ? r.json() : null)
  .then(v => v && v.number)
  .catch(() => null);
```

Clubfinder treats this request as non-blocking. Counter failure must never block, alter or break Clubfinder; it simply means that search has no issued number.

Do not call the endpoint merely because the Find My Club button was pressed. The increment belongs after the successful-return condition has been met.
