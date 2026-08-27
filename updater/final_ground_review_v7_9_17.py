#!/usr/bin/env python3
import json,re
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
p=R/'clubfinder.html'; t=p.read_text()
def bounds(name):
 m=re.search(r'\b(?:const|let|var)\s+'+re.escape(name)+r'\s*=\s*\[',t)
 if not m: raise SystemExit(name+' not found')
 s=t.find('[',m.start()); d=0; ins=False; esc=False; q=''
 for i in range(s,len(t)):
  c=t[i]
  if ins:
   if esc: esc=False
   elif c=='\\': esc=True
   elif c==q: ins=False
  else:
   if c in ('\"',"'"): ins=True;q=c
   elif c=='[': d+=1
   elif c==']':
    d-=1
    if d==0:return s,i+1
s,e=bounds('GROUNDS'); arr=json.loads(t[s:e]); before=len(arr)
arr=[x for x in arr if (x.get('name') or x.get('club') or '').strip()!='Bottlesford Town FC']
if len(arr)!=before-1: raise SystemExit(f'Expected exactly one Bottlesford Town FC ground, removed {before-len(arr)}')
t=t[:s]+json.dumps(arr,separators=(',',':'))+t[e:]; p.write_text(t)
lp=R/'updater/ground-approval-ledger.json'; ledger=json.loads(lp.read_text())
if not any((x.get('tenant') or '').lower()=='romulus fc' for x in ledger.get('known_groundshares',[])):
 ledger['known_groundshares'].append({'tenant':'Romulus FC','host':'Sutton Coldfield Town FC','ground':"The Domino's Arena / Central Ground",'postcode':'B72 1NL','season':'2026-27','evidence':"Current venue evidence places both clubs at The Domino's Arena, Coles Lane. FCHD explicitly records Romulus at Sutton Coldfield Town FC's Domino's Stadium; current league fixture evidence places both at The Domino's Arena; independent reporting identifies Romulus as groundsharing with Sutton Coldfield Town, consistent with the established landlord/tenant relationship.",'source_url':'https://fchd.info/maps/GAZ.htm','approved_at':datetime.now(timezone.utc).isoformat(),'status':'current','approval_source':'v7.9.17 final evidence review'})
ledger['version']='7.9.17'; ledger['updated_at']=datetime.now(timezone.utc).isoformat(); lp.write_text(json.dumps(ledger,indent=2)+'\n')
print('v7.9.17: removed misspelled duplicate ground Bottlesford Town FC; approved Romulus -> Sutton Coldfield Town FC')
