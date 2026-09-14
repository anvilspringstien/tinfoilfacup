# Extra Preliminary legacy reconciliation

READ ONLY. No production data changed.

- Legacy rows inspected: **218**
- Football Web Pages dated rows available: **260**
- Exact same orientation + score matches: **208**
- Exact score/team matches with home/away reversed: **0**
- Team-pair matches but score/status differs: **1**
- No source pair found in audited dates: **9**

## Orientation differences

None.

## Same clubs, different recorded score/status

- Tie 66: **Abbey Hulton United None-None Kidsgrove Athletic**; legacy decision=`walkover`; legacy winner=`Abbey Hulton United FC`
  - FWP 2026-08-08 Extra Preliminary Round: Kidsgrove Athletic 0-0 Abbey Hulton United; status=FT; source=https://www.footballwebpages.co.uk/fa-cup/20260808

## Unmatched legacy rows

- Tie 9: **Marske United None-None Boro Rangers**; legacy decision=`walkover`; legacy winner=`Marske United FC`
- Tie 16: **Euxton Villa 6-0 Atherton LR**; legacy decision=``; legacy winner=`Euxton Villa FC`
- Tie 31: **Hallam 0-3 Irlam**; legacy decision=``; legacy winner=`Irlam FC`
- Tie 80: **Loughborough Students 1-2 Eastwood Community**; legacy decision=``; legacy winner=`Eastwood Community FC`
- Tie 110: **Bedfont Sports Club 0-1 Concord Rangers**; legacy decision=``; legacy winner=`Concord Rangers FC`
- Tie 149: **Royal Wootton Bassett Town 0-2 Winslow United**; legacy decision=``; legacy winner=`Winslow United FC`
- Tie 155: **AFC Varndeanians 1-3 Eastbourne Town**; legacy decision=``; legacy winner=`Eastbourne Town FC`
- Tie 196: **Sherborne Town 1-3 Baffins Milton Rovers**; legacy decision=``; legacy winner=`Baffins Milton Rovers FC`
- Tie 210: **Bournemouth Poppies 1-2 Downton**; legacy decision=``; legacy winner=`Downton FC`

## Migration rule

Only exact dated source matches should be auto-promoted. Orientation differences may be normal replay/home-away differences and require chronology-aware handling. Pair-only and unmatched rows remain fail-closed for manual review.
