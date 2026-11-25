# Mission Control Club Audit, Phase 1

Club Audit joins the season's original Clubfinder population and companion Journey registry into a read-only JSON report. It runs against the checked-out repository and sends the report to standard output. Python 3.10+ and Node.js with full ICU support are required. There are no network requests, credentials, feeds to modify, or third-party packages.

```sh
python -B -m updater.club_audit > /tmp/club-audit.json
python -B -m updater.club_audit --generated-on 2026-11-25 --club 'Leyton Orient FC'
python -B -m unittest discover -s tests -p 'test_club_audit.py' -v
```

Supply the same `--generated-on` date and identical source bytes for identical JSON. The date is an output label, defaulting to the current UTC date. It does not turn a current checkout into a historical snapshot. Source paths and SHA-256 byte hashes identify the exact files consulted. The competition timestamp is reported separately. The canonical website queue is regenerated in a temporary directory outside the checkout and compared with its committed snapshot.

Use the [JSON Schema](club-audit.schema.json) and [generated example](examples/club-audit-2026-11-25.json) when reviewing the contract. By default, the output includes every registered identity. Repeat `--club` with exact registry names to produce an excerpt. The schema and population-wide summaries are identical for full reports and excerpts.

## How to read a club record

| Member | Meaning |
| --- | --- |
| `club_id` and `aliases` | The existing League & Tier identity hash of season, registry population and canonical club name. The ID stays stable across field updates. Registry identity migrations need their own review. Labels have source scopes for the competition, website or league publisher. A publisher label can be shared across sources and is never a global join key. |
| `membership` | Original roster membership, eligibility as actually present in each build, and companion registry membership and lifecycle. A club can be in both registries. |
| `competition` | Declared entry rounds and the observed Club Entry Radar rounds, including replays. Each observed round identifies the source label and the matching method. Companion home-ground candidates are supporting evidence. |
| `published.public` and `published.beta` | Current HTML ground, postcode, coordinates and website from the respective builds. Each field has a value, status, review status and provenance. A missing value is `null`. A loose display-name hit with no unique recognised identity is ambiguous. A known website destination can be verified while the build mapping is absent. |
| `league_tier` | Active season approval or hold from the signed approval ledger, with the decision reference and supporting evidence. An approved tuple appears only for an active approval. |
| `tie_day` | Explicit interval decisions and their effect on observed played dates, with date and identity holds. Interval end dates are exclusive. Season approvals never supply tie-day approval. |
| `discrepancies` | Differences across builds, conflicting or pending evidence and active holds. The open-location review input transcribes the public follow-up from [PR #733](https://github.com/anvilspringstien/tinfoilfacup/pull/733). It supplies review reasons and observations only. |

The population and ID rules come from the League & Tier roster and approval CLIs. Round extraction comes from Club Entry Radar, with exact, AFC-preserving identity matching and only the round engine's declared aliases and recorded identity confirmations. Ground rows and website map keys use the existing AFC-preserving identity rule. Shared locations cannot establish a club identity. Fixture-day venue records cannot establish a home ground. The current ground-name ledger, Law 2 verification ledger and entrant home-ground evidence carry distinct provenance. A name-only change leaves the postcode's own evidence in force. Coordinates retain their recorded source or pending status. The website queue and bulk-publication CLI continue to own website review and publication. Club Audit reads their data and never calls promotion.

`reconciliation` exposes source-only round labels, unmatched played labels, approval or review records outside the current population, and differences between the roster and each build. This keeps the Petts Wood & Holmesdale successor visible while the legacy Holmesdale registry identity and its membership hold stay intact. The current inputs also leave Eastwood Town and Wolverhampton City unassigned under the available identity rules.

## Reconciliation on 25 November 2026

| Measure | Public | BETA |
| --- | ---: | ---: |
| Eligible website mappings | 32 / 651 | 334 / 651 |
| Ground records missing or non-unique across all 743 identities | 92 | 62 |
| Ground records missing or non-unique among 40 Second Round Proper fixture participants | 31 | 0 |

The 743 unique identities are 651 original origins and 92 companion-only identities. The 252-row companion registry overlaps the original population by 160. The active League & Tier ledger gives 740 season approvals and three holds for Boro Rangers, Cribbs and Holmesdale. There are zero interval approvals. Those numbers are reconciliation results from the inputs. The CLI does not require them to stay fixed as the registries and decisions evolve. The second-round ground metric uses the existing custodian audit's current fixture scope. A recorded BETA ground can still lack verified coordinates, as Leyton Orient illustrates.

## Mission Control deployment

The main Worker is [tffac-mission-control](https://tffac-mission-control.anvilspringstien.workers.dev/) and its isolated Radar test Worker is [tffac-mission-control-radar-test](https://tffac-mission-control-radar-test.anvilspringstien.workers.dev/). Both hosts and their Radar endpoints returned HTTP 403 to unauthenticated requests on 25 November. The Cloudflare account and installed source revision were unavailable for direct inspection.

The 24 November original-Worker backup handoff identifies a deployed Cloudflare Worker outside this checkout, with the dashboard, Google OAuth sign-in and callback, browser-local review workspace, read-only Gmail view and an Ombudsman Worker service binding. The 23 November Radar handoff and subsequent combined handoff document a private Radar API and manual JSON import. The isolated Worker successfully fetched a report from GitHub Actions. That flow reads a successful, manually dispatched `club-entry-radar.yml` run on `main` and uses the `club-entry-radar-readonly` artifact. The handoffs do not verify the exact combined implementation installed on the original host today. The repository owns Club Entry Radar and its workflow, while these handoffs identify the separate Worker deployments.

This phase provides local report generation and read-only CI tests. It changes neither Worker and creates no deployment or artifact-fetch integration.
