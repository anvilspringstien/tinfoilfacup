#!/usr/bin/env python3
from pathlib import Path

# Guarded one-time repair hook: keeping this file in the result-scan watch list
# also gives the live scanner an explicit push event after the workflow update.
ROOT=Path(__file__).resolve().parents[1]
AUTO=ROOT/'updater'/'auto_results.py'
RENDER=ROOT/'updater'/'clubfinder_render_regression.js'
PATCH=ROOT/'updater'/'patch_clubfinder_competition_logic.py'

# 1) Result scanner: accept the same canonical pair in reverse order as a replay.
text=AUTO.read_text(encoding='utf-8')
old='''  match=next((f for f in known if norm(f.get("home"))==norm(home) and norm(f.get("away"))==norm(away)),None)\n  if not match:\n   unmatched.append([home,away]); continue\n  date=match.get("date","") or current_date\n  winner=match["home"] if hs>as_ else match["away"] if as_>hs else ""\n  parsed.append({"home":match["home"],"away":match["away"],"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":date,"round":match.get("round",SCAN_ROUND),"source_url":FWP_URL})\n'''
new='''  match=next((f for f in known if norm(f.get("home"))==norm(home) and norm(f.get("away"))==norm(away)),None)\n  reverse_replay=False\n  if not match:\n   match=next((f for f in known if norm(f.get("home"))==norm(away) and norm(f.get("away"))==norm(home)),None)\n   reverse_replay=match is not None\n  if not match:\n   unmatched.append([home,away]); continue\n  # Original ties must retain canonical orientation. A completed row with the\n  # same two clubs reversed is the replay at the opposite venue, so preserve\n  # the observed orientation/date and label it explicitly as a replay.\n  if reverse_replay:\n   out_home,out_away=home,away\n   date=current_date or match.get("date","")\n   round_name=SCAN_ROUND+" Replay"\n  else:\n   out_home,out_away=match["home"],match["away"]\n   date=match.get("date","") or current_date\n   round_name=match.get("round",SCAN_ROUND)\n  winner=out_home if hs>as_ else out_away if as_>hs else ""\n  parsed.append({"home":out_home,"away":out_away,"home_score":hs,"away_score":as_,"winner":winner,"status":"FT","decision":"","date":date,"round":round_name,"source_url":FWP_URL})\n'''
if old in text:
    text=text.replace(old,new,1)
elif new not in text:
    raise SystemExit('ABORT: auto_results replay parser boundary not found')
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

# 3) Replace the now-stale Bishop replay-pending regression with completed replay checks,
#    and add Exmouth as the user-reported regression case.
text=RENDER.read_text(encoding='utf-8')
start=text.index("  const bishop=ELIGIBLE.find(c=>same(c.name,'Bishop Auckland FC'));\n")
end=text.index("\n  const sporting=ELIGIBLE.find",start)
replacement="""  const bishop=ELIGIBLE.find(c=>same(c.name,'Bishop Auckland FC'));\n  if(!bishop)throw new Error('DL5 regression: Bishop Auckland FC not found in ELIGIBLE');\n  const bishopJourney=buildJourney(bishop);\n  const bishopHistory=(bishopJourney.breadcrumbs||[]).map(x=>x.result||{});\n  const bishopDraw=bishopHistory.find(r=>same(r.home,'Emley AFC')&&same(r.away,'Bishop Auckland')&&Number(r.home_score)===1&&Number(r.away_score)===1&&/First Round Qualifying/i.test(r.round||''));\n  const bishopReplay=bishopHistory.find(r=>same(r.home,'Bishop Auckland')&&same(r.away,'Emley AFC')&&Number(r.home_score)===0&&Number(r.away_score)===2);\n  if(!bishopDraw)throw new Error('Replay regression: Emley 1-1 Bishop Auckland First Qualifying draw missing');\n  if(!bishopReplay)throw new Error('Replay regression: Bishop Auckland 0-2 Emley replay missing');\n  if(!same((bishopJourney.carrier||bishop).name,'Emley AFC'))throw new Error('Replay regression: expected Emley AFC to become custodian after Bishop replay');\n\n  const exmouth=ELIGIBLE.find(c=>same(c.name,'Exmouth Town FC'));\n  if(!exmouth)throw new Error('Replay regression: Exmouth Town FC not found in ELIGIBLE');\n  const exmouthJourney=buildJourney(exmouth);\n  const exmouthHistory=(exmouthJourney.breadcrumbs||[]).map(x=>x.result||{});\n  const exmouthDraw=exmouthHistory.find(r=>same(r.home,'Banbury United')&&same(r.away,'Exmouth Town')&&Number(r.home_score)===0&&Number(r.away_score)===0);\n  const exmouthReplay=exmouthHistory.find(r=>same(r.home,'Exmouth Town')&&same(r.away,'Banbury United')&&Number(r.home_score)===2&&Number(r.away_score)===1);\n  if(!exmouthDraw)throw new Error('Replay regression: Banbury United 0-0 Exmouth Town draw missing');\n  if(!exmouthReplay)throw new Error('Replay regression: Exmouth Town 2-1 Banbury United replay missing');\n  if(!same((exmouthJourney.carrier||exmouth).name,'Exmouth Town'))throw new Error('Replay regression: Exmouth Town should remain custodian after winning replay');\n"""
text=text[:start]+replacement+text[end:]
text=text.replace("  console.log('Emley-Bishop Auckland replay-pending state: PASS');\n  console.log('Bishop IF THROUGH fixture:',bishopNext&&bishopNext.knownFixture?(bishopNext.knownFixture.home+' v '+bishopNext.knownFixture.away):'not yet mapped');\n","  console.log('Bishop Auckland 0-2 Emley replay: PASS');\n  console.log('Exmouth Town 2-1 Banbury United replay: PASS');\n")
RENDER.write_text(text,encoding='utf-8')

print('REPLAY ORIENTATION FIX: SUCCESS')
print('Scanner recognises reversed home/away as replay of canonical pair.')
print('Decisive replay scores override stale draw-replay flags.')
print('Rendered regressions now cover Bishop Auckland/Emley and Exmouth/Banbury.')
