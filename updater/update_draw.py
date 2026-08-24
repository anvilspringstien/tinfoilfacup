#!/usr/bin/env python3
import json, re, sys, urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
JSON_PATH=ROOT/"competition.json"
SOURCE_URL=sys.argv[1] if len(sys.argv)>1 else ""
ROUND=sys.argv[2] if len(sys.argv)>2 else "First Round Qualifying"
DATE=sys.argv[3] if len(sys.argv)>3 else "2026-09-05"

if not SOURCE_URL:
    raise SystemExit("Usage: update_draw.py SOURCE_URL [ROUND] [YYYY-MM-DD]")

req=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"TinFoilFACupDataUpdater/1.0"})
raw=urllib.request.urlopen(req,timeout=30).read()

# PDFs from the FA are often text-extractable only with a PDF library. To keep the
# GitHub job dependency-light, use pdftotext when content is PDF; otherwise decode HTML/text.
ctype=""
try: ctype=urllib.request.urlopen(req,timeout=30).headers.get("Content-Type","")
except Exception: pass
tmp=ROOT/"updater"/"_source"
tmp.write_bytes(raw)
if raw[:4]==b"%PDF" or "pdf" in ctype.lower():
    import subprocess
    txt=tmp.with_suffix(".txt")
    subprocess.run(["pdftotext","-layout",str(tmp),str(txt)],check=True)
    text=txt.read_text(errors="ignore")
else:
    text=raw.decode("utf-8","ignore")
    text=re.sub(r"<[^>]+>"," ",text)

# Parse official draw-style lines. Supports leading tie numbers and unresolved "or" clubs.
lines=[]
for line in text.splitlines():
    line=re.sub(r"\s+"," ",line).strip()
    line=re.sub(r"^\d+\s+","",line)
    if re.search(r"\s+v(?:\.|s\.?)?\s+",line,re.I):
        parts=re.split(r"\s+v(?:\.|s\.?)?\s+",line,maxsplit=1,flags=re.I)
        if len(parts)==2 and parts[0] and parts[1]:
            lines.append((parts[0].strip(" ."),parts[1].strip(" .")))

if not lines:
    raise SystemExit("Validation failed: no draw ties parsed; existing JSON left unchanged.")

data=json.loads(JSON_PATH.read_text())
fixtures={}
suffix=re.compile(r"\s+(FC|AFC|CFC)$",re.I)

def alternatives(side):
    # Draws use "Club A or Club B"; register each candidate so a replay winner resolves.
    return [x.strip() for x in re.split(r"\s+or\s+",side,flags=re.I) if x.strip()]

for home,away in lines:
    rec={"round":ROUND,"home":home,"away":away,"date":DATE,"kickoff":"15:00"}
    if " or " in home.lower() or " or " in away.lower(): rec["conditional"]=True
    for club in alternatives(home)+alternatives(away):
        fixtures[club]=rec
        short=suffix.sub("",club)
        fixtures.setdefault(short,rec)

# Fail-safe sanity checks.
if len(lines)<20:
    raise SystemExit(f"Validation failed: only {len(lines)} ties parsed; existing JSON left unchanged.")
if ROUND=="First Round Qualifying" and len(lines)<100:
    raise SystemExit(f"Validation failed: expected ~112 ties, parsed {len(lines)}; existing JSON left unchanged.")

data["fixtures"]=fixtures
data["updated_at"]=datetime.now(timezone.utc).isoformat()
data["source_url"]=SOURCE_URL
tmpout=JSON_PATH.with_suffix(".json.new")
tmpout.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
tmpout.replace(JSON_PATH)
print(f"Published {len(lines)} {ROUND} ties to competition.json")
