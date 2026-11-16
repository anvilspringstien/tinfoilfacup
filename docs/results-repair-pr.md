Results ingestion can legitimately advance the DL5 Campaign from Atherton Collieries to AFC Fylde after the verified 17 October 5–0 result, but the rendered and Stats guards freeze the earlier custodian. The same journey lost its replay's verified 19:45 kick-off when the result omitted schedule metadata and the completed pending replay was pruned.

This repair tests custody chronologically, blocks live/unsourced/incomplete results from advancing custody, transfers attributed exact-match metadata before pruning, and recovers qualifying replay times from exact source match pages. Existing original/replay, ancestry and venue assertions remain. HP7 checks its selected Campaign instead of rejecting a legitimate new draw elsewhere among the nearby choices. Results diagnostics now retain input, candidate and source payloads for future failures.

Independent evidence: [the FA's official round report](https://www.thefa.com/news/2026/oct/17/20261017-fac4qr-wrap) confirms Fylde's 5–0 win, agreeing with the captured full-time FWP source. The lost 17 October candidate was not archived; the tested candidate is explicitly reconstructed from the captured 18 October source through the importer.

Validation:

- 54 unit checks across Results metadata, replay sync, staging, source validation, publication boundaries and guard preservation.
- Shared round-state, round-source, Extra Preliminary ancestry and shadow producer regressions.
- Published-snapshot renderer/Stats checks and the reconstructed candidate's competition, alias, kickoff, historical journey/venue, systemic replay, all-origin integrity, HP7, EX8, KT21, Law 2 and production UI regressions.
- Live enrichment exercise recovered all 20 missing later qualifying replay times; 52 qualifying replays checked. All exercise output stayed in /tmp.

Details and actual commands: `docs/results-repair-2026-10-18.md` and `docs/results-repair-commands.md`. A read-only CI workflow repeats the offline checks.

No competition.json/Beta data patches. No Draw changes or relaxed completeness counts. **Do not merge or deploy without passing applicable GitHub checks and explicit owner approval.**
