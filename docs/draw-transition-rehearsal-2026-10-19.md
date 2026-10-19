# First Proper draw: permanent publication rehearsal

The 19 October draw import succeeded, but downstream guards incorrectly treated
Fourth Qualifying as permanently active. PRs #492/#493 repaired those assertions
without removing historical checks. This follow-up makes the incident repeatable
and exercises the surrounding publication checks across advancing round states.

## Evidence and limits

The fixture freezes the exact pre-import canonical input, actual published output
and draw report from run 39327691531. Every file has source commit/path provenance
and compressed/uncompressed checksums. Original FA HTML was not retained: parser
input is explicitly reconstructed, not represented as an original source capture.
The real import must reproduce its actual published output apart from its clock.

Synthetic replays use the real pending participants and schedules. Both possible
winning sides are covered. Later draws/results and venue enrichment are clearly
synthetic; none of these scenarios is a claim about future competition outcomes.

## Permanent checks

| State | Expected active draw |
|---|---|
| Fourth Qualifying before import | 32 qualifying ties |
| Proper draw, replays pending | 40 ties, 11 conditional slots |
| All pending replay home teams win | 40 definite ties |
| All pending replay away teams win | 40 definite ties |
| Second Proper | 20 ties, prior draws archived |
| Third Proper | 32 ties including synthetic new entrants |

Each state generates the production embedded snapshot and separate BETA fallback
using their existing CLIs in a disposable checkout. The runner extracts the
standalone regression commands from Results and Competition Health workflows,
including Campaign, Stats, historical venues/journeys, all selectable origins,
protected UI and embedded equality. Additional BETA identity/replay/Stats/fallback
checks run against each state. Repository production/data inputs are hash-checked
on both successful and failed exit. The new CI workflow has read-only permission.

Permanent negative controls require the repaired production/BETA Thame guards,
exceptional-replay guard and BETA snapshot guard individually to reject missing
qualifying archive ties, partial active draws and wrong-round active fixtures.
The real parser/import entrypoint additionally rejects 39/41 Proper ties,
duplicate clubs and wrong-round source rows without writing canonical input.

## Replay identity findings

The real-name rehearsal found that archived replay staging used a stricter
comparison than the subsequent conditional resolver. `Anstey N` could not match
`Anstey Nomads`. Staging now uses the draw importer's structural abbreviation
comparison, retaining the requirement for exactly one destination.

`Forest Grn` also needs a source-name equivalence to `Forest Green Rovers`, because
the FA abbreviation omits an entire token. That equivalence lives in the shared
draw normalizer, so staging and conditional resolution agree. The frozen source
slot and canonical replay schedule document its provenance. No result, venue or
page is manually corrected. All 22 possible replay winners must have one exact
destination; an additional conflicting Anstey destination still blocks staging.

## Operational boundary

These checks establish ingestion and publication behaviour once a run starts.
They do not establish that GitHub will launch every scheduled run, or that an
unseen future source format will parse. The first live post-draw replay ingestion
still needs operational verification. Existing source/ancestry/penalty evidence,
publication locks and stale-candidate rejection remain in force.
