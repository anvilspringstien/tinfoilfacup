from pathlib import Path
import json
import re

HTML=Path('clubfinder.html')
COMP=Path('competition.json')
OUT=Path('clubfinder-payload-classification.md')
text=HTML.read_text(encoding='utf-8')

def fmt(n):
    return f"{n:,} bytes ({n/1024:.1f} KiB)"

def assignment_span(name):
    m=re.search(rf'\b(?:const|let|var)\s+{re.escape(name)}\s*=',text)
    if not m:return None
    start=m.start(); i=m.end(); depth=0; quote=None; esc=False
    while i<len(text):
        ch=text[i]
        if quote:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==quote: quote=None
            i+=1; continue
        if ch in "'\"`": quote=ch
        elif ch in '([{': depth+=1
        elif ch in ')]}': depth=max(0,depth-1)
        elif ch==';' and depth==0:
            return start,i+1
        i+=1
    return None

def payload(name):
    span=assignment_span(name)
    if not span:return None,None
    a,b=span
    eq=text.find('=',a,b)
    return text[eq+1:b-1].strip(),span

names=['EMBEDDED_COMPETITION_DATA','doc','GROUNDS','ELIGIBLE','PRELIM_FIXTURES_BY_CLUB','LAW2_ORIGIN_LOCATIONS','EPR_RESULTS_BY_TIE','CLUB_WEBSITES','CURRENT_RESULT_OVERRIDES','NEXT_FIXTURE_OVERRIDES']
rows=[]
for name in names:
    val,span=payload(name)
    if not span:continue
    a,b=span
    size=len(text[a:b].encode())
    outside=text[:a]+text[b:]
    refs=len(re.findall(rf'\b{re.escape(name)}\b',outside))
    datauris=len(re.findall(r'data:[\w.+-]+/[\w.+-]+;base64,',text[a:b]))
    rows.append((name,size,refs,datauris))

embedded_equal=False
v,_=payload('EMBEDDED_COMPETITION_DATA')
if v:
    embedded=json.loads(v.replace('<\\/script','</script'))
    canonical=json.loads(COMP.read_text(encoding='utf-8'))
    embedded_equal=(embedded==canonical)

# Data URI ownership by containing assignment.
ownership=[]
for idx,m in enumerate(re.finditer(r'data:([\w.+-]+/[\w.+-]+);base64,([A-Za-z0-9+/=]+)',text),1):
    owner='unassigned/global'
    for name in names:
        sp=assignment_span(name)
        if sp and sp[0]<=m.start()<sp[1]: owner=name; break
    ownership.append((idx,owner,len(m.group(0).encode()),m.group(1)))

classification={
'EMBEDDED_COMPETITION_DATA':('required standalone fallback, but duplicated canonical payload','Semantically identical to competition.json; retained so Clubfinder still works when the live JSON fetch fails.'),
'doc':('live application output mixed with replaceable static assets','Stats certificate HTML is live behaviour, but large inline image data can be externalised without changing certificate logic.'),
'GROUNDS':('live core/static location payload','Used by current venue, map and journey fallback logic; candidate for extraction to a generated data file, not deletion.'),
'ELIGIBLE':('live core/static origin payload','Drives the postcode nearest-club search and entry-round metadata; candidate for extraction, not deletion.'),
'PRELIM_FIXTURES_BY_CLUB':('evolutionary fallback candidate','Older preliminary-round lookup still referenced. Must prove behavioural equivalence against competition.json before removal.'),
'LAW2_ORIGIN_LOCATIONS':('live protected origin payload','Current Law 2 origin-location protection. Candidate for generated external data once validation is complete.'),
'EPR_RESULTS_BY_TIE':('evolutionary fallback candidate','Hard-coded early-round results still referenced. Likely removable only after proving canonical competition data fully covers every protected journey.'),
'CLUB_WEBSITES':('small live static payload','Negligible size; no reason to optimise first.'),
'CURRENT_RESULT_OVERRIDES':('small compatibility layer','Tiny guarded override layer; keep until its cases are absorbed into canonical data and regression-tested.'),
'NEXT_FIXTURE_OVERRIDES':('small compatibility layer','Tiny guarded override layer; keep until canonical fixtures make it redundant.'),
}

lines=['# Clubfinder Payload Classification','',
'Read-only second-stage audit. Production Clubfinder is not modified. Reference counts below are identifier uses outside each declaration, so zero would be a strong dead-code signal; non-zero means only that the payload is still wired somewhere, not that it is irreducible.','',
'## Key finding','',
f'- Embedded competition snapshot exactly matches `competition.json`: **{"YES" if embedded_equal else "NO"}**.',
'- The largest obvious saving is therefore architectural, not algorithmic: the same canonical competition state exists both as a live JSON file and as an inline offline fallback.',
'- The second large saving is static certificate artwork embedded as base64 data URIs.','',
'## Payload classification','']
for name,size,refs,datauris in rows:
    cls,note=classification.get(name,('unclassified',''))
    lines += [f'### `{name}`',f'- Size: **{fmt(size)}**',f'- References outside declaration: **{refs}**',f'- Embedded data URIs inside assignment: **{datauris}**',f'- Classification: **{cls}**',f'- {note}','']
lines += ['## Embedded image ownership','']
byowner={}
for idx,owner,size,mime in ownership:
    byowner.setdefault(owner,[0,0]); byowner[owner][0]+=1; byowner[owner][1]+=size
for owner,(count,size) in sorted(byowner.items(),key=lambda kv:kv[1][1],reverse=True):
    lines.append(f'- `{owner}`: **{count} image(s), {fmt(size)}**')
lines += ['','## Clean-sheet implication','',
'A smaller Clubfinder should be built beside v7.6 from the settled requirements, with generated data separated from application code. The safest target architecture is: a small HTML/CSS/JS shell; canonical competition data loaded from `competition.json`; compact generated origin/ground data; certificate images as ordinary static assets; and an optional explicit offline snapshot only if offline/fetch-failure resilience remains a requirement.','',
'Before deleting the preliminary/EPR fallback tables, run the full journey/replay/render regression suite with those tables deliberately disabled. That is the proof point for whether they are genuine evolutionary baggage or still required compatibility data.']
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('\n'.join(lines))
