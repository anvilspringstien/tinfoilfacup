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
  Ambiguous source evidence, club identity, groundshare, sponsorship, exact postcode or exceptional competition decisions should fail closed for review rather than being promoted through an ad-hoc assumption. A held item never becomes verified merely because other work has succeeded.

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

A **critical candidate-health failure** must block publication of the affected candidate. A candidate that fails canonical chronology, source evidence, identity, venue/postcode, round coverage, publication freshness or regression guards cannot become canonical state. A delayed or missing *scheduled launch* is a distinct operational warning: it never proves the last published competition data correct, nor does it automatically invalidate independently validated data.

**Fixture-local quarantine:** a disputed/uncertain tie or result is held rather than inferred. Where current safeguards can prove separation, this does not automatically block publication of an **unrelated, independently sourced and fully validated** result. It must not alter a held fixture, invent a progression/custodian, bypass shared chronology checks or turn an overall unresolved state into a verified all-clear. If the boundary between held and proposed data cannot be proved, fail closed at the broader publication boundary.

Publication order remains **build → validate → health → regress → commit**, followed by the required stale-input/rebase checks before push. A green result for a *single item* is not the same as overall health, and a successful catch-up run is not evidence that its scheduled launch occurred. Diagnostic reports may still be retained without canonical publication.

## Public / Shed release boundary

**Public and Shed separation must be demonstrable throughout the entire rendering and data dependency chain, not merely through different URLs or filenames.**

No Shed-only change shall reach Public without explicit, owner-approved promotion.

Shared dependencies must be deliberately identified, governed and tested.

Public includes the normal hosted entrance, installed app and their complete downstream rendering and data paths. Shared canonical competition data remains governed by the publication invariant; shared application code does not exempt experimental changes from release approval.

Mission Control must distinguish four states, each supported by its own evidence:

1. **Verified** — supported by sufficient evidence.
2. **In the Shed** — implemented within the experimental environment.
3. **Approved for Public** — explicitly authorised for publication.
4. **Served to Public** — independently confirmed in the hosted user experience.

No state may be inferred merely from the preceding state.

## Future Round Fire Drill

Hardening is complete **only when an end-to-end synthetic Future Round Fire Drill passes as an acceptance test** through the ordinary pipeline without application-code edits; documentation, selected historical regression tests, or a passing current-round scan do not substitute for this proof. The drill should include unknown clubs, unfamiliar valid grounds/postcodes, home and away wins, draws/replays where applicable, changing custodians and campaigns reaching new venues.

Success means:

> **A completely unfamiliar but otherwise ordinary FA Cup round can move from official observation → validated canonical data → derived campaigns/custodians → Clubfinder → Stats/Pigeon Miles → BETA fallback without a human editing code.**

The acceptance drill must explicitly verify fail-closed quarantines for ambiguous club names, sponsored grounds, groundshares, qualifying roles and exact-postcode conflicts, plus independently verified fixture-local recovery, safe rebase/concurrent-writer handling and canonical publication gates.

Exceptional football may still require a reviewed disposition. Ambiguous evidence may quarantine. Neither is permission to hard-code ordinary future football.
