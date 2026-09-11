#!/usr/bin/env python3
"""Promote explicitly audited Law 2 supplemental origin locations to verified.

This does not alter protected GROUNDS. It only changes verification state inside the
Law 2 supplemental origin layer, and only when club, ground and postcode exactly
match the independently-reviewed ledger.
"""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'clubfinder.html'
LEDGER=ROOT/'updater'/'law2-verified-location-ledger.json'

def norm(s):
    s=str(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def locate(t,n):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(n)+r'\s*=\s*\[',t)
    if not m: return None
    s=t.find('[',m.start()); d=0; ins=False; esc=False; q=''
    for i in range(s,len(t)):
        c=t[i]
        if ins:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q: ins=False
        else:
            if c in ('"',"'"): ins=True; q=c
            elif c=='[': d+=1
            elif c==']':
                d-=1
                if d==0: return s,i+1
    raise SystemExit(f'ABORT: unbalanced {n}')

def compact(x):
    return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

text=HTML.read_text(encoding='utf-8')
ledger=json.loads(LEDGER.read_text(encoding='utf-8'))
p=locate(text,'LAW2_ORIGIN_LOCATIONS')
if not p: raise SystemExit('ABORT: LAW2_ORIGIN_LOCATIONS missing')
rows=json.loads(text[p[0]:p[1]])
by={norm(x.get('name') or x.get('club')):x for x in rows}
verified=ledger.get('verified_locations') or []
if not verified: raise SystemExit('ABORT: verified location ledger is empty')
promoted=[]
for item in verified:
    key=norm(item.get('club'))
    row=by.get(key)
    if not row: raise SystemExit(f"ABORT: supplemental Law 2 location missing for {item.get('club')}")
    expected_ground=str(item.get('ground') or '').strip()
    expected_pc=str(item.get('postcode') or '').strip().upper()
    actual_ground=str(row.get('ground') or '').strip()
    actual_pc=str(row.get('postcode') or '').strip().upper()
    if norm(actual_ground)!=norm(expected_ground) or actual_pc!=expected_pc:
        raise SystemExit(f"ABORT: reviewed location drift for {item.get('club')}: {actual_ground} {actual_pc} != {expected_ground} {expected_pc}")
    sources=item.get('sources') or []
    if not any(s.get('type')=='official_club' and s.get('url') for s in sources):
        raise SystemExit(f"ABORT: {item.get('club')} lacks official-club verification source")
    row['verification']='verified'
    row['verification_label']='✅ Verified'
    row['verification_source']='Guarded Law 2 verified-location ledger'
    row['verified_at']=item.get('verified_at')
    row['verified_sources']=sources
    promoted.append(item.get('club'))
text=text[:p[0]]+compact(rows)+text[p[1]:]
HTML.write_text(text,encoding='utf-8')
print('LAW 2 VERIFIED LOCATION PROMOTION: SUCCESS')
print('Promoted:',len(promoted))
for club in promoted: print('-',club)
print('Protected GROUNDS array: UNTOUCHED')
