#!/usr/bin/env python3
from pathlib import Path
import re

html=Path('clubfinder.html').read_text(encoding='utf-8')
needles=['EPR_RESULTS_BY_TIE','EMBEDDED_COMPETITION_DATA','competitionData','COMPETITION','resultsBy','buildJourney','canonicalResultWinner']
out=['# Extra Preliminary runtime path audit','','READ ONLY. Production data unchanged.','']
seen=[]
for needle in needles:
    matches=[m.start() for m in re.finditer(re.escape(needle),html)]
    out += [f'## `{needle}`',f'Matches: **{len(matches)}**','']
    for n,i in enumerate(matches[:12],1):
        a=max(0,i-900); b=min(len(html),i+1500)
        snippet=html[a:b]
        # redact embedded image payloads if any wander into context
        snippet=re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+','DATA_IMAGE_REDACTED',snippet)
        out += [f'### {n}','```js',snippet,'```','']
Path('epr-runtime-path-audit.md').write_text('\n'.join(out),encoding='utf-8')
print('EPR RUNTIME PATH AUDIT COMPLETE')
