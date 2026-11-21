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
