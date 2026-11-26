# Approved factual club records in Public

Use the existing current-ground and website publication ledgers as the source of truth. The reconciliation CLI plans and applies exact approved factual fields to Public when the approved values already exist in BETA. It does not edit BETA, competition data, fixture history, the eligibility roster, League & Tier, or application behaviour.

Run the plan first. It lists each website mapping key and dated evidence batch, each approved ground/postcode change and all BETA entrant records awaiting their separate promotion decision.

```sh
python -B -m updater.publish_approved_public_club_records
```

Read the plan and check the active source records. Existing Public website conflicts and absent or withdrawn approvals are reported without being applied. A Public ground with unexpected prior values stops the CLI. The 31 pending entrant previews, including Leyton Orient, still lack the independent coordinate and promotion approval required by their evidence ledger. The separate Public and BETA eligibility records for Holmesdale and Petts Wood & Holmesdale are outside this publication.

Only after project-owner approval of the proposed publication, generate and check the Public output and the dependent tester list:

```sh
python -B -m updater.publish_approved_public_club_records --apply
python -B updater/export_test_postcodes.py
python -B -m updater.publish_approved_public_club_records --check
python -B -m updater.public_club_facts_guard --base origin/main
python -B -m unittest discover -s tests -p 'test_public_club_facts_*.py' -v
```

A review branch can generate the proposed files for inspection. The approved main-branch merge is the publication step. The Stage C guard reconstructs the expected Public HTML from the approved facts and checks the complete document byte-for-byte. Competition and Challenges retain their existing checks. No automatic publication workflow runs this CLI.
