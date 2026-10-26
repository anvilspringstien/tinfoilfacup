# Club website audit

Website coverage is independent of the directory export request. Only reviewed
club-published evidence is promoted. Missing, conflicting or ambiguous candidates
stay in the queue; no domain is generated from a club name.

## 26 October 2026 checkpoint — missing-link coverage, batch 07

Reviewed twelve previously unreviewed missing origins, Bashley through Belper
Town. Eleven club-published destinations are approved; Beckenham Town stays
missing because the league-linked site could not be read. Earlier holds remain
separate and unchanged.

- Original qualifying-club coverage: 103 -> 114 of 651 linked.
- Missing links: 548 -> 537. Verified queue records: 147 -> 158.
- All 80 current clubs remain verified and linked; four existing-link holds remain.
- Basildon's expired custom-domain page links its working, current club-managed
  Pitchero destination. Bedfont FC and Bedfont Sports remain distinct identities.
- Evidence and the Beckenham hold are recorded in batch 07. Only the BETA website
  map literal changes; no ground, eligibility or competition data is edited.

## 23 October 2026 checkpoint — missing-link coverage, batch 06

Reviewed the first 30 missing qualifying-club websites. Batch 06 records 27 new
approved links with club-published evidence. Abbey Hey, Barking and Barton Town
remain missing pending an accessible, preferred current destination; individual
findings are recorded in the ledger's held section.

- Original qualifying-club coverage: 76 -> 103 of 651 linked.
- Missing links: 575 -> 548. Verified queue records: 120 -> 147.
- All 80 current clubs remain verified and linked. The four older existing-link
  holds below remain unresolved and unchanged.
- Only the website map literal changes in the BETA application. Eligibility,
  competition data and protected original Clubfinder are unchanged.
- Club website identity approval does not certify every ground/address claim on
  that website. Welwyn's first-team page specifies a 2026/27 ground while its
  homepage still mentions an older one; Totton also retains an older footer
  address. These are candidates for details checks, not manual competition edits.

## Proposed club-details check within outreach

The desktop presentation and donation flow are now user-accepted. Fold a simple
details check into the planned club introduction, beginning with current clubs.
This is a proposal: no messages are sent by this audit or this change.

1. Use the approved front-door crest, a named Anvil Springstien sign-off and the
   public https://tinfoilfacup.com/ link. Explain the supporter/grassroots purpose.
2. Include the exact club name, ground, postcode and official website currently
   shown by Clubfinder. Clearly identify them as our current published details.
   Ask for a simple all-correct reply or corrections; no account is required.
3. Invite the recipient to visit the site and enter their ground's postcode.
   Preflight that actual postcode through the three-choice search before sending:
   shared grounds and later entrants can mean their club will not appear. For a
   club without a reliable search route, use the email details panel instead of
   promising that postcode entry will display them. A dedicated club-view link is
   a possible later improvement, not an existing feature.
4. Resolve the recipient from the club's own current public general/secretary
   contact page and review the personalised message before authorised sending.
   Maintain a small private contact log: exact club identity, contact source/date,
   sent date, Gmail thread, response and any fields explicitly confirmed. Keep
   addresses and correspondence out of the public repository.
5. Distinguish public-source verification from direct club confirmation. Never
   label silence as confirmation. A delayed or absent reply does not block a
   website link already supported by reviewed public evidence.
6. Review replies against the sender's club role and public evidence, then feed
   supported corrections through the relevant CLI/data review route. No automatic
   inbox-to-live updates and no manual competition patches. Record what changed,
   its source and date; a confirmation only covers the fields actually checked.
7. Start with a small authorised pilot and review delivery, replies, corrections
   and workload before expanding. Optionally send one gentle follow-up after
   10–14 days; this is a proposed cadence, not a promise of a response or a
   scheduled task. Honour requests for no further contact.

The same invitation can introduce the product and improve its directory. There
is no new runtime feature, extra page load or club login in this first approach.

## 23 October 2026 checkpoint — older existing links

Reviewed all 31 existing mappings awaiting independent verification. Batch 05
records 27 approvals using club-published homepages, contact pages, stadium
information or club history. Existing URLs are preserved: this batch adds evidence,
not new links.

- All 80 current First Round Proper clubs remain verified and linked.
- Original qualifying-club coverage remains 76 of 651 linked; 575 are missing.
- Queue records independently verified: 93 -> 120.
- Existing links awaiting verification: 31 -> 4.
- The CLI promotion accepts zero new mappings and reproduces the BETA application
  byte-for-byte. Competition input bytes and all 651 eligible origins are unchanged.
- The queue was rebuilt against the competition input updated on 23 October.

Evidence and per-club review notes are in
`updater/club_website_verified_batch_05.json`. Its `held` section is deliberately
excluded from approved publication and records these follow-ups:

| Club | Finding | Next step |
| --- | --- | --- |
| Ashington FC | Club identity is corroborated at Woodhorn Lane, but the homepage contains numerous unrelated gambling/supplement links. | Site-health review before approval; no claim is made about the cause. |
| Barnoldswick Town FC | Existing custom domain could not be retrieved. The league and the club-managed Pitchero contact page agree on Silentnight Stadium, BB18 5LJ. | Review the differing replacement candidate: https://www.pitchero.com/clubs/barnoldswicktown/ |
| Carlisle City FC | Existing domain serves a parking/for-sale page. | Confirm an authoritative replacement; do not approve the parked domain. |
| Kendal Town FC | Homepage and contact page return HTTP 403 to the research reader. | Verify through an accessible club-published source or ordinary browser; no restriction was bypassed. |

These four existing mappings have **not** been replaced, removed or marked
verified. Their findings remain recorded for explicit review under the existing
mapping-conflict policy. No email was sent.

## 21 October 2026 checkpoint

- All 80 current First Round Proper clubs have independently checked official
  website links, including the 48 later entrants outside the original qualifying
  search list.
- Original qualifying-club coverage: 46 -> 76 of 651 linked clubs. The nearest-club
  eligibility list remains exactly 651 clubs.
- Across those original 651, 575 still need a link and 31 older existing links
  still need independent verification. A linked club is not automatically a
  verified club.
- The current-club ledger records 80 clubs and 25 explicit eligible-name aliases.
  The resulting website map contains 156 exact identities, including existing
  aliases; that number is not a club count.

Evidence is in `updater/club_website_verified_batch_04.json`. Source pages are
club-owned homepages, club information/contact pages, or the club's own published
links. Fleetwood's own Linktree links the main domain, news, ticket news and TV;
its main site rejected automated retrieval, so no restriction was bypassed.
Berkhamsted uses its club-managed Pitchero site, identified by its Broadwater
address. Doncaster, Sutton, Huddersfield and Oxford lookalikes were rejected.

## Repeatable CLI workflow

1. Run `node updater/club_website_queue.js --out updater/club_website_audit_queue.json`.
   Current clubs come first, followed by existing links awaiting verification,
   missing origin-club links, then already-verified records. Only reviewed aliases
   share evidence; similar names alone do not merge clubs.
2. Research candidates from public club, league or association sources. Read
   club-published identity/contact information. Record the exact club, HTTPS URL,
   evidence URL, verification date and notes in a versioned reviewed ledger.
   Record known canonical/eligible aliases explicitly. Escalate conflicting
   mappings and identity ambiguity; continue with other clear records.
3. Run `node updater/club_website_bulk_promote.js --ledger LEDGER.json --out /tmp/website-map.json`.
   This validates against qualifying identities plus recognised canonical fixture
   and archive identities. It rejects unknown clubs, unreviewed rows, unrelated
   aliases, credentials, insecure URLs, duplicate approvals and replacement of
   existing links. AFC prefixes remain meaningful (Blackpool is not AFC Blackpool).
4. Add `--apply-beta` to reproduce the BETA website literal. This CLI can change
   only that literal; it never writes competition.json, the protected original
   Clubfinder, or the nearest-club list. Repeating an approved ledger is a no-op.
5. Refresh the queue and the existing Stage C source report, run the website and
   identity checks, then use the normal reviewed PR, green-check and Pages route.

`club_website_bulk_audit.js` also accepts `--source-name` for provenance when a
permitted CSV comes from another source. Candidate matching is never approval.
A future permitted Non-League Network export can feed this same process.

This is a persistent work queue and CLI publication process, not an unattended
web-research service. Routine clear records can be handled under the agreed
process; only ambiguous evidence or existing-link conflicts need a user decision.
No email has been sent as part of the website audit.

