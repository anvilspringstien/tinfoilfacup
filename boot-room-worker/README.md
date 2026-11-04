# TFFAC Boot Room — invited service Shed

A separate Cloudflare Worker and SQLite Durable Object for the first invited chat test. No production TFFAC page, Campaign, competition data, counter, Likes service or existing visual prototype is changed. No public navigation button or invitation delivery is included. Deployment is not performed by this PR.

## What works

- One shared room; closed by default. Landlord opens it for up to twelve hours, supplies next-opening text, or closes immediately. Server rejects messages/hearts after closing even on existing sockets; a closing alarm updates connected clients. Reading and reporting remain available to invited members when closed.
- One-use, random 256-bit invitations issued by the landlord, with ten reserved test places maximum. Invitations and sessions are stored as hashes, expire seven days after issue and are never put in URLs. Successful redemption sets a Secure, HttpOnly, SameSite=Strict host cookie. The landlord allocates pigeon names; participants cannot rename themselves or claim another identity in messages. Logout revokes that session; suspension revokes it and closes existing connections.
- Live WebSocket broadcast, replies, idempotent hearts, private reports, moderator removal and suspension. Messages use textContent, not interpreted HTML. Reporters are visible only to the landlord. Message removal also clears hearts; later replies to removed messages are rejected.
- Last 200 messages, up to seven days. Daily cleanup alarm removes expired records even without visitors. Cloudflare infrastructure backups can outlast application retention; this is not a promise to erase platform backups immediately. No uploads, private messages, automated Barry/AI, email or external services.
- Five actions per ten seconds per participant, 2,000 accepted actions/day room-wide, 200 WebSocket joins/day, two connections per participant and twenty total. Limits persist across object restarts. WebSockets use the hibernation API and attachments. No automatic reconnect loop, polling, ping timers or third-party scripts. Returning to a visible room or restoring a page performs one fresh state check and reconnect; background/offline/disconnected inputs are disabled, and typing resumes only after a fresh socket snapshot. Draft text survives connection changes.
- Simple service test UI at `/`, private landlord data behind `/admin` plus Bearer-authenticated API. Admin secret stays only in module memory; Lock/navigation clears it. All forms use same-origin JSON requests, strict CSP, no-store responses and no credentials in query strings. Real browser/device checks remain necessary after deployment.

**Identity boundary:** these are invited Boot Room identities, not verified TFFAC Campaign identities. Call signs and custodians are deliberately not presented as verified. A call sign copied from browser storage is not proof of ownership. Secure Campaign association is a later stage, before integration with the established visual prototype and public button.

## Checks

Node 24:

```sh
node --test tests/boot-room.test.mjs tests/boot-room-client.test.mjs
npx --yes wrangler@4.156.1 deploy --dry-run --config boot-room-worker/wrangler.jsonc --outdir /tmp/tffac-boot-room-build
```

For a local end-to-end check, install the test tools outside the repository:

```sh
npm install --prefix /tmp/tffac-boot-tools --no-save wrangler@4.156.1 ws@8.21.0
node /tmp/tffac-boot-tools/node_modules/wrangler/bin/wrangler.js dev --config boot-room-worker/wrangler.jsonc --ip 127.0.0.1 --port 8789 --var ADMIN_TOKEN:local-test-only
# In another terminal:
node tests/boot-room-live-check.mjs http://127.0.0.1:8789 /tmp/tffac-boot-tools/node_modules/ws
```

The integration script refuses non-loopback hosts and uses only the literal local fixture credential. It creates two independent authenticated WebSocket clients and verifies cross-client delivery/replies/hearts, refresh persistence, report/removal, suspension, closure, logout, invitation replay and origin/admin rejection. These are protocol clients, not a claim of an iPhone/desktop browser test. This managed development host required a loopback-only interface-enumeration workaround for Wrangler; the workaround is not part of the Worker or deployment. The final functional check uses the real local Wrangler/workerd runtime.

## Owner Cloudflare setup — after checks

Use Workers Free, the same GitHub repository, a **new** Worker named `tffac-boot-room-shed`, root `/`, no build command:

- Production deploy: `npx wrangler@4.156.1 deploy --config boot-room-worker/wrangler.jsonc`
- Preview command: `npx wrangler@4.156.1 preview --config boot-room-worker/wrangler.jsonc`

Add a **new, separate** random `ADMIN_TOKEN` as a Production runtime Secret and retain it privately in the password manager. Do not reuse the Likes/Post Office tokens, put it in build variables or paste it into chat. Previews have isolated Durable Object storage and no admin secret unless explicitly supplied a separate test secret. No production secrets should be copied into Previews Base.

After deployment verify `/health`, then `/admin` unlock. Issue separate one-use invitations for desktop and phone, enter each privately at `/`, open briefly, test both directions and reload, close it, confirm posting stops on both, then verify removal, reporting, suspension and logout. Keep closed afterwards. Do not invite others or change the public app yet. No real opening hours are agreed; fixture/draw automation is absent.

## No-cost boundary and remaining promotion work

Cloudflare Free supports SQLite Durable Objects and WebSocket hibernation. All account-level request, compute and storage allowances are shared; application caps are not an absolute defence against malicious traffic or a promise of unlimited chat. Free limits cause failed operations rather than paid overages while the account remains Free. No paid plan, resource or upgrade is required/authorized by this implementation. Review actual Cloudflare metrics during an invited opening, including impact on existing services, before public promotion.

Before an invited public-facing opening: agree human moderation/coverage, privacy wording and retention; verify real mobile cookie/reconnect behavior and alarm expiry; review identity association and abuse controls; integrate and refine the established visual prototype; choose the button placement. Long-term histories, authenticated Campaign association, account recovery and automatic schedules are intentionally not claimed as complete.

References checked 3 November 2026:
- https://developers.cloudflare.com/durable-objects/platform/pricing/
- https://developers.cloudflare.com/durable-objects/best-practices/websockets/
- https://developers.cloudflare.com/workers/previews/configuration/


## Boot Room design integration — 3 November

The live service now uses the approved Boot Room prototype's dark frame, cream/teal conversation, sender-aligned bubbles, reply excerpts, pinned composer, closed-room next-opening notice, house rules and Barry landlord identity. The two crest images reuse the exact existing optimized public TFFAC assets (no new image downloads or generation in the repository); CSP permits images only from tinfoilfacup.com. The standalone visual Sites prototype remains unchanged.

### Entrance and conversation

`/` is the Boot Room entrance on both desktop and phone: one centred frame with Barry's introduction, opening details, house rules and a link to `/chat`. `/chat` retains the approved scrolling conversation and sticky room status, with a pinned composer only while open. The previous desktop introduction beside the chat is removed. Existing invitation cookies work across both paths; visiting the entrance does not leave the room or consume another invitation. `/admin` remains the landlord view. No public My Campaign button is added by this isolated change.

The public read-only `GET /api/doors` returns only `open`, `until` and the landlord's `next` opening text. Conversation, people, reports, usage and credentials remain protected. The entrance checks on load, foreground restoration, network return or a manual Check doors tap, without opening a WebSocket or polling. Opening state is checked again by the existing authenticated conversation flow on entry. If opening details cannot be checked, the entrance shows that limitation instead of asserting that the room is closed.

Report receipts are personal: snapshots expose only whether the current participant reported a message, never the report list or another reporter's identity. A confirmed report changes its message control to Reported and adds a private receipt beneath it, including after reconnect/reload. Pending transmission is labelled Sending. Closed rooms still allow reports while replies/hearts/typing are disabled. The landlord view has a visible checking state and last successful refresh time.

The public navigation/button, existing invitations/sessions and room opening state are unchanged. Browser design QA uses clearly labelled sample messages on desktop and a390x844 Chrome frame, not live room data or Safari. Live phone verification remains appropriate after deployment.

## Opening advert and sample conversation — 4 November

The entrance advertises the planned 7 November 09:00–23:45 UK opening and Monday draw session. The chalkboard is presentation copy in `ui.mjs`; it does **not** schedule or open the room. The live status below it is checked separately. Barry must open the room manually and choose the actual deadline. The bounded manual opening now permits up to 16 hours in quarter-hour increments (14.75 hours covers 09:00–23:45); server expiry remains exact, regardless of the advert’s “ish”. Update the chalkboard after the event.

`/demo` is a public, entirely fictional 25-post qualifying-round conversation with demo call signs and custodian rows. It has no script, forms, credentials, live-room API access or writes, and is clearly labelled as a sample throughout. It never reads or inserts live messages. `Read Recent Chats` leads to this sample for the invited launch; the smaller live-room link retains the existing invitation/session journey. Root and room use the same centred frame on phone and desktop. Existing invitations, sessions, moderation, message retention and closed-room state are preserved.
