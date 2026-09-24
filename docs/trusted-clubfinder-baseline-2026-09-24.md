# Tin Foil FA Cup — guarded Clubfinder baseline (24 September 2026)

## Published source checkpoint

| Component | Fixed revision or content identity |
| --- | --- |
| Source commit immediately following BETA Exmouth correction | `1385aa87396cf053985c38a3f708145cf3ff72a7` |
| Protected production `clubfinder.html` blob | `1123ba2129125fc1bf34a4b72ec5bb1ae3e30dbc` |
| Published BETA `beta/clubfinder-beta.html` blob | `54a33af7f0af4fa703fd654dad335c60d0d2a093` |
| Canonical `competition.json` blob | `cf007dd2bbea5eb6cb80f68880bfc65667ea966d` |
| Canonical and both exact embedded snapshots | `2026-09-24T14:18:33.604895+00:00` |
| Post-merge BETA identity smoke | [successful run 36025446493](https://github.com/anvilspringstien/tinfoilfacup/actions/runs/36025446493) |
| GitHub Pages publication | [successful run 36025444648](https://github.com/anvilspringstien/tinfoilfacup/actions/runs/36025444648) |
| Read-only full cross-version reconciliation | [successful run 36025514906](https://github.com/anvilspringstien/tinfoilfacup/actions/runs/36025514906) |

This checkpoint captures **two deliberately different HTML builds**, not a mandate to synchronise them by copying. Keep production Competition Health and all publishing safeguards intact. Re-run the read-only reconciliation on the latest main before any subsequent production promotion.

## Confirmed behaviour on identical canonical data

- Twelve representative qualifying campaigns agree between production and BETA on current custodian, historical match sequence and next fixture; none of the twelve origins was missing.
- The audit examined 676 distinct historical results, of which 125 contain explicit historical venue details. Zero of those 125 lost their canonical postcode, and there are zero cross-build postcode differences.
- Thame United directly resolves to its verified Third Round Qualifying home tie against Eastbourne Borough on 3 October 2026 at OX9 3RN. Losing Exmouth's direct lookup no longer advances to a fixture in **either** build; the audit exercises the actual live fixture index rather than a null stub.
- The Petts Wood & Holmesdale v Windsor & Eton fixture on 5 September retains the source-specific historical venue **The New Inn Stadium, BR2 8HQ** in both builds.
- The BETA-only 2026 merger identity presents **Petts Wood & Holmesdale FC** at BR2 8HQ and keeps an older Holmesdale saved campaign (including search number and call sign) intact.
- Browser acceptance for saved campaign **#01088** verified the visible club name, five played matches, Eastbourne Borough as current custodian, next Thame fixture and Stats (four completed rounds, five matches, five clubs, 24 goals, five grounds, 124 displayed Pigeon Miles). Mileage arithmetic has a separate deterministic regression; the displayed 124 was browser-observed, not independently recalculated from live postcode coordinates.
- The 8 August Petts Wood home tie retains BR2 8HQ but labels its ground **Ground name unconfirmed** rather than inventing a historical sponsor name.

## Known exceptions; not cleared for unreviewed production promotion

1. **Public merged-club identity remains BETA-only.** Production still has the retired Holmesdale public club record; the twelve sampled parity origins exclude this intentional difference. Browser validation does **not** imply production has received the merged-club UI fix.
2. **26 historical ground-name-only differences** remain for review. Neither build loses any of the 125 explicit historical postcodes. Preserve source-specific historical match venues; do not overwrite with current ground names solely because postcodes match.
3. **Five distinct decided penalty-shootout results** were found. BETA Stats displays verified shootout winners; production's certificate helper returns blank for level scorelines. An undecided draw awaiting a replay correctly remains blank in both.
4. Continue to protect pending replay/conditional-draw alternatives. The BETA Exmouth correction specifically prevents a *verified losing club* from being promoted via a source index; it is not permission to select an unverified winner.
5. Safari multi-tab navigation and Challenge/Stats navigation redesign remain separately parked; neither is included in this checkpoint.

## Change-control gates

The [read-only audit in PR #74](https://github.com/anvilspringstien/tinfoilfacup/pull/74) must continue to pass whenever either build or the competition snapshot changes. Keep fixture-level quarantining and publication work isolated from Clubfinder reconciliation. Do not bypass Competition Health or edit production as a side effect of BETA changes. Preserve the source commit above for rollback and repeat browser acceptance before a separate reviewed production promotion.
