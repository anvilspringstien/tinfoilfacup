# Daily TFFAC admin — Outreach & Website Audit acceptance gates

This is the repeatable morning routine. The existing **08:00 UK PR triage** is separate; the Outreach/Audit daily check is a second task. **Incomplete drafts and proposed website links must never be counted as completed delivery or publication.**

## Morning order

1. **Watchers & Ombudsman:** check scheduled Results (:17) and Draw (:37) runs, success versus observed scheduled launches, overall verification and competition/ground-health reports. Treat missing launches as operational amber even when successful runs are consistently stable. Never infer an overall all-clear from green PR checks.
2. **Mail:** read new club confirmations, delivery failures and reply queue; maintain Alerts. Club email is evidence to review, not a direct permission to patch protected competition data.
3. **Outreach:** up to **15 new club introductions**, each qualifying as an actual Clubfinder Campaign origin. Use the real postcode and verify the real Campaign number on site; exclude previously contacted clubs by searching Gmail Sent and Drafts.
4. **Website audit:** work in substantive, independently researched batches, normally 10–15; promote only independently evidenced official senior-club domains through the BETA-reviewed ledger and normal regressions.
5. **PR backlog:** inspect urgent club data and backend/ingestion/safeguard work before obsolete visual experiments. Carry useful old tests forward onto fresh main; do not bulk-merge stale branches.
6. **Hand-over:** record counts, blockers and PR links in Mission Control/Where We Were.

## Outreach — approved email shape

- Subject and headline: **Keeping your club details up to date**.
- Use the **actual original 600 × 226 transparent PNG banner**, named `tffc-combined-photo-and-crest.png`, as an **embedded inline image above the headline**, not a detached attachment, broken CID, temporary image URL or a recreated crest. The image must be undistorted: `width:100%;max-width:600px;height:auto`.
- Use the approved introduction wording: `Your club is already included in this season’s Tin Foil FA Cup.` Include the short custodianship explanation and grassroots support rationale.
- Include **Your current listing:** as a four-field table: **Club, Ground, Postcode, Website**. Copy these as currently shown in Clubfinder, not as assumed updates. Where absent, **No link currently shown**. Ask the club to confirm a candidate website separately.
- Verify every intended contact, actual postcode, starting Campaign number, current ground name and website state. Never presume every tested postcode returns Campaign 1.
- Include exactly **one full approved contact footer**, with name, project, site, email and telephone. Avoid duplicate Gmail signature blocks.
- Save **unsent drafts**. Reopen and visually inspect the **first** for banner, title, full listing and footer, then inspect the remainder. Match Gmail Draft/Sent counts; **zero unapproved sends**.
- Use the restored structured MIME workflow demonstrated by the Punjab United pilot on 23 November and subsequent successful batches. Preserve the original HTML styling and plain-text alternative, with the exact PNG as a related inline MIME part and matching Content-ID. Inspect every completed introduction and acknowledgement; replies retain the approved crest and full footer in the original thread. If the current connector cannot produce this structure, stop and delegate to the proven Work workflow rather than generating defective drafts. No unattended sending scripts.
- Reconcile introductions against Gmail Sent by unique club identity, not message count. A duplicate introduction, acknowledgement or follow-up must not increment the contacted-club total. Drafts never count as contacted. On 25 November the reported reconciliation was 304 unique clubs from 305 introductions, including one duplicate for Gosport Borough.

## Website audit — evidence before publication

Website, ground name, postcode and League & Tier are independent evidence categories. Record discrepancies separately; website verification must not silently change venue information or approve league membership. The approved season ledger from #732 is independent of tie-day eligibility. Club Audit integration is future work.

- Eligible starting clubs only; use current queue and prior verification ledgers to avoid repeats.
- Club-managed **senior first-team** site or trustworthy league direct cross-link with real evidence URL and review date; hold stale, youth-only, social, inaccessible and ambiguous matches. Never invent a URL from a club name.
- Record verified entries in `updater/club_website_verified_batch_XX.json`. Use `updater/club_website_bulk_promote.js` for reviewed changes and `updater/club_website_queue.js` to **regenerate** queue data; do not hand-edit derived JSON or competition records.
- Limit changes to BETA `CLUB_WEBSITES`; do not alter postcode, ground, fixtures, results, Call Signs, Camp​aign data, worker state or public site as a side-effect of website verification.
- Open a PR, run the publication, identity and regression checks, and merge only after green checks and review. Distinguish **proposed** from **merged** link coverage out of 651.

## Daily definition of done

Chat is the project headquarters for decisions and review; Work handles substantial engineering and the proven structured drafting workflow. Mission Control is the operational desk. Morning automations must report blockers rather than bypass quality gates. Do not append new evidence indefinitely to stale PR branches; retain dated findings and carry forward through a reviewed current branch.

Report **Outreach: researched / drafted / visually verified / user-sent** and **Audit: researched / verified / PR-open / green / merged** separately; never mark 15 as sent when 15 are merely draft objects. If an inline banner/footer or contact check is missing, say **blocked**, fix one test example, then proceed.

**Production protected; CLI is the Law; £0 budget; user reviews sends and merges.**
