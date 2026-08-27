# Tin Foil FA Cup — Current Venue Validation

Last checked: **27/08/2026, 14:20:30 UTC**

**v7.9.2 VALIDATION ONLY. No canonical GROUNDS record, approval ledger, `clubfinder.html`, or `competition.json` is changed.**

- Units checked: **7**
- Canonical records present: **0**
- Canonical records missing: **7**
- Multiple canonical matches: **0**
- Canonical records changed: **0**
- Held relationships changed: **0**

## Canonical comparison

### Epsom & Ewell FC

- State: `CANONICAL_MISSING`
- Eligible display name: **Epsom & Ewell FC**
- Action: `changed_groundshare`
- Current canonical: **NO CANONICAL GROUNDS RECORD**
- Validated target: **Chalky Lane • KT9 2NF** • `51.346952, -0.306908`
- Postcode change required: **N/A — canonical missing/ambiguous**
- Ground-name change required: **N/A — canonical missing/ambiguous**
- Venue evidence: https://epsomandewellfc.co.uk/club/visiting-us/
- Coordinate basis: Open Postcode Geo / KT9 2NF (postcode centroid candidate)

### Belper United FC

- State: `CANONICAL_MISSING`
- Eligible display name: **Belper United FC**
- Action: `changed_groundshare`
- Current canonical: **NO CANONICAL GROUNDS RECORD**
- Validated target: **Don Amott Arena • DE3 9FB** • `52.921171, -1.54175`
- Postcode change required: **N/A — canonical missing/ambiguous**
- Ground-name change required: **N/A — canonical missing/ambiguous**
- Venue evidence: https://belperunited.co.uk/contact-us/
- Coordinate basis: Open Postcode Geo / DE3 9FB (postcode centroid candidate)

### Southall FC

- State: `CANONICAL_MISSING`
- Eligible display name: **Southall FC**
- Action: `changed_groundshare`
- Current canonical: **NO CANONICAL GROUNDS RECORD**
- Validated target: **Honeycroft • UB7 8HX** • `51.512049, -0.457664`
- Postcode change required: **N/A — canonical missing/ambiguous**
- Ground-name change required: **N/A — canonical missing/ambiguous**
- Venue evidence: https://www.southallfc.com/contact
- Coordinate basis: Open Postcode Geo / UB7 8HX (postcode centroid candidate)

### Cobham FC

- State: `CANONICAL_MISSING`
- Eligible display name: **Cobham FC**
- Action: `independent_current_ground`
- Current canonical: **NO CANONICAL GROUNDS RECORD**
- Validated target: **The Reg Madgwick Stadium • KT11 3EP** • `51.329238, -0.412258`
- Postcode change required: **N/A — canonical missing/ambiguous**
- Ground-name change required: **N/A — canonical missing/ambiguous**
- Venue evidence: https://www.cobhamfootballclub.com/contact
- Coordinate basis: Open Postcode Geo / KT11 3EP (postcode centroid candidate)

### Eastwood Community FC

- State: `CANONICAL_MISSING`
- Eligible display name: **Eastwood Community FC**
- Action: `independent_current_ground`
- Current canonical: **NO CANONICAL GROUNDS RECORD**
- Validated target: **Coronation Park • NG16 3HB** • `53.01357, -1.296344`
- Postcode change required: **N/A — canonical missing/ambiguous**
- Ground-name change required: **N/A — canonical missing/ambiguous**
- Venue evidence: https://www.eastwoodcfc.co.uk/contact
- Coordinate basis: Open Postcode Geo / NG16 3HB (postcode centroid candidate)

### Hayes & Yeading United FC

- State: `CANONICAL_MISSING`
- Eligible display name: **Hayes & Yeading United FC**
- Action: `independent_current_ground`
- Current canonical: **NO CANONICAL GROUNDS RECORD**
- Validated target: **The SkyEx Community Stadium • UB4 0SL** • `51.509788, -0.395011`
- Postcode change required: **N/A — canonical missing/ambiguous**
- Ground-name change required: **N/A — canonical missing/ambiguous**
- Venue evidence: https://hyufc.ktckts.com/contactus
- Coordinate basis: Open Postcode Geo / UB4 0SL (postcode centroid candidate)

### Corby Town FC

- State: `CANONICAL_MISSING`
- Eligible display name: **Corby Town FC**
- Action: `independent_current_ground`
- Current canonical: **NO CANONICAL GROUNDS RECORD**
- Validated target: **Steel Park • NN17 2AE** • `52.506286, -0.705086`
- Postcode change required: **N/A — canonical missing/ambiguous**
- Ground-name change required: **N/A — canonical missing/ambiguous**
- Venue evidence: https://www.corbytown.co.uk/a/steel-park-49382.html?page=2
- Coordinate basis: Open Postcode Geo / NN17 2AE (postcode centroid candidate)

## Held outside scope

- **Romulus FC ↔ Sutton Coldfield Town FC** remains `HELD_FOR_MORE_EVIDENCE` and is not validated, corrected, approved or published by this stage.

## Safety

- v7.9.1 must still contain exactly seven queue units and zero published canonical records.
- Missing canonical records are reported, never silently created by this validation stage.
- Multiple canonical matches are reported and block automatic promotion for that club.
- The three stale relationships #8/#10/#14 are not revived.
- Postcode-centroid candidates are not silently substituted for existing exact ground coordinates when the postcode is unchanged.
- This stage writes only the validation JSON/report.
