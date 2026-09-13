# Tin Foil FA Cup — Law 2 Qualifying-Origin Audit

**Status: READ ONLY — production Clubfinder v7.6 unchanged.**

## Constitutional rule under audit

Law 2 is interpreted as:

> Every club whose 2026-27 Emirates FA Cup campaign begins in a qualifying round is eligible to be a Tin Foil FA Cup journey origin.

Clubs entering only at a Proper Round are not Tin Foil FA Cup starting clubs under this rule.

## Authoritative competition population

The existing FA Cup Journey Registry audit already reconciles Clubfinder against The FA's official 2026-27 accepted-club and exemptions documents. It enforces a clean **491 + 252 = 743** partition and validates these entry-round totals:

| Entry round | Clubs |
|---|---:|
| Extra Preliminary Round | 438 |
| Preliminary Round | 53 |
| First Round Qualifying | 88 |
| Second Round Qualifying | 48 |
| Third Round Qualifying | 0 |
| Fourth Round Qualifying | 24 |
| First Round Proper | 48 |
| Third Round Proper | 44 |
| **Total accepted** | **743** |

The current Clubfinder origin population is exactly the first two rows: **438 + 53 = 491**.

## Law 2 result

The current production origin pool omits **160 clubs that begin their FA Cup campaign in later qualifying rounds**:

- First Round Qualifying: **88**
- Second Round Qualifying: **48**
- Third Round Qualifying: **0**
- Fourth Round Qualifying: **24**

Therefore the correct Law 2 origin population is:

**491 current origins + 160 later qualifying entrants = 651 Tin Foil FA Cup journey origins.**

The remaining **92** accepted clubs enter at a Proper Round (48 First Round Proper + 44 Third Round Proper) and remain outside the Law 2 starting population.

## Leatherhead constitutional canary

The audit confirms:

- **Leatherhead FC**
- Entry round: **First Round Qualifying**
- Current registry state: `active-supporting-evidence`
- Ground evidence: **Fetcham Grove • KT22 9AS**
- Existing guarded Clubfinder ground record: **not yet present**

Leatherhead is therefore **constitutionally eligible under Law 2** and is currently absent only because Clubfinder's protected origin population stops at Preliminary Round entrants.

## Ground-data blast radius

The 160 missing Law 2 origins are not identity or source-of-truth orphans:

- **6** already have an existing guarded ground record.
- **154** have supporting ground evidence in the Journey Club Registry.
- **0** have no ground evidence at all.

However, supporting evidence is deliberately not equivalent to a guarded production origin record. The 154 supporting-only clubs must pass the same ground/postcode/coordinate verification discipline used by Clubfinder before they can safely participate in nearest-distance selection.

## Safe production implementation

Do **not** special-case Leatherhead and do **not** simply append 160 names to `ELIGIBLE`.

The safe implementation is systemic:

1. Promote the 160 qualifying-round identities from the canonical Journey Club Registry into a Law 2 origin-candidate set.
2. Verify/promote their home-ground postcode and coordinates into the guarded origin-ground namespace without overriding actual tie venues.
3. Build the production origin population from all qualifying entrants: EPR + Preliminary + First Qualifying + Second Qualifying + Fourth Qualifying.
4. Keep First Round Proper and Third Round Proper entrants excluded from origin selection.
5. Add constitutional regressions:
   - origin population = **651**;
   - later qualifying supplement = **160**;
   - no Proper-Round-only club can be selected as an origin;
   - **KT22 9AS returns Leatherhead FC as the nearest eligible origin** once its guarded ground record is promoted;
   - Leatherhead journey starts at **First Round Qualifying** and then uses the existing result/custodian machinery normally.
6. Run the existing all-club journey, Competition Health, Ground Health, replay and rendered-venue regressions before production publication.

## Audit automation

`updater/law2_qualifying_origin_audit.py` is a read-only guard. It checks the live Clubfinder origin count, canonical Journey Club Registry, entry-round population, overlap, Leatherhead canary, ground-evidence coverage and the resulting 651-club Law 2 population. It writes only an audit JSON report.

The branch-only workflow `.github/workflows/law2-eligibility-audit.yml` runs this audit with read-only repository permissions and uploads the report as an artifact.

Production `clubfinder.html`, `competition.json`, GROUNDS and journey logic are untouched by this audit branch.
