#!/usr/bin/env python3
"""Promote explicitly audited Law 2 supplemental origin locations to verified.

This does not alter protected GROUNDS. It only changes verification state inside the
Law 2 supplemental origin layer, and only when club, ground and postcode exactly
match the independently-reviewed ledger.

All missing/drifted reviewed locations are collected before aborting so a guarded
run reports the complete reconciliation queue rather than only the first mismatch.
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

# First pass: validate the complete reviewed set without mutating any row.
# Keep fail-closed behaviour, but report every reconciliation problem together.
problems=[]
for item in verified:
    club=item.get('club')
    key=norm(club)
    row=by.get(key)
    if not row:
        problems.append(f"supplemental Law 2 location missing for {club}")
        continue
    expected_ground=str(item.get('ground') or '').strip()
    expected_pc=str(item.get('postcode') or '').strip().upper()
    actual_ground=str(row.get('ground') or '').strip()
    actual_pc=str(row.get('postcode') or '').strip().upper()
    if norm(actual_ground)!=norm(expected_ground) or actual_pc!=expected_pc:
        problems.append(f"reviewed location drift for {club}: {actual_ground} {actual_pc} != {expected_ground} {expected_pc}")
    sources=item.get('sources') or []
    if not any(s.get('type')=='official_club' and s.get('url') for s in sources):
        problems.append(f"{club} lacks official-club verification source")

if problems:
    print(f'LAW 2 VERIFIED LOCATION PROMOTION: ABORT — {len(problems)} review problem(s)')
    for problem in problems:
        print('-',problem)
    raise SystemExit(1)

# Second pass: promotion occurs only when the whole reviewed set is clean.
promoted=[]
for item in verified:
    row=by[norm(item.get('club'))]
    sources=item.get('sources') or []
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
