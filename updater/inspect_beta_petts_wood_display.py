#!/usr/bin/env python3
from pathlib import Path
import re
s=Path("beta/clubfinder-beta.html").read_text(encoding="utf-8")
terms=["Holmesdale FC","This Campaign starts with","<h2>","stats-origin","STARTED WITH","origin.name","saveJourney","loadSavedJourney","currentCustodian","originName"]
for term in terms:
    ms=list(re.finditer(re.escape(term),s,re.I))
    print(f"TERM {term!r} COUNT {len(ms)}")
    for i,m in enumerate(ms[:14],1):
        a=max(0,m.start()-1300); b=min(len(s),m.end()+2600)
        prefix=s[max(0,m.start()-6000):m.start()]
        funcs=list(re.finditer(r"(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\([^)]*\)\s*\{",prefix))
        fn=funcs[-1].group(1) if funcs else "(top-level)"
        print(f"--- {term} #{i} @ {m.start()} enclosing={fn} ---")
        print(s[a:b].replace("\r",""))
        print("--- END ---")
print("ELIGIBLE_HOLMESDALE", re.findall(r'\{"name":"Holmesdale FC"[^}]*\}',s)[:3])
