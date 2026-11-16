# Bulk publication after independent verification

The candidate CSV from `club_website_bulk_audit.js` is **never** publication input. Research and verify official websites first. Create a reviewed JSON ledger:

```json
{
  "schema_version": 1,
  "verified": [
    {
      "club": "Example FC",
      "url": "https://example.org/",
      "evidence_url": "https://example.org/about",
      "verified_on": "2026-10-12",
      "status": "verified_official_club_site"
    }
  ]
}
```

Then run `node updater/club_website_bulk_promote.js --ledger reviewed.json --out /tmp/club-websites-reviewed.json`.

The generator checks **exact eligible club identity**, duplicate approvals, HTTPS, dated independent evidence, status, and conflicting existing links. It emits a sorted **proposed** map plus accepted identities. It does **not** edit Clubfinder, open a PR or claim a source was independently verified. A reviewer must check that the evidence actually supports each identity before transplanting the proposed map into the BETA `CLUB_WEBSITES` constant and running regression tests. Never overwrite existing URLs silently.

Evidence can be an official club page or a trusted football league's direct link to the club's website; candidate-source directory matches alone do not suffice.
