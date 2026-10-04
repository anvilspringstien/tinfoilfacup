# Tin Foil FA Cup — Construction Law

## Governing question

Before making any patch, repair, regression, guard or new component, ask:

> **Does this move Tin Foil FA Cup closer to being able to ingest an entire future round or draw automatically—including new results, changing winners, changing custodians and previously unseen grounds—without requiring another code change?**

If the answer is **no**, stop and reappraise the proposed change.

A useful alarm bell is:

> **Would we have to edit the code if this happened next Saturday?**

For ordinary football, if the answer is yes, the design is carrying data as code.

## Principles

- **History is asserted. Current state is derived.**
  Exact historical results, exceptional dispositions, identity migrations and verified historical venues may be locked by regression tests. Current winners, custodians and ordinary next fixtures should be derived from canonical competition data.

- **A normal football result must be data, not a software event.**
  A home win, away win, draw, replay, new opponent, new ordinary ground or previously unseen valid postcode must not normally require a code edit.

- **Quarantine uncertainty; do not encode guesses.**
  Ambiguous source evidence or exceptional competition decisions should fail closed for review rather than being promoted through an ad-hoc assumption.

- **Tests must admit valid future data.**
  Regression harnesses may use fixed historical controls, but their mocks must not reject an otherwise valid future club, ground, postcode, winner or round merely because it has not occurred before.

- **A fix restores today's correctness. A solution increases tomorrow's autonomy.**
  Emergency operational repairs are permitted when publication safety requires them, but they must be identified as temporary operational debt and followed by a generic repair.

## Fossil classification

When auditing hard-coded knowledge, classify it before changing it:

1. **Historical assertion — keep.** A fact about a completed event whose exact preservation protects chronology.
2. **Exceptional rule/disposition — keep, but isolate.** A reviewed abnormal event such as a voided tie, ordered replay or identity migration that cannot safely be inferred as ordinary football.
3. **Accidental current knowledge — remove.** A club, winner, custodian, fixture, venue or postcode that software needs only because it happens to describe the present competition state.

## Publication invariant

Canonical/UI publication must be transactional:

**build → validate → health → regress → commit**

A critical health result must prevent publication. Diagnostic reports may still be retained as artifacts, but an unhealthy candidate must not become canonical state.

## Future Round Fire Drill

Hardening is complete only when a synthetic unfamiliar round can travel through the ordinary pipeline without application-code edits. The drill should include unknown clubs, unfamiliar valid grounds/postcodes, home and away wins, draws/replays where applicable, changing custodians and campaigns reaching new venues.

Success means:

> **A completely unfamiliar but otherwise ordinary FA Cup round can move from official observation → validated canonical data → derived campaigns/custodians → Clubfinder → Stats/Pigeon Miles → BETA fallback without a human editing code.**

Exceptional football may still require a reviewed disposition. Ambiguous evidence may quarantine. Neither is permission to hard-code ordinary future football.
