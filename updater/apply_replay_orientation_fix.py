#!/usr/bin/env python3
from pathlib import Path

# Guarded one-time repair hook. It remains in the result-scan watch list, but is
# deliberately semantic/idempotent: later scanner hardening must not fail merely
# because the exact source-text boundary of the original patch has changed.
ROOT=Path(__file__).resolve().parents[1]
AUTO=ROOT/'updater'/'auto_results.py'
RENDER=ROOT/'updater'/'clubfinder_render_regression.js'
PATCH=ROOT/'updater'/'patch_clubfinder_competition_logic.py'

# 1) Result scanner: accept the same canonical pair in reverse order as a replay.
text=AUTO.read_text(encoding='utf-8')
old='''  match=next((f for f in known if norm(f.get("home"))==norm(home) and norm(f.get("away"))==norm(away)),None)\n  if not match:\n   unmatched.append([home,away]); continue\n  date=match.get("date","") or current_date\n  winner=match["home"] if hs>as_ else match["away"] if as_>hs else ""\n  parsed.append({"home":match["home"],"away":match["away"],"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":date,"round":match.get("round",SCAN_ROUND),"source_url":FWP_URL})\n'''
legacy_new='''  match=next((f for f in known if norm(f.get("home"))==norm(home) and norm(f.get("away"))==norm(away)),None)\n  reverse_replay=False\n  if not match:\n   match=next((f for f in known if norm(f.get("home"))==norm(away) and norm(f.get("away"))==norm(home)),None)\n   reverse_replay=match is not None\n  if not match:\n   unmatched.append([home,away]); continue\n  # Original ties must retain canonical orientation. A completed row with the\n  # same two clubs reversed is the replay at the opposite venue, so preserve\n  # the observed orientation/date and label it explicitly as a replay.\n  if reverse_replay:\n   out_home,out_away=home,away\n   date=current_date or match.get("date","")\n   round_name=SCAN_ROUND+" Replay"\n  else:\n   out_home,out_away=match["home"],match["away"]\n   date=match.get("date","") or current_date\n   round_name=match.get("round",SCAN_ROUND)\n  winner=out_home if hs>as_ else out_away if as_>hs else ""\n  parsed.append({"home":out_home,"away":out_away,"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":date,"round":round_name,"source_url":FWP_URL})\n'''
if 'reverse_replay=False' not in text or 'round_name=SCAN_ROUND+" Replay"' not in text:
    if old in text:
        text=text.replace(old,legacy_new,1)
    else:
        raise SystemExit('ABORT: auto_results no longer proves reverse-orientation replay handling')
# Semantic postcondition rather than an exact-text equality check. The current
# scanner may have extra sources/arguments while retaining the same protection.
if 'reverse_replay=False' not in text or 'round_name=SCAN_ROUND+" Replay"' not in text:
    raise SystemExit('ABORT: auto_results replay orientation postcondition failed')
AUTO.write_text(text,encoding='utf-8')

# 2) Journey winner helper: a decisive score always beats a stale draw-replay flag.
text=PATCH.read_text(encoding='utf-8')
old="""function canonicalResultWinner(r){\n  if(!r)return '';\n  if(r.decision==='draw-replay')return '';\n  const hs=Number(r.home_score),as=Number(r.away_score);\n  if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as)return hs>as?r.home:r.away;\n  return r.winner||'';\n}"""
new="""function canonicalResultWinner(r){\n  if(!r)return '';\n  const hs=Number(r.home_score),as=Number(r.away_score);\n  if(Number.isFinite(hs)&&Number.isFinite(as)&&hs!==as)return hs>as?r.home:r.away;\n  if(r.decision==='draw-replay')return '';\n  return r.winner||'';\n}"""
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('ABORT: canonicalResultWinner boundary not found')
PATCH.write_text(text,encoding='utf-8')

# 3) This repair script must never revert newer regression assertions.
# The canonical rendered regression is source-controlled and already tests the
# historical Bishop/Emley and Exmouth/Banbury replays alongside the final
# Exmouth/Thame custodian transition. Check it without modifying its contents.
text=RENDER.read_text(encoding='utf-8')
required_markers=(
    "const bishop=ELIGIBLE.find(c=>same(c.name,'Bishop Auckland FC'))",
    "const exmouth=ELIGIBLE.find(c=>same(c.name,'Exmouth Town FC'))",
    "const exmouthSecondQReplay=canonicalHistory.find(",
    "Thame should become custodian after verified Exmouth 1–3 Thame replay",
    "Exmouth should remain custodian until a published Second Qualifying result advances it",
)
missing=[marker for marker in required_markers if text.count(marker)!=1]
if missing or "Exmouth Town should remain custodian after winning replay" in text:
    raise SystemExit("ABORT: rendered replay regression coverage is stale or incomplete: "
                     + repr(missing))
# Deliberately no RENDER.write_text(): a replay-orientation repair may never
# overwrite a later, source-owned custodian assertion.

print('REPLAY ORIENTATION FIX: SUCCESS')
print('Scanner proves reversed home/away replay handling semantically.')
print('Decisive replay scores override stale draw-replay flags.')
print('Rendered Bishop/Emley, Exmouth/Banbury and Exmouth/Thame regressions preserved.')
