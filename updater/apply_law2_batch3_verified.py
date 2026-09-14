#!/usr/bin/env python3
"""Prepare reviewed Law 2 batch 3 using the established guarded ledger."""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'clubfinder.html'
LEDGER=ROOT/'updater'/'law2-verified-location-ledger.json'
EVIDENCE=ROOT/'updater'/'law2-batch3-evidence.json'

def norm(s):
    s=str(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def locate(t,n):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(n)+r'\s*=\s*\[',t)
    if not m: raise SystemExit(f'ABORT: {n} missing')
    s=t.find('[',m.start()); d=0; ins=False; esc=False; q=''
    for i in range(s,len(t)):
        c=t[i]
        if ins:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q: ins=False
        else:
            if c in ('"',"'"): ins=True;q=c
            elif c=='[': d+=1
            elif c==']':
                d-=1
                if d==0: return s,i+1
    raise SystemExit(f'ABORT: unbalanced {n}')

def compact(x):
    return json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

text=HTML.read_text(encoding='utf-8')
evidence=json.loads(EVIDENCE.read_text(encoding='utf-8'))
ledger=json.loads(LEDGER.read_text(encoding='utf-8'))
items=evidence.get('verified_locations') or []
holds=evidence.get('held_for_review') or []
if len(items)!=9: raise SystemExit(f'ABORT: expected 9 verified batch items, got {len(items)}')
if len(holds)!=1: raise SystemExit(f'ABORT: expected 1 held item, got {len(holds)}')

p=locate(text,'LAW2_ORIGIN_LOCATIONS')
rows=json.loads(text[p[0]:p[1]])
by={norm(x.get('name') or x.get('club')):x for x in rows}

for item in items:
    club=item['club']; row=by.get(norm(club))
    if not row: raise SystemExit(f'ABORT: supplemental record missing for {club}')
    if str(row.get('verification') or '').lower()=='verified':
        raise SystemExit(f'ABORT: {club} unexpectedly already verified')
    old_pc=str(row.get('postcode') or '').strip().upper()
    new_pc=str(item['postcode']).strip().upper()
    if old_pc!=new_pc:
        raise SystemExit(f'ABORT: postcode drift needs explicit coordinate review for {club}: {old_pc} -> {new_pc}')
    # Ground naming may be refreshed when the current official club source uses a newer
    # stadium/sponsorship label but the verified postcode is unchanged.
    row['ground']=item['ground']
    row['ground_source']='Law 2 independently reviewed current home-ground evidence'

for held in holds:
    row=by.get(norm(held['club']))
    if not row: raise SystemExit(f'ABORT: held supplemental record missing for {held["club"]}')
    if str(row.get('verification') or '').lower()=='verified':
        raise SystemExit(f'ABORT: held club unexpectedly verified: {held["club"]}')

text=text[:p[0]]+compact(rows)+text[p[1]:]
HTML.write_text(text,encoding='utf-8')

existing=ledger.setdefault('verified_locations',[])
existing_by={norm(x.get('club')):x for x in existing}
for item in items:
    canonical={
        'club':item['club'],'ground':item['ground'],'postcode':item['postcode'],
        'verified_at':evidence['reviewed_at'],'sources':item['sources']
    }
    key=norm(item['club'])
    if key in existing_by:
        old=existing_by[key]
        if old!=canonical: raise SystemExit(f'ABORT: ledger already contains differing record for {item["club"]}')
    else:
        existing.append(canonical)
ledger['verified_locations']=existing
LEDGER.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('LAW 2 BATCH 3 PREPARATION: SUCCESS')
print('Reviewed promotions prepared:',len(items))
print('Held for review:',', '.join(x['club'] for x in holds))
