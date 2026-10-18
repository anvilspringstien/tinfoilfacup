# FRQ repair lessons and next-round readiness — 18 October 2026

This is a code/workflow audit after PR #471, not proof of a future source payload.
Ground Health is handled separately from changes to draw or replay publishing.

## Proven

- The production Competition Health run 39132012005 passed after #471 and published
  commit ffedd381. The guarded Results path and reconstructed source tests passed
  in review. Confirm the final production Results run and BETA fallback separately.
- Captured real-source ingestion covers 32 FRQ observations, 5–0 Fylde custody,
  19:45 Atherton replay metadata retention, unchanged production inputs, and
  renderer, Stats, historical journeys/venues, all-origin and UI checks.
- round_state_regression.py covers qualifying draw/replay ancestry independent of
  orientation, postponed/abandoned rearrangements, awards, penalty winners,
  explicit void/replay orders, chronology conflicts and Competition Proper
  penalties without replay ancestry.
- The draw importer independently validates a complete next draw even when the
  old-round catalogue is partial. EXPECTED_ROUND_TIES sets First Round Proper to
  40. The current boundary regression explicitly exercises 31/32/33 FRQ rows;
  this is not an end-to-end proof of 39/40/41 Proper rows.

## Priority follow-ups before relying on unattended replay ingestion

1. **Archived replay orchestration:** auto_round_results.active_fixtures follows
   source_round and active fixtures. After draw promotion it does not scan archived
   FRQ fixtures. publish-preceding-replays.yml has no schedule and its production
   write step requires workflow_dispatch with publish=true. Its guarded stage and
   source/ancestry checks exist; automatic scheduled promotion is not evidenced.
   Prove the conditional next-round slot -> archived replay -> exact result ->
   definite slot -> Campaign/Stats path, then explicitly decide whether to promote
   that manual boundary to automatic operation. Keep that policy change separate.
2. **Actual round-boundary stress case:** exercise partial FRQ catalogue plus all
   40 Proper ties through auto_draw.main, including unresolved A-or-B slots.
   Reject 39/41 ties, wrong-round pages, ambiguous identities and conflicting
   source results without changing canonical state. Preserve all 32 outgoing ties,
   original/replay dates, venues, kickoffs and mileage; repeat to prove idempotency.
3. **Publication concurrency:** Results, Competition Health, Ground Health (this
   fix), and the preceding-replay publisher share competition-state per branch.
   Draw uses fa-cup-draw-scan-main instead and rebases without the full post-rebase
   competition/UI checks. Test Draw promotion racing a result/report publication,
   including stale queued SHAs and a genuine conflicting update. Align writer
   coordination and revalidation in a separately reviewed change.
4. **Failure evidence and alerts:** Results now captures inputs, candidate and
   source HTML. Give draw/round-boundary failures equivalent reproducible evidence
   and test an independent alert for blocked publication, source degradation,
   queued/stuck runs, successful recovery and published-state freshness. A healthy
   request/heartbeat alone is not proof that results reached the public snapshot.

## Repeated-ingestion test stability found during this review

After the production import succeeded, the original Fylde unit test correctly got
`duplicate`, but expected `result`. It had depended on mutable current history.
The captured candidate now uses the exact pre-publication canonical input from
13d0e1f, compressed with a documented checksum, and the unit case explicitly tests
first and repeated classification. Current published-snapshot guards still run
against the current checkout separately. Freeze incident scenarios while keeping
live-state tests dynamic; do not remove duplicate protection to satisfy a test.

## Ground Health publication regression added here

Its Law 2 audit builders rewrite clubfinder.html but the monitor owns reports,
not presentation. Discard only that known temporary audit view before committing
an explicit report allowlist; reject other tracked mutations. Use a fresh branch
checkout and the common competition-state lock. Disposable local Git remotes prove
report-only publication with a dirty generated HTML view and a newer upstream UI,
no commit for unchanged reports, and rejection of an unexpected competition edit.
The full audit pipeline independently passed: 651 selectable origins, zero critical
items, zero review items. Production presentation and competition data are not
changed by this PR.

## Confidence

The repaired Results path has strong direct evidence. Safe rejection is often
proven where unattended successful recovery/publication is not. Do not represent
manual archived-replay publication as fully automatic, or the existing synthetic
32-tie boundary checks as a live 40-tie draw acceptance test.
