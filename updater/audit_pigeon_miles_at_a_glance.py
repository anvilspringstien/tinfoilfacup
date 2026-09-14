#!/usr/bin/env python3
from pathlib import Path

html=Path('clubfinder.html').read_text(encoding='utf-8')
needles=['AT A GLANCE','At a Glance','Pigeon Miles Travelled','Home Games Played','Away Games Played']
out=['# Pigeon Miles At-a-Glance audit','','READ ONLY. Production data unchanged.','']
seen=set()
for needle in needles:
    start=0
    while True:
        i=html.find(needle,start)
        if i<0: break
        key=(max(0,i-1800),min(len(html),i+2600))
        if key not in seen:
            seen.add(key)
            snippet=html[key[0]:key[1]]
            out += [f'## Match: `{needle}`','', '```html',snippet,'```','']
        start=i+len(needle)
Path('pigeon-miles-at-a-glance-audit.md').write_text('\n'.join(out),encoding='utf-8')
print('PIGEON MILES AT-A-GLANCE AUDIT COMPLETE')
print('Snippets:',len(seen))
