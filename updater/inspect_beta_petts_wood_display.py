#!/usr/bin/env python3
from pathlib import Path
import re
s=Path("beta/clubfinder-beta.html").read_text(encoding="utf-8")
terms=["Holmesdale FC","This Campaign starts with","campaign starts with","Nearest:","buildJourney","campaignOrigin","origin.name","club.name","heading","stats"]
for term in terms:
    ms=list(re.finditer(re.escape(term),s,re.I))
    print(f"TERM {term!r} COUNT {len(ms)}")
    for i,m in enumerate(ms[:12],1):
        a=max(0,m.start()-900); b=min(len(s),m.end()+1800)
        print(f"--- {term} #{i} @ {m.start()} ---")
        print(s[a:b].replace("\r",""))
        print("--- END ---")
