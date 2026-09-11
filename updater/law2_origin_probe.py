#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'clubfinder.html').read_text(encoding='utf-8')

def arr(name):
    m=re.search(rf'(?:const|let|var)\s+{re.escape(name)}\s*=\s*(\[.*?\])\s*;',text,re.S)
    if not m: raise SystemExit(f'ABORT: {name} missing')
    return json.loads(m.group(1))

eligible=arr('ELIGIBLE'); grounds=arr('GROUNDS')
print('LAW2 PROBE eligible count:',len(eligible))
print('LAW2 PROBE eligible sample:',json.dumps(eligible[0],ensure_ascii=False,sort_keys=True))
print('LAW2 PROBE ground sample:',json.dumps(grounds[0],ensure_ascii=False,sort_keys=True))
for club in ('Leatherhead FC','Epsom & Ewell FC','Newton Aycliffe FC'):
    x=next((r for r in eligible if (r.get('name') or r.get('club'))==club),None)
    g=next((r for r in grounds if (r.get('name') or r.get('club'))==club),None)
    print('LAW2 PROBE club',club,'eligible=',json.dumps(x,ensure_ascii=False,sort_keys=True),'ground=',json.dumps(g,ensure_ascii=False,sort_keys=True))
for fn in ('previousRoundsHtml','stateHtml','renderClub'):
    m=re.search(rf'function\s+{fn}\s*\([^)]*\)\s*\{{',text)
    if m:
        print('LAW2 PROBE function',fn,':',text[m.start():m.start()+1200].replace('\n','\\n'))
    else:
        print('LAW2 PROBE function',fn,': NOT FOUND')
