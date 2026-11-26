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

The generator checks **exact eligible club identity**, duplicate approvals, HTTPS, dated independent evidence, status, and conflicting existing links. It emits a sorted **proposed** map plus accepted identities. By default it does not edit Clubfinder. After reviewing the evidence, pass `--apply-beta` and, for authorised Public changes, `--apply-public`. Both switches may be used together. The CLI validates each target against its own existing mapping before writing either build. These switches edit only the website literals. Regenerate the queue with `node updater/club_website_queue.js --out updater/club_website_audit_queue.json` and run publication regressions.

Evidence can be an official club page or a trusted football league's direct link to the club's website; candidate-source directory matches alone do not suffice.
