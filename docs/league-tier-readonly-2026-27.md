# Tin Foil FA Cup — 2026–27 League & Tier audit (read-only)

## Purpose

Recover the interrupted League & Tier investigation as a reproducible,
evidence-based candidate registry and exception queue. This is **not**
a Clubfinder promotion, Mission Control deployment or Giant Killer release.

**No approved Tier, no badge award, no mutation of live club data.**

## Population and identity

- The original named population is the 651 unique clubs in
  `tester-club-postcodes.csv`. It is a roster, **not** a source for league
  membership. Entry round is never used to derive a league or Tier.
- The 2026–27 `journey-club-registry.json` contributes additional identities;
  duplicates of the original roster are not copied into the candidate view.
- The proposed match key ignores accents, punctuation, and **trailing** FC/AFC,
  but preserves leading AFC and the rest of the club name.
- Ambiguous matches and alternative-club allocations never receive a Tier.
  Fuzzy names are only suggestions in the queue, not asserted matches.
- Historic 15 November research reported **629 matches / 22 exceptions**.
  The previous full match table was not retained.

## Initial FA allocations

**The Football Association, 14 May 2026**:
[NLS Step 1–4 allocations (original PDF)](https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/nls/nls-1-to-4-club-allocations-2026-27---v1-140526.ashx)

Source ledger:
`updater/league-tier-sources/fa-nls-steps-1-4-2026-27-initial.csv`.

It transcribes 336 original allocation places:
- Step 1: 24 clubs, proposed overall Tier 5
- Step 2: 48 clubs, proposed overall Tier 6
- Step 3: 88 clubs, proposed overall Tier 7
- Step 4: 176 places, proposed overall Tier 8

The combined initial list contains **335 definite club names and one
provisional alternative**: “Guernsey or Peacehaven & Telscombe”.
Neither club is assigned a Tier by that ambiguous source.

These are **initial allocations, not verified current membership**. The FA
states that allocations may be amended. Every match is a *candidate for
review*, even one with an exact source name. The ledger must be reconciled
against later official decisions before any approved Tier exists.

### Steps 5–6

[FA Steps 5–6 allocation PDF, 14 May 2026](https://www.thefa.com/-/media/thefacom-new/files/competitions/2026-27/nls/nls-56-club-allocations-202627-v1-140526.ashx)

The ledger `updater/league-tier-sources/fa-nls-steps-5-6-2026-27-initial.csv`
transcribes the allocation tables on pages 1–10. Appendix pages 11–12
describe relegation and reprieve criteria and do not contribute memberships.

- Step 5: 320 places, proposed overall Tier 9.
- Step 6: 340 places, proposed overall Tier 10.
- Five places are provisional. AFC Knowsley, Halewood Apollo and Crewe
  were marked pending promotion. Harlow Town's place was subject to
  compliance with Rule 13.B. The Southern Combination also listed the
  Guernsey/Peacehaven alternative. The two FA PDFs list one
  alternative place each, at Steps 4 and 5.
- Retained reprieves marked `[2]` are named initial allocations.
  Western Football League Step 6 is recorded as Division One, the
  [league's published name](https://www.westernleague.co.uk/).
  The FA PDF labels the column Premier Division (WL1).
- Counts use the numbered club rows, including Norwich United and
  Christchurch where the source repeats a row number.
- Across both PDFs there are **996 places**. Of the 651 Clubfinder entries,
  **626** have a single candidate and **25** remain for review
  (18 missing, four with multiple source allocations and three provisional).

## Official 2026–27 membership for Tiers 1–4

| Tier | Division | Clubs | Official season evidence |
| --- | --- | ---: | --- |
| 1 | Premier League | 20 | [2026–27 fixture list](https://www.premierleague.com/en/news/4675097/all-380-fixtures-for-season-202627-premier-league-season), 19 October edition |
| 2 | EFL Championship | 24 | [EFL Championship table](https://www.efl.com/news/2026/november/21/sky-bet-championshi-results-table-and-stats/), 21 November |
| 3 | EFL League One | 24 | [EFL League One table](https://www.efl.com/news/2026/november/21/sky-bet-league-one-results--table---stats/), 21 November |
| 4 | EFL League Two | 24 | [EFL League Two table](https://www.efl.com/news/2026/november/21/Sky-Bet-League-Two-results--table---stats-/), 21 November |

The Premier League opening round names all 20 clubs. Each EFL table lists
24 clubs. The two membership ledgers under `updater/league-tier-sources/`
contain one source URL and date per club. The League One table lists
MK Dons, recorded in the ledger under the full name
[Milton Keynes Dons](https://www.mkdons.com/news/2026/may/02/league-one-awaits/)
confirmed by the club for the same season. The general matching rules are unchanged.

Membership ledgers provide an explicit `tier` and leave `fa_step` empty.
The existing NLS ledgers provide FA Step, from which the CLI derives
overall Tier 5–10. The candidate report uses `proposed_tier` for both
evidence types and keeps every `approved_tier` empty.

## Post-May evidence through 24 November 2026

`updater/league-tier-sources/nls-2026-27-post-may-evidence.csv` records
later decisions, adopted constitutions and senior league participation
separately from the May PDFs. Each row names the audit identity and the
club as listed by the source. Publication and effective dates are recorded
where the source gives them. An undated source uses the date it was
checked. The optional identity URL documents the name or team connection.

The CLI considers this evidence only for the exact recorded audit
identity. A formal allocation decision has precedence over an adopted
constitution, followed by a league's season membership or fixture record,
then the May allocation. A publication or a separately stated effective
date after the audit cut-off delays application. Equally authoritative
disagreements and conflicts with the professional membership ledger
stay in the review queue. The CLI preserves both original FA ledgers,
keeps name suggestions for review and proposes no Tier for a withdrawal.

The FA allocation release still points to the May documents. The
amendment search covered the FA and individual league notices, including
the [Spartan South Midlands amendments](https://ssmfl.uk/news/statement-constitution-amendments-12062026),
[Wessex appeal outcomes](https://www.wessexleague.co.uk/appeal-updates),
[North West Counties AGM](https://nwcfl.com/news-articles.php?id=10153)
and [Western League directory](https://www.westernleague.co.uk/teams).
This is the set of changes found and verified in this pass. The public
sources checked did not yield a consolidated replacement for the May PDFs.

| Population | Baseline candidates | Post-May candidates | Post-May exceptions |
| --- | ---: | ---: | ---: |
| Original Clubfinder | 626 of 651 | 650 of 651 | 1 |
| Companion-only Journey registry | 92 of 92 | 92 of 92 | 0 |
| Combined | 718 of 743 | 742 of 743 | 1 |

The 25 original exceptions now have evidence-backed candidates.
For example, the [Isthmian League](https://www.isthmian.co.uk/match/6a59064dce9ef452b61f3494)
and [Southern Combination](https://fulltime.thefa.com/index.html?league=840602727)
confirm the Peacehaven and Guernsey play-off outcome. The
[Spartan South Midlands table](https://fulltime.thefa.com/index.html?league=522238936&selectedCompetition=0&selectedDivision=116590296&selectedFixtureGroupKey=1_43894481&selectedSeason=584103502)
identifies the lower-division Royston Town and Stotfold rows as reserve sides.

The comparison against all 718 former candidates identified four affected
Clubfinder clubs.

| Club | May candidate | Post-May evidence |
| --- | --- | --- |
| Bradford Town | Western Premier, Tier 9 | Hellenic Premier, Tier 9 after an [upheld appeal](https://bradfordtownfc.com/club-statement-lateral-league-movement/) |
| Litherland REMYCA | NWCFL Division One North, Tier 10 | Premier Division, Tier 9 after an [FA reprieve](https://www.nwcfl.com/news-articles.php?id=10150) |
| Wells City | Western Division One, Tier 10 | [Western Premier Division](https://www.westernleague.co.uk/teams), Tier 9 |
| Boro Rangers | Northern League Division One, Tier 9 | [Senior resignation](https://www.northernfootballleague.org/news/boro-rangers-submit-resignation/) on 30 June. Hold the proposed Tier until there is evidence of an active replacement senior allocation. |

### Historical 629/651 comparison

The 15 November tally was described as a unique-name match against the
FA allocations and referred to spelling differences, duplicate names and
the provisional play-off place. The prior discussion and repository
history yielded no per-club table, input snapshot or matching settings
for the 629. The rerunnable baseline produces 626 candidates, 18 missing
matches, four competing matches and three provisional cases. The 25 named
resolutions and Boro Rangers withdrawal explain the move from 626 to 650.
The original three-club difference remains unattributed.

Do **not** infer a club's Tier from its FA Cup entry round, historic result,
postcode, playing venue, or a different season's league table.

## Reproduce audit

```bash
python -m unittest discover -s tests -p 'test_league_tier_readonly.py' -v
python -m updater.league_tier_readonly --as-of 2026-11-24 --out /tmp/tffac-league-tier-2026-27
```

Produces five files under the explicitly supplied `--out` directory:

1. `league-tier-candidates-2026-27.csv`: **every original club** plus
   companion-only journey clubs; empty `approved_tier` throughout
2. `league-tier-review-queue-2026-27.csv`: each unresolved case and the evidence required
3. `league-tier-audit-summary-2026-27.json`: counts, provenance and changes against the baseline
4. `league-tier-audit-2026-27.md`: concise human summary
5. `league-tier-exceptions-2026-27.md`: named remaining exceptions and prior cases resolved by the later evidence

GitHub's `League and Tier — 2026-27 read-only audit` workflow runs the
tests and uploads the report as an artifact. The workflow has
`contents: read` permissions and does not commit or deploy anything.

## Promotion boundary

1. Review the sourced candidates and apply season-specific identity decisions through the normal
   Construction Law route. Only a separately approved reviewed registry may
   contain `approved_tier` values.
2. Expose it in Mission Control's eventual Club Audit as **read-only first**.
3. Independently develop Giant Killer regression tests against canonical
   cup ties, resolved winners and historical Tier for each match. Keep the
   Challenge disabled until all promotion and safety gates pass.

The present outputs are not used by Public, BETA, Keep, Barry Air, the results
watchers, Clubfinder, Stats or Mission Control. Nothing is auto-promoted.

## Phase 4 evidence review

The itemised readiness report covers all 742 candidates and the Boro
Rangers hold. This pass rechecked all 996 initial entries against their
published FA PDF tables and all 92 professional entries against the four
season-specific league rosters. It also rechecked the 28 post-May candidates
against their exact audit identity and source tuple. The CLI checks each
candidate's source, club, league, division, Tier and FA Step, including a
blank FA Step for professional memberships. The published May allocations
remain subject to appeals. No consolidated replacement was located.

| Evidence and matching method | Candidates | Readiness |
| --- | ---: | --- |
| Initial FA allocation, exact name | 19 | Needs an adopted constitution or equivalent official season confirmation |
| Initial FA allocation, trailing FC/AFC only | 597 | Same requirement, with a recorded review of the exact suffix rule |
| Initial FA allocation, spelling or punctuation | 6 | Needs a named identity check and season confirmation |
| Professional season membership, exact name or trailing suffix | 91 | Eligible for a recorded season-membership review |
| Professional season membership, documented publisher alias | 1 | Verify MK Dons against the full Milton Keynes Dons identity |
| Post-May allocation decision | 2 | Review each later decision and its timing |
| Adopted league constitution | 2 | Review each named identity and constitution |
| Official league participation | 24 | Review the identity link and what period the evidence actually covers |

The six spelling cases are Bishop's Stortford, Corinthian Casuals, Cray
Valley (PM), Hollands & Blair, Larkfield & New Hythe and Weston-super-Mare.
The 28 post-May rows include all previously resolved duplicates and three
changed prior candidates. The named report flags those 35 candidates for
individual membership scrutiny. It also retains Boro Rangers with no
proposed Tier. Review senior identity independently of venue, postcode
and website verification. Those fields play no part in the CLI's checks.

### Tier on the day of a tie

The readiness CLI compares scored, completed results and replays in the
competition snapshot through 24 November. It excludes walkovers and other
non-played results. It flags disputed dates, leaves a label shared by two
clubs unresolved and lists unlinked result labels. Future scheduled ties
are outside that comparison.

Of 693 clubs with an unambiguous dated scored result in the snapshot, only
Bradford Town has a documented membership start in the evidence under
review. Its immediate move on 12 June predates the recorded 8 August tie.
A start date alone leaves continuity through the tie date to be reviewed.
The [Premier League AGM](https://www.premierleague.com/en/news/4673099/the-202627-premier-league-season-officially-starts/)
formalised membership for the 20 Premier League candidates on 5 June.
Those candidates have no scored FA Cup ties in this snapshot. The
[EFL opening weekend](https://www.efl.com/news/2026/june/25/the-2026-27-efl-fixtures-are-here/)
is a schedule milestone and the November division lists establish season
membership. The present evidence carries no approved validity intervals.
The FA's [round dates](https://www.thefa.com/news/2026/jun/05/round-dates)
are useful for planning and do not supply a tie's actual played date.

Two dated-result issues merit separate review before any tie-time use.
The Kendal Town–Heaton Stannington preliminary round result has two dates
in the snapshot. The bare Sutton United label could link to either audit
identity, and the qualified labels need a recorded cup identity link.
The readiness report records both problems without changing competition
data or using the apparent round of entry to choose a club.

### Proposed approval workflow

1. **Prepare a review manifest via the CLI.** Pin the source commit, input
   hashes, audit date and season. Emit the candidate's stable club
   identifier, exact registry and source names, league, division, Tier,
   optional FA Step, authority, evidence URLs and dated source snapshots.
   Carry the source-to-registry identity decision explicitly. Re-running
   with the same pinned inputs yields the same proposed manifest.
2. **Record the review decision.** A reviewer records `approve season
   membership`, `approve dated interval` or `hold`, with their
   identity, timestamp, rationale and the manifest digest. For an
   interval, require a sourced inclusive start, exclusive end or explicit
   date through which continuity is verified. Publication/observation
   dates cannot substitute for an effective date. Use a reviewed
   correction or supersession record when a later decision changes
   membership. A reviewer can accept simple suffix matches as a batch;
   named identity links, competing evidence and amendments are reviewed
   individually.
3. **Validate and append through the CLI.** Preview the exact changes;
   reject stale digests, absent sources, unresolved identities, conflicting
   intervals, invalid league/Step/Tier tuples and approvals outside the
   documented period. An explicit later apply operation appends reviewed
   decisions to a version-controlled ledger. Repeated identical
   decisions are idempotent. Corrections supersede prior entries while
   preserving their evidence, reviewer, timestamp and commit lineage.
4. **Resolve match-day Tier by stable identity and actual played date.**
   A future consumer requires one applicable dated decision for each
   participant. A season-only decision has no match-day effect. Missing
   dates, aliases, bounds or conflicting decisions keep that use pending.

This phase implements the read-only reviewer only. The proposed approval
ledger, writes and publication remain for a separate decision.

```bash
python -m updater.league_tier_review --as-of 2026-11-24 --out /tmp/tffac-league-tier-2026-27
```

This adds the per-club `league-tier-readiness-2026-27.csv` and the grouped
`league-tier-readiness-2026-27.md` to the audit reports.

## Phase 5 season confirmations and proposed approvals

The evidence bundle checks all 48 NLS division lists. It captures
2026–27 FA Full-Time tables, league tables and equivalent official
season fixtures for the three National League divisions. The latter
come from the [Sutton United release](https://www.suttonunited.net/fixtures-2026-27-schedule-revealed/),
the [Chester fixture](https://chesterfc.com/fixtures/first-team/) and
[result cards](https://chesterfc.com/results/first-team/), and the
[Torquay United release](https://torquayunited.com/horsham-at-home-first-up-for-united-fixture-release-day/).
Each captured list has its own source URL, captured names and observation
date. These are membership snapshots, not evidence of uninterrupted
membership at every date in the season.

| Evidence population | Season membership proposed | Holds |
| --- | ---: | ---: |
| Initial FA allocation candidates | 620 of 622 | 2 |
| Post-May candidates | 28 of 28 | 0 |
| Official professional memberships | 92 of 92 | 0 |
| Original Clubfinder overall | 648 of 651 | 3 |
| Companion-only Journey registry overall | 92 of 92 | 0 |

All 35 named identity or membership reviews from Phase 4 have supporting
season evidence. Seven additional publisher abbreviations or variants
have individual records. The 35 proposed division batches include only
exact and trailing-suffix matches. Individual findings require their own
explicit decisions. The fixture-identity hold for bare Sutton United and
the Kendal Town–Heaton Stannington date conflict remain in the separate
readiness report.

- **Boro Rangers** remains unresolved after the senior withdrawal.
- **Cribbs** withdrew its first XI on 9 November and remains a season
  hold. A separately evidenced historic period may be reviewable.
  [Club statement](https://cribbsfc.co.uk/news/club-statement-1st-xi-withdrawal-from-the-uhlsport-hellenic-league)
- **Holmesdale** remains a hold for the legacy identity. The league
  confirms the merger into Petts Wood & Holmesdale. The successor's
  season membership requires a reviewed identity link before use for the
  legacy record. [League announcement](https://scefl.com/holmesdale-merger-to-bring-growth-and-a-name-change)

### Approval CLI

Prepare the review proposal with the cut-off and an explicit output path.
The JSON includes the full candidate list, source pins, per-entry
evidence, proposed division batches and holds. The Markdown summary
lists coverage and the named holds.

```bash
python -m unittest discover -s tests -p 'test_league_tier*.py' -v
python -m updater.league_tier_approval prepare --as-of 2026-11-24 \
  --out /tmp/league-tier-proposed-approval-2026-27.json
```

The manifest pins the bytes of the source ledgers and the reviewed
membership evidence. It pins the population by its identity projection.
Ground, postcode and website edits do not change that projection.
Identity IDs are scoped to this season and its existing audit roster
names. A future roster rename needs an explicitly reviewed identity
migration before its earlier decisions can be carried forward.

A subsequent authorised reviewer can submit a separate decision request
with `manifest_sha256`, `reviewer`, a timezone-aware `reviewed_at`,
and one or both of the following lists.

- `division_batches` entries require the manifest's exact `batch_id`,
  its `count` and a review `reason`. A batch only records season decisions.
- `decisions` entries name the exact `club`, `scope` (`season` or
  `interval`), `action` (`approve` or `hold`) and `reason`. For a
  dated decision record `valid_from` and exclusive `valid_until`.
  Approval also requires the exact `interval_sha256` of separately
  reviewed dated evidence covering the requested dates. A new decision
  can provide `supersedes` with the active event ID of the same identity
  and scope.

The `record` subcommand takes `--manifest`, `--decisions` and an
explicit `--ledger`. It rebuilds the pinned manifest from the checked-out
inputs, rejects altered or stale proposals, verifies every decision,
and appends the batch atomically or leaves the existing ledger intact.
External sources must be refreshed into new versioned evidence when
they change. Season and dated decisions are separate and do not create
events in each other's scope. Ambiguous identities, unsupported dates
and conflicting active intervals fail validation. A repeated identical
event is idempotent. Each event keeps the reviewer, reason, evidence,
manifest digest, proposed classification and any superseded event.
The ledger is version-controlled for review and correction.

At the proposal stage the live ledger contained zero events, all
`approved_tier` fields were blank, and no dated intervals were proposed.

## Phase 6 final acceptance

The 24 November 2026 proposal digest is
`e77fec695e631789c0835ae53895cabda8b27de502ae77e0a9734d45709eaddb`.
The acceptance regression recomputes that digest, the six source-file
hashes and the roster identity pin. It reconciles every membership to
captured evidence, checks the Tier and FA Step relationship, and
verifies that each of the 743 roster identities occurs exactly once.

| Population | Season approvals in isolated replay | Holds |
| --- | ---: | ---: |
| Original Clubfinder | 648 | 3 |
| Companion-only Journey | 92 | 0 |
| Total | 740 | 3 |

The CLI replay expanded 35 division batches into 698 season approvals
and recorded 42 individual season approvals. The three explicit holds
were Boro Rangers FC, Cribbs FC and Holmesdale FC. There were zero
tie-day approvals. Two fresh temporary ledgers were byte-identical.
Repeating the same request, submitting a rehashed stale proposal and
requesting an unsupported tie-day interval each left the first temporary
ledger byte-identical. The live ledger remained empty throughout.

Only an active event for the same identity and scope can be superseded.
The regression exercises wrong-identity, wrong-scope and already
superseded events, as well as overlapping intervals. During review,
individual requests were found to be able to supply their own
`batch_id`. The CLI now derives batch provenance exclusively from
validated batch selections. The stale check compares repository evidence
pins. It relies on versioned updates for changes at the original
publishers.

The Sutton United cup identity ambiguity and the Kendal Town–Heaton
Stannington date conflict (22 and 25 August) are still reported
independently of the membership holds.

### Main baseline failures

Full test discovery reproduced all five failures on main
`c9ce1aeb97fd22a6037dcb63a859d0bc359122d5`. The four focused test modules
reproduced the same five failures after main advanced to `9d70321c`.
The Weston alias and Public Stats window paths were also exercised with
controlled data and window stubs.

| Failing test | Cause and separate remediation |
| --- | --- |
| `test_weston_has_one_third_qualifying_conditional_slot` | The test reads current fixtures for a historical conditional draw. Weston subsequently lost the replay to Wimborne, whose 3 October tie against Crowborough is recorded as a completed result. Use a fixed pre-replay fixture for conditional draws and a resolved-history fixture for progression. |
| `test_live_lookup_falls_back_to_canonical_club_identity` | BETA calls the competition-specific key helper where the test requires a literal call to the generic helper. The current lookup resolves both Weston results, including the replay loss. Assert the lookup behavior with a punctuation variant. |
| `test_glance_card_and_existing_logic` | The old label and emoji assertions predate the styled “Pigeon Miles Flown” label and embedded icon. Assert the rendered card, mileage and icon. |
| `test_stats_certificate_labels_pigeon_miles` | The expected “Pigeon Miles Travelled” label was renamed to “Pigeon Miles Flown”. Test the current label and numeric value. |
| `test_popup_opens_once_and_before_first_await_in_certificate` | The old function signature and exact popup statement predate supplied-window support. Exercise both paths to check that a new window opens once before the mileage await and an existing window is reused. |

## Phase 7 formal season-membership decisions

Approving reviewer **Anvil Springstien** (GitHub `anvilspringstien`)
explicitly authorised the formal season decisions in the 24 November 2026
Phase 7 instruction for PR #732. The CLI recorded the decisions at
**19:52:18 UTC on 24 November 2026** using the accepted Phase 6 digest and
evidence pins. The versioned
[decision request](../updater/league-tier-sources/league-tier-2026-27-season-approval-request.json)
preserves the batch and individual rationale and the three hold reasons.

| Population | Season approvals | Season holds | Tie-day approvals |
| --- | ---: | ---: | ---: |
| Original Clubfinder | 648 | 3 | 0 |
| Companion-only Journey | 92 | 0 | 0 |
| **Total** | **740** | **3** | **0** |

The ledger covers all 743 identities exactly once. The approvals comprise
698 clubs across 35 division batches and 42 individual decisions. Boro
Rangers, Cribbs and Holmesdale remain held. The Sutton United identity
ambiguity and the 22/25 August Kendal Town–Heaton Stannington date
conflict remain separate cup diagnostics.

The CLI produced an identical ledger when replayed from an empty temporary
ledger. Resubmitting the same request left the ledger byte-identical.
The League & Tier regression suite repeats the check in isolation.
The ledger SHA-256 is
`e2c7c2b0540cb64e410722c7f22d2f9108a44a9d03eabbca1ae96a097aad9303`.
The candidate export remains read-only with blank `approved_tier` fields.
The five existing test failures and their separate remedies are listed
in the Phase 6 baseline table above.
