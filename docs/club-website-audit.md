# Club website audit

Website coverage is independent of the directory export request. Only reviewed
club-published evidence is promoted. Missing, conflicting or ambiguous candidates
stay in the queue; no domain is generated from a club name.

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
