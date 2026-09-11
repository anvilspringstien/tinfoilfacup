# Tin Foil FA Cup — Law 2 qualifying eligibility audit

Status: **READ ONLY — no production Clubfinder or competition data changed**

## Question

Law 2 starts a Tin Foil FA Cup journey in the FA Cup qualifying rounds. Which 2026-27 Emirates FA Cup clubs therefore belong in the Clubfinder origin population?

## Official FA entry-round population

The repository's existing FA reconciliation parses the official 743 accepted clubs and official exemptions into these entry-round counts:

- Extra Preliminary Round: **438**
- Preliminary Round: **53**
- First Round Qualifying: **88**
- Second Round Qualifying: **48**
- Fourth Round Qualifying: **24**
- First Round Proper: **48**
- Third Round Proper: **44**

No clubs enter at Third Round Qualifying in the published exemption structure.

## Law 2 population

Qualifying-round entrants are therefore:

**438 + 53 + 88 + 48 + 24 = 651 clubs**

Current protected Clubfinder origins: **491**.

The 491 is not an arbitrary subset: it exactly equals the clubs entering in the first two qualifying stages used by the current origin pool:

**438 Extra Preliminary + 53 Preliminary = 491**

The Law 2 gap is therefore exactly:

**651 − 491 = 160 missing eligible origin clubs**

Those 160 are:

- **88** clubs entering at First Round Qualifying
- **48** clubs entering at Second Round Qualifying
- **24** clubs entering at Fourth Round Qualifying

The **92** clubs entering at First Round Proper or Third Round Proper are accepted FA Cup clubs but are **not Law 2 Clubfinder origins**, because their campaigns do not begin in the qualifying rounds.

## Leatherhead canary

Leatherhead FC is officially accepted for the 2026-27 Emirates FA Cup and is listed by the FA among the **88 clubs exempt to First Round Qualifying**. It is therefore one of the 160 clubs omitted by the current 491-origin rule and should be a Law 2 origin.

The existing companion Journey Club Registry already records:

- club: **Leatherhead FC**
- entry round: **First Round Qualifying**
- journey state: active
- tie venue evidence: **Fetcham Grove, KT22 9AS**

This makes **KT22 9AS → Leatherhead FC** a suitable regression canary for the eventual production expansion.

## Existing repository readiness

The repository already contains a companion Journey Club Registry for all **252** accepted FA Cup identities outside the protected 491 origins. That registry is broader than Law 2 because it also includes the 92 Proper-round entrants.

For the currently active First Round Qualifying cohort, the registry reports **6 active-guarded** records and **82 active-supporting-evidence** records: exactly **88** clubs. The remaining **72 Law 2 clubs** enter in Second Round Qualifying (48) or Fourth Round Qualifying (24) and are not yet active in the competition chronology.

This means the identity and journey plumbing for the Law 2 expansion already substantially exists; the production origin selector is the part still scoped to 491.

## Recommendation

Do **not** expand Clubfinder to all 743 accepted clubs.

The constitutional production target is **651 Law 2 origins**, comprising every club whose 2026-27 FA Cup campaign begins in Extra Preliminary, Preliminary, First Round Qualifying, Second Round Qualifying or Fourth Round Qualifying.

Before production promotion:

1. Promote only the 160 qualifying-round identities from the companion registry into origin eligibility.
2. Preserve each club's official FA entry round.
3. Keep the existing journey/custodian logic unchanged.
4. Require usable origin location data before a newly eligible club can participate in nearest-three distance selection; do not silently substitute uncertain ground data.
5. Add a rendered regression for **KT22 9AS** requiring Leatherhead FC to be the nearest Law 2 origin and requiring its journey to begin at First Round Qualifying.
6. Add a population regression requiring exactly **651** Law 2 origin identities and rejecting Proper-round-only clubs from the origin pool.

## Safety conclusion

**Audit result: current 491-origin population is too narrow for Law 2 by 160 clubs.**

Canonical Law 2 population for 2026-27: **651**.

Production files remain untouched by this audit.
