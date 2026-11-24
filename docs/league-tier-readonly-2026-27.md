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
  The previous full match table was not retained. This number is a historical
  lead to investigate, not a result claimed by the new partial-source audit.

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

### Required further sources

- Subsequent FA and league announcements, including revised allocations,
  withdrawals and appeal outcomes. Lead for that pass: the
  [Isthmian League](https://www.isthmian.co.uk/articles/club-allocations-for-202627-season)
  lists Peacehaven & Telscombe in South East, and
  [Guernsey FC](https://guernseyfc.com/two-new-opponents-and-an-old-friend-returns/)
  records its Southern Combination place after the play-off. The initial
  allocation audit retains both provisional records.
- Official 2026–27 [Premier League](https://www.premierleague.com/) and
  [English Football League](https://www.efl.com/) membership lists — Tiers 1–4.

Do **not** infer a club's Tier from its FA Cup entry round, historic result,
postcode, playing venue, or a different season's league table.

## Reproduce audit

```bash
python -m unittest discover -s tests -p 'test_league_tier_readonly.py' -v
python -m updater.league_tier_readonly --out /tmp/tffac-league-tier-2026-27
```

Produces only four files under the explicitly supplied `--out` directory:

1. `league-tier-candidates-2026-27.csv`: **every original club** plus
   companion-only journey clubs; empty `approved_tier` throughout
2. `league-tier-review-queue-2026-27.csv`: missing, provisional or
   ambiguous source/identity cases
3. `league-tier-audit-summary-2026-27.json`: counts and provenance
4. `league-tier-audit-2026-27.md`: concise human summary

GitHub's `League and Tier — 2026-27 read-only audit` workflow runs the
tests and uploads the report as an artifact. The workflow has
`contents: read` permissions and does not commit or deploy anything.

## Promotion boundary

1. Import official Premier League/EFL **season evidence** and reconcile subsequent amendments.
2. Re-run matching over all relevant population, resolve exceptions and
   historical 629/22 discrepancy with source citations.
3. Apply reviewed, season-specific identity decisions through the normal
   Construction Law route. Only a separately approved reviewed registry may
   contain `approved_tier` values.
4. Expose it in Mission Control's eventual Club Audit as **read-only first**.
5. Independently develop Giant Killer regression tests against canonical
   cup ties, resolved winners and historical Tier for each match. Keep the
   Challenge disabled until all promotion and safety gates pass.

The present outputs are not used by Public, BETA, Keep, Barry Air, the results
watchers, Clubfinder, Stats or Mission Control. Nothing is auto-promoted.
