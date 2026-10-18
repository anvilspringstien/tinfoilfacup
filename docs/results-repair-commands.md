# Results repair CLI and verification commands

## Authenticated Windows CLI (executed by the repository owner)

```powershell
gh auth status
gh run view 39052574769 --repo anvilspringstien/tinfoilfacup --log-failed
gh run view 39052574769 --repo anvilspringstien/tinfoilfacup --json headSha,headBranch,event,status,conclusion,url
gh run download 39052574769 --repo anvilspringstien/tinfoilfacup --dir "$repair\artifacts"
git --version
gh repo clone anvilspringstien/tinfoilfacup "$repo" -- --no-checkout
git -C "$repo" bundle create "$repo.bundle" --all
```

The actual download/output paths were Desktop/TinFoil-Results-20261018-123451
and Desktop/TinFoil-Repair-20261018-124927. The first clone/bundle attempt failed
because Git was not installed; the successful bundle followed installation and
verification of Git 2.55.0.windows.5. Credentials stayed in the owner's keyring.

## Isolated executor checkout and evidence inspection

```bash
git clone /workspace/scratch/179684192556/upload/TinFoil-Repair-20261018-124927.bundle /workspace/scratch/179684192556/tinfoilfacup
git -C /workspace/scratch/179684192556/tinfoilfacup switch -c repair/results-chronological-custody
git status --short --branch
git log -8 --oneline
git show --stat 96ecbc7
git show --stat c7cc169
git show 96ecbc7:competition.json
```

Run artifacts were read from the supplied ZIP. `rg` searches covered the DL5
assertions, source importer, shared classifier, reconciliation, replay sync,
enrichment, metadata rendering and Results/health workflows. Python read Git
snapshots of competition.json to identify changes to the Atherton result and
pending replay map. No historical competition snapshot was patched.

Public source HTML was captured with:

```bash
curl -fsSL --connect-timeout 10 --max-time 30 https://www.footballwebpages.co.uk/fa-cup/fixtures-results/fourth-qualifying-round -o /tmp/tinfoil-fourthq.html
curl -fsSL --connect-timeout 10 --max-time 30 https://www.footballwebpages.co.uk/fa-cup/20261006 -o /tmp/tinfoil-replay-date.html
curl -fsSL --connect-timeout 10 --max-time 30 https://www.footballwebpages.co.uk/match/2026-2027/emirates-fa-cup/atherton-collieries/trafford/594362 -o /tmp/tinfoil-atherton-replay.html
```

## Unit checks

```bash
python -m unittest discover -s tests -p 'test_results_repair.py' -v
python -m unittest discover -s tests -p 'test_active_replay_fixture_sync.py' -v
python -m unittest discover -s tests -p 'test_stage_preceding_replay_candidates.py' -v
python -m unittest discover -s tests -p 'test_replay_orientation_fix_preserves_regressions.py' -v
python -m unittest discover -s tests -p 'test_archived_replay*.py' -v
python -m unittest discover -s tests -p 'test_preceding_round_replay_audit.py' -v
python -m unittest discover -s tests -p 'test_guard_archived_replay_promotion.py' -v
```

54 tests across these seven groups, including nine new Results repair checks.
The source/milestone consistency assertion was also rerun using `-k captured`.

## Shared and published-snapshot checks

```bash
python updater/round_state_regression.py
python updater/round_source_regression.py
python updater/extra_preliminary_replay_regression.py
python updater/shadow_replay_advancement_regression.py
python updater/build_reconciliation_candidate_regression.py
python updater/reconciliation_gate_regression.py
python updater/kickoff_venue_regression.py
python updater/embedded_snapshot_regression.py
node updater/clubfinder_render_regression.js
node updater/clubfinder_stats_regression.js
node updater/amersham_card_render_regression.js
python tests/run_results_repair_candidate.py
python tests/run_results_repair_candidate.py --check production_ui
git diff --check
```

The candidate runner executes these commands in a temporary checkout after
reconstructing results from all 32 captured source observations using the real
parser, classifier and merger (not hand-written competition patches):

```bash
python updater/refresh_clubfinder_embedded_snapshot.py
python updater/competition_regression_guard.py
python updater/reconcile_result_history_aliases.py --check
python updater/kickoff_venue_regression.py
node updater/clubfinder_render_regression.js
node updater/clubfinder_stats_regression.js
node updater/historical_journey_regression.js
node updater/historical_venue_regression.js
node updater/replay_progression_regression.js
node updater/journey_integrity_regression.js
node updater/amersham_card_render_regression.js
node updater/amersham_stats_regression.js
node updater/ex8_venue_render_regression.js
node updater/kt21_venue_render_regression.js
node updater/law2_origin_regression.js
node updater/production_ui_regression.js
```

A separate live enrichment exercise invoked the enrichment module's `main()` with
COMP and REPORT redirected into /tmp and its normal network fetch cached by URL.
It recovered all 20 missing qualifying-replay times across the canonical baseline;
no production competition file was written. Its report is summarised in the
investigation document.

## Fresh-session review validation

GitHub CLI device authentication and repository reads now succeed as anvilspringstien.
The existing repair was absent from main and remote branches/PRs. The review branch
starts at current main 13d0e1f97951281cdc91bf0eb1b128c06e5bc89c and cherry-picks
prepared repair ee44a17393fddef7669fb4879ecb142d63d94a89 without conflicts.
The complete run blocks in .github/workflows/results-repair-tests.yml are rerun
locally before publication. GitHub checks must pass separately. Publication of
the review branch/PR does not authorise a merge or deployment.

Final complete default candidate run: **PASS** (`checks=all`). All four Python
candidate preprocessing/guard checks and all twelve rendered checks completed
successfully. Earlier targeted reruns are recorded above for reproducibility.
See results-repair-validation.log for the actual passing output.
