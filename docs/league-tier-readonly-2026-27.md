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
