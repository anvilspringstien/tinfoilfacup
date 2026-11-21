# Club Entry Radar — Mission Control read-only data contract

Stage 1 of the entrant-ingestion safety gate. This is **not** an automatic
ground importer, a verified-location promotion, or a deployed Mission Control
screen. It is deliberately separate from all protected production paths.

## Run

```sh
python -m updater.club_entry_radar > club-entry-radar.json
python -m unittest discover -s tests -p 'test_club_entry_radar.py' -v
```

The GitHub Action uploads the machine-readable JSON as
`club-entry-radar-readonly`; it **does not** write that report into the
repository, production, BETA or Cloudflare.

## Contract

`schema_version: 1`, `read_only: true`,
`canonical_source: competition.json`, `season`, `competition_updated_at`,
`automatic_ground_promotion: false`, `fixture_venues_used_as_home_grounds: false`.

`rounds[]` contains `round`, `entrant_count`,
`new_to_observed_rounds`, `coverage`, and `clubs[]`. Each club has its
canonical `club`, identity key, a new-entrant marker, optional companion
registry lifecycle, and **separate** `production` and `beta` source states.

The exact source statuses are:

- `verified_location`: existing Clubfinder record claims verification
- `ground_recorded_coordinates_pending`: ground and postcode are present,
  but the existing record is not marked verified
- `missing_ground`: no exact record, or ground/postcode incomplete
- `identity_conflict`: colliding or ambiguous records; requires review

These statuses describe **existing registry values**; they never imply
fresh independent evidence verification. The machine cannot infer that a
fixture venue is a club's home ground. No location coordinates, mileage,
fixtures, historical results, badges or user Campaigns are changed.

The `new_to_observed_rounds` calculation is relative to **canonical fixtures
actually present** in this snapshot, not the full 743-club accepted list.
Replay rounds immediately follow their parent round. Counts are not
hardcoded to any particular season, round or number of clubs.

## Stage 2 integration in Mission Control (not in this PR)

The current Mission Control UI implementation is not present in the TFFAC
repository inspected for this PR. Before enabling a live dashboard:

1. Locate the real Mission Control deployment and its authenticated backend.
2. Expose this report through an admin-only, read-only endpoint with an
   explicit last-checked time and canonical competition revision.
3. Display source-specific counts with filters by round/status, including
   `missing_ground` and `identity_conflict` alerts.
4. Run the audit after canonical draw ingestion and before publication.
   New missing/ambiguous entrants should create a review alert, not silently
   publish an unsupported ground record.
5. Keep source-evidence review and coordinate/verified-status promotion
   subject to their current Construction Law approval gates.
6. Regression-test the authenticated Mission Control UI and a real user
   Campaign on Big Boy, iPhone and iPad before any deployment.

Do not use the read-only report to automatically patch the fixture venue,
Clubfinder, Barry Air or competition.json. Do not treat 'zero missing' in BETA
as proof that production is ready.
