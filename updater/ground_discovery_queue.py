#!/usr/bin/env python3
import difflib,html,json,re,urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"clubfinder.html"
REPORT=ROOT/"ground-discovery-queue.md"
JSON_REPORT=ROOT/"updater/ground-discovery-queue.json"
SOURCE_URL="https://fchd.info/maps/GAZ.htm"
BATCH_SIZE=25

def norm(s):
    s=html.unescape(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc|football club)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def extract_js_array(text,name):
    m=re.search(r"\b(?:const|let|var)\s+"+re.escape(name)+r"\s*=\s*\[",text)
    if not m: raise SystemExit(f"Could not find {name} array")
    st=text.find("[",m.start());depth=0;ins=False;esc=False;q=""
    for i in range(st,len(text)):
        c=text[i]
        if ins:
            if esc:esc=False
            elif c=="\\":esc=True
            elif c==q:ins=False
        else:
            if c in ("'",'"'):ins=True;q=c
            elif c=="[":depth+=1
            elif c=="]":
                depth-=1
                if depth==0:return json.loads(text[st:i+1])
    raise SystemExit(f"Unbalanced {name} array")

def fetch_source():
    req=urllib.request.Request(SOURCE_URL,headers={
        "User-Agent":"Mozilla/5.0 TinFoilFACupGroundDiscovery/7.6.4",
        "Accept":"text/html,*/*"
    })
    with urllib.request.urlopen(req,timeout=40) as r:
        return r.read().decode("utf-8","replace")

def clean_markup(s):
    s=re.sub(r"<br\s*/?>","\n",s,flags=re.I)
    s=re.sub(r"<[^>]+>","\n",s)
    return [html.unescape(x).strip(" \t\r\n|") for x in s.splitlines()
            if html.unescape(x).strip(" \t\r\n|")]

def parse_fchd(raw):
    # The Gazetteer uses H3 club headings. Capture each heading and the content
    # until the next H3/H1; retain raw lines because groundshares can add a host-club line.
    pat=re.compile(r"<h3\b[^>]*>(.*?)</h3>(.*?)(?=<h3\b|<h1\b|$)",re.I|re.S)
    pc_re=re.compile(r"\b(?:GIR 0AA|(?:[A-Z]{1,2}\d[A-Z\d]?|\d[A-Z]{2})\s*\d[A-Z]{2})\b",re.I)
    coord_re=re.compile(r"(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)")
    rows=[]
    for head,body in pat.findall(raw):
        club=" ".join(clean_markup(head))
        lines=clean_markup(body)
        postcode=None;lat=None;lon=None
        for line in lines:
            m=pc_re.search(line)
            if m and not postcode:postcode=m.group(0).upper()
            c=coord_re.search(line)
            if c and lat is None:
                lat=float(c.group(1));lon=float(c.group(2))
        if not club or not postcode:continue

        # Candidate ground heuristic: first substantive line; if it clearly looks
        # like a host club, prefer the next line. Never auto-publish this field.
        useful=[x for x in lines if not pc_re.fullmatch(x) and not coord_re.search(x)
                and not x.lower().startswith(("http://","https://"))]
        ground=useful[0] if useful else "Ground TBC"
        if len(useful)>1 and re.search(r"\b(FC|AFC|CFC|Town|United|Athletic|Rovers|City)$",ground,re.I):
            ground=useful[1]
        rows.append({
            "club":club,"ground_candidate":ground,"postcode":postcode,
            "lat":lat,"lon":lon,"raw_lines":useful[:8],"source":SOURCE_URL
        })
    return rows

text=HTML.read_text(encoding="utf-8")
eligible=extract_js_array(text,"ELIGIBLE")
grounds=extract_js_array(text,"GROUNDS")
existing={norm(g.get("name") or g.get("club")) for g in grounds}
missing=[e.get("name") for e in eligible if e.get("name") and norm(e.get("name")) not in existing]
missing=list(dict.fromkeys(missing))

raw=fetch_source()
gaz=parse_fchd(raw)
gaz_by={norm(x["club"]):x for x in gaz}
gaz_names=list(gaz_by)

queue=[]
for club in missing:
    key=norm(club)
    if key in gaz_by:
        item={**gaz_by[key],"eligible_club":club,"confidence":"HIGH",
              "match_type":"normalised exact","score":1.0}
    else:
        best=difflib.get_close_matches(key,gaz_names,n=1,cutoff=0.84)
        if best:
            score=difflib.SequenceMatcher(None,key,best[0]).ratio()
            item={**gaz_by[best[0]],"eligible_club":club,
                  "confidence":"REVIEW","match_type":"fuzzy name",
                  "score":round(score,3)}
        else:
            item={"eligible_club":club,"confidence":"NO MATCH",
                  "match_type":"none","score":0.0}
    queue.append(item)

rank={"HIGH":0,"REVIEW":1,"NO MATCH":2}
queue.sort(key=lambda x:(rank[x["confidence"]],x["eligible_club"].lower()))
for i,x in enumerate(queue,1):
    x["queue_id"]=i
    x["batch"]=((i-1)//BATCH_SIZE)+1

counts={
    "missing_clubs":len(missing),
    "fchd_records_parsed":len(gaz),
    "high_confidence":sum(x["confidence"]=="HIGH" for x in queue),
    "review":sum(x["confidence"]=="REVIEW" for x in queue),
    "no_match":sum(x["confidence"]=="NO MATCH" for x in queue),
    "batches":(len(queue)+BATCH_SIZE-1)//BATCH_SIZE
}
payload={"checked_at":datetime.now(timezone.utc).isoformat(),
         "source_url":SOURCE_URL,"source_season":"2025-26",
         "mode":"proposal-only","batch_size":BATCH_SIZE,
         "counts":counts,"queue":queue}
JSON_REPORT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

L=["# Tin Foil FA Cup — Ground Discovery Queue","",
   f"Last checked: **{datetime.now(timezone.utc).strftime('%d/%m/%Y, %H:%M:%S UTC')}**","",
   "Source: **Football Club History Database — 2025–26 English Football Gazetteer**","",
   "This is **proposal-only**. No ground record has been added to Clubfinder.","",
   f"- 🔴 Missing canonical clubs submitted: **{counts['missing_clubs']}**",
   f"- 🟢 High-confidence normalised matches: **{counts['high_confidence']}**",
   f"- 🟡 Fuzzy matches requiring review: **{counts['review']}**",
   f"- ⚪ No Gazetteer match: **{counts['no_match']}**",
   f"- 📦 Review batches: **{counts['batches']}** ({BATCH_SIZE} clubs per batch)","",
   "## Batch 1 — first 25 proposals",""]
for x in queue[:BATCH_SIZE]:
    if x["confidence"]=="NO MATCH":
        L.append(f"- **#{x['queue_id']} {x['eligible_club']}** — ⚪ No FCHD match")
    else:
        L.append(
            f"- **#{x['queue_id']} {x['eligible_club']}** — "
            f"{'🟢' if x['confidence']=='HIGH' else '🟡'} {x['confidence']} — "
            f"{x.get('ground_candidate','Ground TBC')} • {x.get('postcode','Postcode TBC')} "
            f"• `{x.get('lat')}, {x.get('lon')}`"
        )

review_items=[x for x in queue if x["confidence"]=="REVIEW"]
L+=["","## 🟡 Fuzzy-name matches requiring explicit review",""]
if review_items:
    for x in review_items[:100]:
        L.append(f"- **{x['eligible_club']}** ↔ FCHD **{x.get('club')}** — score `{x['score']}` — {x.get('postcode','TBC')}")
else:L.append("No fuzzy-name matches.")

L+=["","## Queue rules","",
    "- HIGH means the eligible-club name and FCHD club name match after normalising FC/AFC/CFC and punctuation.",
    "- REVIEW means only a fuzzy name match exists; it must not be applied automatically.",
    "- Groundshares may make the first FCHD address line a host-club name; raw source lines are retained in the JSON report.",
    "- The source is a 2025–26 Gazetteer, so current 2026–27 changes still require human review.",
    "- This Action never edits `clubfinder.html` or `competition.json`."]
REPORT.write_text("\n".join(L)+"\n",encoding="utf-8")

print("GROUND DISCOVERY QUEUE v7.6.4")
for k,v in counts.items():print(k+":",v)
print("First batch:")
for x in queue[:BATCH_SIZE]:
    print(x["queue_id"],x["confidence"],x["eligible_club"],"->",x.get("club"),x.get("postcode"))
print("PROPOSAL ONLY: no Clubfinder or competition data changed.")
