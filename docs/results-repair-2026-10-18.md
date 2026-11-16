# Results repair investigation — 18 October 2026

Status: isolated repair; no merge or deployment authorised. Draw is a separate task.

## Evidence and limits

- Failed scheduled Results run: https://github.com/anvilspringstien/tinfoilfacup/actions/runs/39052574769
- Event and actual checkout SHA: `45f3e36d590f01ccbfcfb224bfacadb019644b71` (both run.json and checkout log agree).
- Repair baseline from authenticated CLI-supplied Git bundle: `0a3584ca27653899b3f60620f917c848318daa52`.
- The failed run passed competition_regression_guard.py, then failed the DL5 rendered custody assertion.
- Artifact summary at 2026-10-17T17:13:02.288208Z: 32 known ties, 28 FWP archive observations, 28 live observations, 28 classified results, zero blocked records. The shadow report had zero proposals and zero issues.
- The artifact upload log confirms only the two summary reports were retained. The exact candidate competition.json, rendered page and source payloads were not retained. They cannot be recovered from this bundle.
- Independent FA evidence: https://www.thefa.com/news/2026/oct/17/20261017-fac4qr-wrap reports a 5–0 Fylde victory.
- The 18 October FWP round source parses as FT, AFC Fylde 5–0 Atherton Collieries, dated 2026-10-17. This independently corroborates progression; it does not prove the contents of the lost candidate. Offline captures and checksums are in tests/fixtures/results-repair/README.md.
- Earlier cloud device authentication was policy-blocked. In the fresh session on 18 October, device authentication and direct CLI repository reads succeeded as anvilspringstien. Current main was verified as 13d0e1f97951281cdc91bf0eb1b128c06e5bc89c; the prepared repair was absent from remote branches, PRs and main. The existing repair commit was cherry-picked onto that main in an isolated review checkout. No credentials were transferred.

## Confirmed causes

1. The DL5 rendered regression recognises the Atherton replay victory but permanently expects Atherton after it. It does not account for a later FT Fourth Qualifying result. Stats contains the same stale expectation. Other Campaign guards also freeze earlier custodians or scan unrelated nearby cards.
2. The pending replay map held 19:45 in commit `4479544`; commit `96ecbc7` held both the 3–0 result without kickoff/venue and a pending replay fixture with 19:45. By `c7cc169` the pending replay was gone, while the result still lacked kickoff. The original 3 October draw retains its separate Shawe View venue.
3. auto_round_results.merge_result previously copied only the result observation. Classification preserves scores/date/source but does not attach exact scheduled fixture metadata. stage_preceding_replay_candidates calls the same merge path. Replay sync prunes terminal replay fixtures without first transferring their schedule to results.
4. The enrichment stage selected First Qualifying replays only, and match-link discovery expected `/fa-cup/`; current source match paths use `/emirates-fa-cup/`. Thus later replay kickoff recovery was unavailable. The renderer deliberately falls back to Kick-off TBC when neither the result nor pending replay supplies a time.
5. The winner helper could derive a custodian from scored records before full time. It now requires a terminal status, source attribution, and complete integer scores, preserving separately evidenced scoreless advancements and explicit awards.

## Repair boundaries

- No manual changes to competition.json or the Beta snapshot.
- Exact home/away, date and round matching retains attributed kickoff and venue metadata before pruning. Contradictory populated metadata fails closed. Original/replay metadata cannot cross dates or orientations.
- All qualifying replay results can recover missing times from exact dated, oriented source match pages. A missing/ambiguous time remains a publication blocker.
- FA-ordered full replays can use an original-round-labelled match page only when the existing reviewed exceptional disposition exactly matches their identity and result. This preserves the Mulbarton exception rather than inferring new replay ancestry.
- Frozen renderer scenarios prove Trafford -> Atherton -> Fylde, including live/HT/void/unsourced/incomplete-score rejection, no bypass of an unresolved replay, and original/replay ordering, date, 19:45, ground/postcode and 3–0 result preservation.
- Existing milestones, ancestry and venue assertions remain. Later proven results advance expectations. HP7 selects the intended Campaign before checking that its resolved ancestry has no Replay details TBC; unrelated nearby clubs' new draws cannot trip that ancestry guard. HP7 Stats' offline postcode response map gains Salisbury's existing ledger coordinates after that verified later progression; the mileage assertions remain unchanged. The production UI Challenges bridge expectation follows the same verified later results; all bridge, identity and geometry assertions remain.
- Future Results diagnostics retain the exact checkout input, candidate competition/page and public source HTML, as well as existing summaries. Uploading diagnostics cannot approve publication.

## Verification

See results-repair-commands.md for the actual CLI commands and test coverage. The reconstructed candidate uses the captured 18 October source page through the real parser/classifier/merger in a temporary checkout. It is explicitly not represented as the lost 17 October candidate. Production input bytes are checked unchanged after the reconstruction.

A live enrichment exercise against the canonical baseline and cached public match pages recovered all 20 missing later-round kickoffs, checking 52 qualifying replays total. It fetched 20 exact match pages, changed 195 alias copies' kickoff records, and left zero active venue records changed and zero active home venues unresolved. All writes for this exercise were under /tmp.

## Publication

Open the Results PR separately. Require all applicable GitHub checks and explicit user approval before any merge or deployment. Do not use this PR to patch competition scores manually, relax fixture completeness, or repair Draw ingestion.

## Health and reconciliation review follow-up

PR #471's first GitHub run passed the real Results scan and both offline repair
jobs. Health and reconciliation separately failed because neither imported the
active round before requiring zero overdue results: health synchronised older
chronology, while reconciliation only imports preceding scoreless replay evidence.
Both now invoke the existing guarded active-round Results importer before their
health audit. Reconciliation remains contents:read, restores its checkout inputs
with an EXIT trap, enriches replay times and runs alias/competition/snapshot guards
before renderer/Stats validation. Health retains its existing main-only publication
boundary and all subsequent regression checks. No health thresholds or source
completeness rules are relaxed. The captured-source candidate test now also runs
the real competition health audit; it reports zero overdue and zero critical issues.
