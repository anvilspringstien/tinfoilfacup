# Extra Preliminary legacy reconciliation

READ ONLY. No production data changed.

- Legacy rows inspected: **218**
- Football Web Pages dated rows available: **260**
- Exact same orientation + score matches after known club-alias normalisation: **215**
- Exact score/team matches with home/away reversed: **0**
- Team-pair matches but score/status differs: **1**
- No source pair found in audited dates: **2**

## Alias normalisation used

- `afc varndeanians` → `afc varndenians`
- `atherton lr` → `atherton laburnum rovers`
- `bedfont sports club` → `bedfont sports`
- `bournemouth poppies` → `bournemouth`
- `eastwood community` → `eastwood cfc`
- `irlam` → `irlam town`
- `royal wootton bassett town` → `royal wootton bassett`
- `sherborne town` → `sherbourne town`

## Orientation differences

None.

## Same clubs, different recorded score/status

- Tie 66: **Abbey Hulton United None-None Kidsgrove Athletic**; legacy decision=`walkover`; legacy winner=`Abbey Hulton United FC`
  - FWP 2026-08-08 Extra Preliminary Round: Kidsgrove Athletic 0-0 Abbey Hulton United; status=FT; source=https://www.footballwebpages.co.uk/fa-cup/20260808

## Unmatched legacy rows

- Tie 9: **Marske United None-None Boro Rangers**; legacy decision=`walkover`; legacy winner=`Marske United FC`
- Tie 155: **AFC Varndeanians 1-3 Eastbourne Town**; legacy decision=``; legacy winner=`Eastbourne Town FC`

## Migration rule

Only exact dated source matches should be auto-promoted. Known club-name aliases above are identity normalisation only, not score/result overrides. Pair-only and unmatched rows remain fail-closed for manual review.
