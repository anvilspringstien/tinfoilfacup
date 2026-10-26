# Barry’s Post Office — activation checklist

The design preview is published and remains non-sending. The dedicated Worker was deployed successfully on 26 October 2026, with the fixed Gmail destination, Durable Object and rate-limit bindings confirmed in its build log. Anvil confirmed that the Production Turnstile secret was stored privately. The service is enabled for an isolated real-delivery test; **the public footer links are not switched yet**.

## Free delivery

Cloudflare states that sends to an account’s verified destination addresses are free on Workers Free, including when only Email Routing is configured. The binding is restricted to `tinfoilfacup@gmail.com`. Do not enable arbitrary-recipient sending or upgrade the plan.

Use the dedicated subdomain `post.tinfoilfacup.com` for the sender `barry@post.tinfoilfacup.com`; establish it as a routing domain before sending. Review the provider’s suggested DNS records for this subdomain only. Preserve existing root-domain mail records and website hosting. If the dashboard requires a paid plan for the selected route, stop and reassess.

References checked 26 October 2026:
- https://developers.cloudflare.com/email-service/platform/pricing/
- https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/
- https://developers.cloudflare.com/email-service/api/send-emails/workers-api/
- https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
- https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/

## Activation

1. Verify `tinfoilfacup@gmail.com` as the destination in Cloudflare Email Routing. Configure the dedicated sending subdomain as above.
2. Create a free managed Turnstile widget restricted to `tinfoilfacup.com`, `www.tinfoilfacup.com` and `anvilspringstien.github.io`. Obtain its public site key and private secret. Never commit the secret.
3. Connect a **new** Cloudflare Worker to this repository with root `/post-office-worker` and deploy command `npx wrangler deploy`. Do not change the Ombudsman or counter Worker. Check that rate-limit namespace ID `178025098` is unused by other Workers in this account; select a unique ID if necessary.
4. Set the encrypted Worker secret `TURNSTILE_SECRET`. Verify all three bindings: POST_MAIL, POST_OFFICE, RATE_LIMITER. Deploy first with `ENABLED=false`; health must return `ready:false` and messages must be rejected.
5. Set `ENABLED=true` and deploy. Verify `/health` returns `ready:true`. This readiness probe checks configuration, **not inbox delivery**.
6. Use the actual returned Worker URL in `TFFC_POST_OFFICE={endpoint:'https://ACTUAL-WORKER/messages',sitekey:'PUBLIC-KEY'}` before `post-office.js`. Never invent a deployment URL or expose a secret.
7. In a private integration test, submit one identifiable message through the real form. Verify it arrives in Gmail, the subject, body, Reply-To and delivery reference. Submit the same UUID/payload through a controlled test and verify only one received message. Test validation, Turnstile failure, keyboard/phone dismissal and provider failure. No automatic retries.
8. Only then add `post-office-launcher.js` to the two public BETA pages. It intercepts the existing footer links when public endpoint/site-key configuration is present; otherwise they keep their current behaviour. Clubfinder and Challenges HTML must be separate isolated PRs under existing guards. Refresh the Stage C report separately as required. The small launcher loads with the page; form CSS/JS, existing images and Turnstile load only on the first contact interaction.
9. Add the incoming `Barry’s Post Office` subject to the appropriate Gmail label/workflow through the guided settings process. Do not silently create Gmail rules.

## Behaviour

- Feedback and Issue Report share one dialog. Name optional, reply email and message required. No attachments or Campaign/device/location payload.
- Fixed recipient, plain-text body, validated Reply-To, server-verified Turnstile hostname/action, exact origin checks, bounded request stream, honeypot and approximate three-attempts/minute rate limit. CORS is a browser boundary, not authentication.
- A separate Durable Object serialises delivery, caps new submissions at 100/day and remembers SHA-256 payload fingerprints/statuses for seven days. It stores no message text, email address or IP; the inbox holds the correspondence. Logs must not record payloads or secrets. Normal Cloudflare request metadata still exists under its account settings.
- Receipt is written **before** asking the provider to send. During the seven-day receipt retention period, same ID/content never causes another provider call, including concurrent requests. Changed content with a reused ID is rejected. Ambiguous sends remain uncertain; there is no automatic resend, queue or background retry.
- Success means the provider accepted delivery, not that Gmail inbox placement is independently proven. The UI says “accepted for delivery”. Production activation requires one observed Gmail delivery.
- Pending form cannot close accidentally. Scroll position, focus and background inert state are restored on close; no message is stored in browser storage.
- There is always a direct email alternative. A network timeout preserves the message and displays its reference without claiming success.

## Checks

From the repository root: `node --test tests/test_post_office_worker.mjs`.

Initial Cloudflare deployment is confirmed; real Gmail delivery remains unverified. `ENABLED=true` now permits the isolated live test. Do not connect the main footer until delivery to Gmail is verified.

## Deployment record — 26 October 2026

- Worker: `https://tffc-barry-post-office.anvilspringstien.workers.dev` (observed in successful build log).
- First build: `06d5bf82`; initial version `f50e1327-e2b3-4139-8c5e-0249a3ac1190`; sending initially disabled.
- Destination `tinfoilfacup@gmail.com` was shown Verified in Cloudflare.
- `post.tinfoilfacup.com` was shown Enabled in Email Routing. An incorrectly duplicated subdomain was removed and replaced with this exact name.
- Managed Turnstile widget created for `tinfoilfacup.com` and `anvilspringstien.github.io`. The apex entry also covers its subdomains under Turnstile hostname rules.
- Public site key: `0x4AAAAAAFm9afKRjLbSGnx5`. Secret never received or committed; Anvil added it directly as the Production secret `TURNSTILE_SECRET` and confirmed completion.
- Worker preview URLs disabled; previews do not receive the Production secret.
- `/beta/post-office-live-test.html` sends real messages. `/beta/post-office-preview.html` stays a non-sending design demo.
- End-to-end Turnstile validation, sending-provider acceptance and Gmail inbox receipt are **pending**. Local health fetch was not verifiable from this environment (HTTP 403); this is not evidence of application failure. Verify through the user’s browser before testing mail.
