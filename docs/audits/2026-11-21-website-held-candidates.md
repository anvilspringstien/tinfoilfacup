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


## Follow-up evidence audit — 23 November 2026 (no publication)

Three additional qualifying-origin candidates from BETA draft #718 were checked against live official club pages. These are **website identity and address checks**, not approval to publish the batch or to alter Clubfinder's historical ground records.

| Club | Evidence checked 23 Nov | Current BETA Clubfinder ground/postcode | Finding and decision |
| --- | --- | --- | --- |
| Nelson FC | https://www.nelsonfc.co.uk/visitors/ ; https://www.nelsonfc.co.uk/teams/ | The Daisy Arena, Victoria Park; BB9 7BN | Official senior club website explicitly gives the Daisy Arena, Victoria Park, Lomeshaye Way, BB9 7BN and has a men's 2026/27 team page. **Website evidence supported; no promotion.** |
| Nantwich Town FC | https://www.nantwichtownfc.co.uk/club-details-and-personnel/ ; https://www.nantwichtownfc.co.uk/the-swansway-stadium/ | Optimum Pay Stadium; CW5 5BS | Official senior club website gives **Swansway Stadium**, Waterlode, CW5 5BS; Clubfinder retains older/different sponsor name **Optimum Pay Stadium**. **Website identity supported; ground-name discrepancy HOLD** pending dated historical/venue review; do not rewrite ground metadata automatically. |
| North Ferriby FC | https://www.northferribyfc.co.uk/find-us ; https://www.northferribyfc.co.uk/ ; https://find-and-update.company-information.service.gov.uk/company/11050793 | Dransfield Stadium; HU14 3AB | Official club now calls the venue **Versa Sportswear Stadium**, Grange Lane, HU14 3AB, while Companies House retains Dransfield Stadium as registered office. **Website identity supported; sponsor-name discrepancy HOLD**; preserve original historical label until a separate dated venue-name decision. |

The official sources are first-party senior-club pages; a website crawl date does not imply a new announcement on 23 November. No site links, competition fixtures, custody, locations or postcodes changed. **Proposed today: 0; merged today: 0.** Draft #718 still proposes 15 website links, none released.

### Outreach quality gate — 23 November

- Gmail lists **14**, not 15, incomplete unsent outreach drafts from 20 November; the Nelson FC draft is not present in the current Drafts listing. Do not infer it was sent or deleted without evidence. Other 14 are preserved; no new draft created.
- No new club-introduction message found in Sent since 19 November (recent Sent entries are Ombudsman self-mail). Previous outreach from 17 November has a genuine inline 600×226 banner; 20 November drafts do not.
- Connector does not offer a proven working CID/inline image drafting path. **BLOCKED**. Prepared 0 new; verified 0 new; sent 0 new. Do not recreate, send, or discard existing drafts until the approved rendering workflow is demonstrated.
- Actual Campaign number must be independently confirmed per club using live Clubfinder before any draft passes. Do not rely on blanket Campaign 1 copy in the incomplete batch.

### GitHub scheduled-run evidence — 23 November

- Results scanner scheduled success: https://github.com/anvilspringstien/tinfoilfacup/actions/runs/45143924950 (09:05 UTC); draw scanner scheduled success: https://github.com/anvilspringstien/tinfoilfacup/actions/runs/45109039983 (03:58 UTC). These prove individual launches, not complete expected schedule coverage.
- Competition status publication **failed** after the 09:05 results run: https://github.com/anvilspringstien/tinfoilfacup/actions/runs/45144871886 ; a separate scheduled publication run at 08:29 succeeded: https://github.com/anvilspringstien/tinfoilfacup/actions/runs/45139053149 . The downstream failure remains open for investigation.
- 07:21 UTC Ombudsman email reports `no_recent_scheduled_launch` for both results and draw, with catch-up eligible. It predates the later 09:05 results launch. Do not mark schedule continuity healthy from successful isolated runs.
- `docs/admin-daily-checklist.md` still absent on `main`; draft PR #719 remains open. Release gate remains **CLI/regression unverified** in this run. No merge until CLI checks and BETA/production parity safeguards pass.

Carry forward: restore the exact inline Gmail banner and single footer, account for the missing Nelson draft, independently verify Campaign numbers, review sponsor-name differences without retroactive venue edits, inspect publication failures and scheduled-launch gaps, and run CLI regression checks before merging any website proposal.
