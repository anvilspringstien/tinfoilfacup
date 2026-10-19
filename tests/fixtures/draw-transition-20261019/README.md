# 19 October 2026 First Round Proper import

Frozen evidence from successful draw run **39327691531**. `manifest.json`
identifies each immutable source commit/path and compressed/uncompressed SHA-256.
The run checked out `669f577ba7596a559ab7afb7dcfcc6a701bcbc8c` and published
`d4005bc` (full object ID in the manifest).

- `competition-before.json.gz`: exact canonical input, Fourth Qualifying active.
- `competition-published.json.gz`: exact importer output, 40 Proper ties and all
  32 outgoing ties archived, with result history and pending replays retained.
- `draw-watch-report.json`: published report, including the 11-row shrinking
  old-round catalogue and complete 40-tie target draw.

**No original FA HTML was retained by this run.** Do not call this a raw source
capture. The rehearsal rebuilds FA-shaped HTML from the published target rows;
it models the 11 outgoing rows with the canonical pending replay schedule.
That reconstructed input passes through the real parser and `auto_draw.main`.
Its output must equal the frozen actual publication except for `updated_at`.

Replay scores and later Proper rounds are **synthetic**, using real pending
participants and unmistakably synthetic new entrants. They are test scenarios,
not evidence of future winners, draws or fixture dates. Both possible winning
sides of every pending replay are tested, including abbreviated FA identities.

Run `python -m unittest discover -s tests -p 'test_round_transition_rehearsal.py' -v`
and `python tests/run_round_transition_rehearsal.py --state proper-resolved`.
The workflow runs all six states, including both replay-winning orientations.
Generated production/BETA fallbacks and all
scenario data exist only inside disposable copies; nothing is published.
