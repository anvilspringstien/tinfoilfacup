# Website audit — 21 November 2026 (evidence-only, BETA)

Scope: revisit three held website candidates in the 17 November batch 26. No links are approved for publication. No competition, location, identity or production data changes.

| Club | Evidence inspected | Finding | Decision |
| --- | --- | --- | --- |
| Beckenham Town FC | https://scefl.com/sceflclub/beckenham-town ; https://find.englandfootball.com/club/73756 ; https://www.beckenhamtownfc.com/ | League and England Football independently name the same senior club and domain, but direct opening of the official domain was unavailable in the audit environment. | HOLD: do not promote until destination itself is usable. |
| Corsham Town FC | https://corshamtownfc.co.uk/ ; https://www.afccorsham.co.uk/news/corsham-town-season-tickets-2993504.html | Candidate senior domain currently renders a generic WordPress 'Project 1' sample/placeholder. AFC Corsham confirms a partnership with the distinct senior club but is not itself the senior website. | HOLD: do not promote placeholder or junior club site. |
| Boro Rangers FC | https://www.northernfootballleague.org/team/boro-rangers/ ; https://fanbanter.co.uk/9th-tier-club-announce-decision-to-withdraw-from-league-ahead-of-2026-27-season/ | League profile is historical; reported senior men's withdrawal on 30 June 2026. No verified active senior website to publish. | HOLD: historical/identity review needed, no competition edits. |

All evidence reviewed on 2026-11-21. These are candidate checks, not a claim that the websites are currently publishable. Historical source dates are not re-labelled as current confirmation.

## Safeguards and release gate

- No Clubfinder link changes in this PR; queue and verified batch files are intentionally unchanged.
- Before any later link promotion, confirm the actual live senior site and club-managed ownership, record a dated verified-ledger entry, and run `node updater/club_website_audit.js`, `node tests/test_club_website_publication.js`, and `python updater/audit_beta_production_parity.py` as applicable; inspect their CLI flags before invoking.
- Preserve all 651 eligible origins, all current website links, competition, custody, ground/postcode and production files.
- Outreach blocked: Gmail draft creation in this connector does not embed the approved 600×226 photo-and-crest banner as a valid inline MIME image. Fifteen existing 20 November drafts are unsent, missing banner/footer; do not duplicate or send.
- `docs/admin-daily-checklist.md` is not present on main as of this review. Restore/merge an approved daily checklist separately before relying on it.

## Follow-up evidence audit — 22 November 2026 (no publication)

This is a follow-up to BETA batch 27 (draft PR #718), not an approval to merge or a claim that all 15 candidate websites were rechecked today. Existing evidence for those 15 is recorded in `updater/club_website_verified_batch_27.json` on that draft branch. Gmail has 15 unsent, incomplete drafts for those recipients (created 20 November); no new outreach is prepared or sent because the currently available Gmail draft API cannot establish a working inline banner.

| Club | Primary source checked 22 Nov | Finding | Decision |
| --- | --- | --- | --- |
| Ossett United FC | https://www.ossettutd.com/club/contact/ ; https://www.pitchero.com/clubs/ossetttown/contact ; https://www.footballwebpages.co.uk/ossett-united/club-information | The club's own current contact page uses Ingfield, WF5 9HL; the club-linked Pitchero profile and Football Web Pages use WF5 9HA, which is the Clubfinder postcode. These conflict; do not silently replace the postcode or treat either as conclusively corrected. | Website identity supported; **postcode discrepancy HOLD** pending direct club confirmation and location review |
| Newcastle Town FC | https://newcastletownfc.co.uk/contact-us/ ; https://newcastletownfc.co.uk/matchday-info/ | Official senior club website and matchday contact identify the GRG Waste Stadium, ST5 3BX, matching the existing Clubfinder postcode. The website's club-secretary address also matches the current unsent outreach draft. | Website evidence supported for BETA review only; no promotion |
| Portishead Town FC | https://portisheadtownfc.com/contact/ ; https://www.westernleague.co.uk/teams/premier-division/portishead-town | Official senior club website identifies Bristol Road, BS20 6QG and current senior team contacts; league independently confirms Bristol Road Playing Fields. | Website evidence supported for BETA review only; no promotion |

The first-party pages above were checked against indexed/current web results on 22 November; do not interpret a crawl timestamp as a new club announcement. No production/BETA mapping, club identity, location, result or custody data is modified by this evidence-only update.

**CLI release gate (not run in this automation environment):** `gh` is unavailable here. Before merging #718 or promoting any links, inspect the branch diff, check its base is current, run `node updater/club_website_audit.js`, `node tests/test_club_website_publication.js`, and `python updater/audit_beta_production_parity.py` with their supported flags, and confirm all 651 origins and existing mappings are preserved. CLI is the Law; do not represent this evidence review as passing regressions.
