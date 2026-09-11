#!/usr/bin/env python3
"""Read-only verification audit for the 160 added Law 2 origins.

Separates already-canonical guarded locations, explicitly verified supplemental
locations, and the remaining supporting-evidence review queue. It never promotes
records itself.
"""
from pathlib import Path
from collections import Counter
import json,re
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'clubfinder.html'; REG=ROOT/'journey-club-registry.json'
OUT=ROOT/'updater'/'law2-location-verification-audit.json'; MD=ROOT/'law2-location-verification-audit.md'
NEW={'First Round Qualifying','Second Round Qualifying','Fourth Round Qualifying'}

def norm(s):
    s=str(s or '').lower().replace('&',' and ')
    s=re.sub(r'\b(fc|afc|cfc)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def arr(t,n,required=True):
    m=re.search(r'\b(?:const|let|var)\s+'+re.escape(n)+r'\s*=\s*\[',t)
    if not m:
        if required: raise SystemExit(f'ABORT: {n} missing')
        return []
    s=t.find('[',m.start());d=0;ins=False;esc=False;q=''
    for i in range(s,len(t)):
        c=t[i]
        if ins:
            if esc:esc=False
            elif c=='\\':esc=True
            elif c==q:ins=False
        else:
            if c in ('"',"'"):ins=True;q=c
            elif c=='[':d+=1
            elif c==']':
                d-=1
                if d==0:return json.loads(t[s:i+1])
    raise SystemExit(f'ABORT: unbalanced {n}')

text=HTML.read_text(encoding='utf-8'); reg=json.loads(REG.read_text(encoding='utf-8'))
grounds=arr(text,'GROUNDS'); supplemental=arr(text,'LAW2_ORIGIN_LOCATIONS',False)
gby={norm(x.get('name') or x.get('club')):x for x in grounds}; sby={norm(x.get('name') or x.get('club')):x for x in supplemental}
selected=[x for x in reg.get('clubs',[]) if x.get('entry_round') in NEW]
if len(selected)!=160: raise SystemExit(f'ABORT: expected 160 added Law 2 origins, found {len(selected)}')
rows=[]
for x in selected:
    club=x.get('club'); key=norm(club); entry=x.get('entry_round')
    if key in gby:
        g=gby[key]; state='verified-canonical'; source='protected GROUNDS'
    elif key in sby:
        g=sby[key]; state='verified-supplemental' if str(g.get('verification') or '').lower()=='verified' else 'review-supporting-evidence'; source=g.get('verification_source') or g.get('ground_source') or g.get('source') or ''
    else:
        raise SystemExit(f'ABORT: no selectable location for {club}')
    rows.append({'club':club,'entry_round':entry,'state':state,'ground':g.get('ground'),'postcode':g.get('postcode'),'source':source})
counts=Counter(r['state'] for r in rows); round_queue=Counter(r['entry_round'] for r in rows if r['state']=='review-supporting-evidence')
if sum(counts.values())!=160: raise SystemExit('ABORT: Law 2 verification partition drift')
report={'season':'2026-27','added_law2_origins':160,'counts':dict(sorted(counts.items())),'remaining_review_by_entry_round':dict(sorted(round_queue.items())),'clubs':rows,'read_only':True,'automatic_promotion':False}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=['# Law 2 Origin Location Verification Audit','',
    'This is a **read-only** review queue for the 160 clubs added to Clubfinder by the Law 2 expansion. Promotion requires current authoritative evidence and is never inferred from FCHD-only supporting data.','',
    f'- Added Law 2 origins audited: **160**',
    f"- ✅ Already verified in protected GROUNDS: **{counts.get('verified-canonical',0)}**",
    f"- ✅ Verified in guarded Law 2 supplemental layer: **{counts.get('verified-supplemental',0)}**",
    f"- ⚠️ Remaining supporting-evidence review queue: **{counts.get('review-supporting-evidence',0)}**",'',
    '## Remaining review queue by entry round','']
for rnd,n in sorted(round_queue.items()): md.append(f'- **{rnd}: {n}**')
md += ['', '## Remaining clubs', '']
for r in rows:
    if r['state']=='review-supporting-evidence': md.append(f"- **{r['club']}** — {r['ground']} • {r['postcode']} • {r['entry_round']}")
MD.write_text('\n'.join(md)+'\n',encoding='utf-8')
print('LAW 2 LOCATION VERIFICATION AUDIT: SUCCESS')
for k,v in sorted(counts.items()): print(k+':',v)
print('Remaining review queue:',counts.get('review-supporting-evidence',0))
print('READ ONLY: no automatic promotion performed')
