from pathlib import Path
import re
s=Path("beta/clubfinder-beta.html").read_text(encoding="utf-8")
lines=s.splitlines()
for name in ("journeyCertificate", "tinFoilMaybeOpenCanonicalStatsRoute","tinFoilCompetitionReady"):
    matches=[i for i,line in enumerate(lines) if name in line]
    print("###",name,"occurrences", [i+1 for i in matches[:15]])
    for i in matches[:3]:
        lo=max(0,i-2);hi=min(len(lines),i+(265 if name=="journeyCertificate" and i < 1600 else 28))
        for j in range(lo,hi):
            line=lines[j]
            if len(line)>400: line=line[:400]+"... [trimmed]"
            print(f"{j+1:>5} {line}")
        print("### END")
print("Source size",len(s.encode()),"lines",len(lines))
