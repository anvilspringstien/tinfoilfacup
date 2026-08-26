#!/usr/bin/env python3
import json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'competition.json'
if len(sys.argv)<8: raise SystemExit('Usage: update_result.py HOME AWAY HS AS ROUND DATE SOURCE [DECISION]')
home,away=sys.argv[1].strip(),sys.argv[2].strip()
hs,as_=int(sys.argv[3]),int(sys.argv[4])
rnd,date,src=sys.argv[5].strip(),sys.argv[6].strip(),sys.argv[7].strip()
decision=sys.argv[8].strip() if len(sys.argv)>8 else ''
if hs<0 or as_<0: raise SystemExit('Negative score invalid')
if hs==as_ and not decision: raise SystemExit('Level result needs decision')
winner=home if hs>as_ else away if as_>hs else ''
if hs==as_ and decision.lower()!='draw-replay':
    m=re.search(r'winner\s*:\s*([^;]+)',decision,re.I)
    if m: winner=m.group(1).strip()
result={'home':home,'away':away,'home_score':hs,'away_score':as_,'winner':winner,'status':'FT','decision':decision,'date':date,'round':rnd,'source_url':src}
data=json.loads(P.read_text(encoding='utf-8'))
results=data.setdefault('results',{}); replays=data.setdefault('replays',{})
suffix=re.compile(r'\s+(FC|AFC|CFC)$',re.I)
def aliases(n):
    s={n,suffix.sub('',n)}
    if not suffix.search(n): s|={n+' FC',n+' AFC'}
    return {x for x in s if x}
for club in aliases(home)|aliases(away): results[club]=result
shorts={suffix.sub('',home),suffix.sub('',away)}
for club in list(replays):
    if suffix.sub('',club) in shorts: replays.pop(club,None)
data['updated_at']=datetime.now(timezone.utc).isoformat()
data['last_result_source_url']=src; data['last_result_round']=rnd
data['last_result']={'home':home,'away':away,'home_score':hs,'away_score':as_,'winner':winner,'date':date}
tmp=P.with_suffix('.json.new'); tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); tmp.replace(P)
print(f'SUCCESS: {home} {hs}-{as_} {away}')
print('Winner:',winner or 'No winner')
print('Fixtures preserved:',len(data.get('fixtures',{})))
