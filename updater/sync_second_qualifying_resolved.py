#!/usr/bin/env python3
"""Guardedly refresh the active Second Qualifying draw.

The official draw always contains EXPECTED_TOTAL ties. Some slots can be
conditional while an earlier replay is unresolved. Those conditional slots are
temporary placeholders: when the source later publishes exactly one fixture
consistent with the placeholder, the definite fixture replaces it
automatically. Ambiguous, missing or structurally inconsistent transitions
still fail closed.
"""
import json,re,urllib.request
from datetime import datetime,timezone
from html import unescape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"competition.json"
REPORT=ROOT/"updater"/"second-qualifying-sync-report.json"
URL="https://www.footballwebpages.co.uk/fa-cup/fixtures-results"
ROUND="Second Round Qualifying"
DATE="2026-09-19"
EXPECTED_TOTAL=80
UA="Mozilla/5.0 TinFoilFACupCompetitionHealth/7.9.25"

def report(stage,**details):
    REPORT.write_text(
        json.dumps(
            {"checked_at":datetime.now(timezone.utc).isoformat(),"stage":stage,**details},
            indent=2,ensure_ascii=False
        )+"\n",
        encoding="utf-8"
    )

def fail(stage,message,**details):
    report(stage,status="FAIL",message=message,**details)
    raise SystemExit(message)

def fetch(url):
    req=urllib.request.Request(
        url,
        headers={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml"}
    )
    return urllib.request.urlopen(req,timeout=30).read().decode("utf-8","replace")

def clean(x):
    return " ".join(unescape(re.sub(r"<[^>]+>"," ",x)).replace("\xa0"," ").split())

def cells(row):
    return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>",row,re.I|re.S)]

def norm(s):
    s=(s or "").lower().replace("&"," and ")
    s=re.sub(r"\b(fc|afc|cfc)\b"," ",s)
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

LEGACY_NAME_ALIASES={
    norm("Burgess H"):norm("Burgess Hill Town"),
    norm("Burgess Hill"):norm("Burgess Hill Town")
}

def canonical_norm(s):
    n=norm(s)
    return LEGACY_NAME_ALIASES.get(n,n)

def compatible(a,b):
    a,b=canonical_norm(a),canonical_norm(b)
    return bool(a and b and (a==b or a.startswith(b+" ") or b.startswith(a+" ")))

def conditional_alternatives(side):
    return [x.strip() for x in re.split(r"\s+or\s+",str(side or ""),flags=re.I) if x.strip()]

def is_conditional_side(side):
    return len(conditional_alternatives(side))>1

def is_conditional_fixture(fixture):
    return is_conditional_side(fixture.get("home","")) or is_conditional_side(fixture.get("away",""))

def parse_time(s):
    s=(s or "").strip().lower().replace(" ","")
    m=re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)",s)
    if m:
        h=int(m.group(1))%12+(12 if m.group(3)=="pm" else 0)
        return f"{h:02d}:{int(m.group(2) or 0):02d}"
    if re.fullmatch(r"\d{1,2}:\d{2}",s):
        h,mm=map(int,s.split(":"))
        return f"{h:02d}:{mm:02d}"
    return "15:00"

def parse(page):
    """Return definite source fixtures only; conditional source rows are not resolved."""
    fixtures=[]
    for row in re.findall(r"<tr\b[^>]*>.*?</tr>",page,re.I|re.S):
        c=[x for x in cells(row) if x]
        try:
            vi=next(i for i,x in enumerate(c) if x.lower()=="v")
        except StopIteration:
            continue
        if vi<1 or vi+1>=len(c):
            continue
        home=c[vi-1].strip()
        away=c[vi+1].strip()
        time=c[vi-2].strip() if vi>=2 else "3pm"
        if not home or not away:
            continue
        if is_conditional_side(home) or is_conditional_side(away):
            continue
        fixtures.append({
            "round":ROUND,
            "home":home,
            "away":away,
            "date":DATE,
            "kickoff":parse_time(time),
            "source_url":URL
        })
    unique={}
    for f in fixtures:
        unique[tuple(sorted((norm(f["home"]),norm(f["away"]))))]=f
    return list(unique.values())

def aliases(name):
    suffix=re.compile(r"\s+(FC|AFC|CFC)$",re.I)
    out={name,suffix.sub("",name)}
    if not suffix.search(name):
        out|={name+" FC",name+" AFC"}
    return {x for x in out if x}

def fmap(fixtures):
    out={}
    for f in fixtures:
        for club in aliases(f["home"])|aliases(f["away"]):
            out[club]=f
    return out

def unique_fixtures(src):
    vals=src.values() if isinstance(src,dict) else (src or [])
    out={}
    for f in vals:
        if not isinstance(f,dict) or not f.get("home") or not f.get("away"):
            continue
        key=(norm(f.get("home")),norm(f.get("away")),f.get("date","") or "")
        out[key]=dict(f)
    return list(out.values())

def side_matches(value,side):
    options=conditional_alternatives(side)
    return any(compatible(value,option) for option in options)

def fixture_matches_slot(fixture,slot):
    """Does one definite source fixture satisfy the alternatives in a saved slot?"""
    return (
        not is_conditional_fixture(fixture)
        and side_matches(fixture.get("home",""),slot.get("home",""))
        and side_matches(fixture.get("away",""),slot.get("away",""))
    )

def fixture_label(fixture):
    return f'{fixture.get("home","?")} v {fixture.get("away","?")}'

def reconcile_conditionals(resolved,current):
    """Merge definite source fixtures with still-unresolved saved placeholders.

    A saved conditional slot has three valid states:
      * zero source matches -> retain the placeholder;
      * one source match -> the source fixture replaces it automatically;
      * more than one source match -> ambiguous, so fail closed.

    Returns (final, retained, transitions, ambiguities).
    """
    conditionals=[dict(f) for f in current if is_conditional_fixture(f)]
    retained=[]
    transitions=[]
    ambiguities=[]
    source_claims={}

    for slot in conditionals:
        matches=[f for f in resolved if fixture_matches_slot(f,slot)]
        if len(matches)>1:
            ambiguities.append({
                "slot":fixture_label(slot),
                "matches":[fixture_label(f) for f in matches]
            })
            continue
        if len(matches)==1:
            match=matches[0]
            key=tuple(sorted((norm(match["home"]),norm(match["away"]))))
            if key in source_claims:
                ambiguities.append({
                    "slot":fixture_label(slot),
                    "matches":[fixture_label(match)],
                    "also_claimed_by":source_claims[key]
                })
                continue
            source_claims[key]=fixture_label(slot)
            transitions.append({
                "from":fixture_label(slot),
                "to":fixture_label(match)
            })
            continue

        keep=dict(slot)
        keep.update({"round":ROUND,"date":DATE})
        retained.append(keep)

    return list(resolved)+retained,retained,transitions,ambiguities

def has_fixture(fixtures,a,b):
    target=tuple(sorted((norm(a),norm(b))))
    return any(tuple(sorted((norm(f["home"]),norm(f["away"]))))==target for f in fixtures)

def main():
    data=json.loads(DATA.read_text(encoding="utf-8"))
    resolved=parse(fetch(URL))
    current=unique_fixtures(data.get("fixtures") or {})
    final,retained,transitions,ambiguities=reconcile_conditionals(resolved,current)

    if ambiguities:
        fail(
            "conditional_resolution",
            "SECOND QUALIFYING RESOLVED SYNC: ABORT - conditional slot resolved ambiguously",
            parsed_count=len(resolved),
            current_unique=len(current),
            ambiguities=ambiguities
        )

    required=[
        ("Hampton & Richmond Borough","Crowborough Athletic"),
        ("Dulwich Hamlet","Welling United"),
        ("Thame United","Exmouth Town"),
        ("Needham Market","Braintree Town"),
        ("Hemel Hempstead Town","Wingate & Finchley")
    ]
    missing=[f"{a} v {b}" for a,b in required if not has_fixture(final,a,b)]
    if missing:
        fail(
            "canaries",
            "SECOND QUALIFYING RESOLVED SYNC: ABORT - required fixtures missing",
            missing=missing
        )

    if len(final)!=EXPECTED_TOTAL:
        fail(
            "final_count",
            f"SECOND QUALIFYING RESOLVED SYNC: ABORT - expected {EXPECTED_TOTAL} total ties after reconciling conditional slots, found {len(final)}",
            parsed_resolved=len(resolved),
            retained_conditional_slots=len(retained),
            current_conditional_slots=sum(1 for f in current if is_conditional_fixture(f)),
            transitions=transitions
        )

    data["fixtures"]=fmap(final)
    data["source_round"]=ROUND
    data.setdefault("round_dates",{})[ROUND]=DATE
    data["updated_at"]=datetime.now(timezone.utc).isoformat()
    data["second_qualifying_sync"]={
        "source":"Football Web Pages + retained unresolved conditional slots" if retained else "Football Web Pages",
        "source_url":URL,
        "synced_at":data["updated_at"],
        "resolved_fixtures":len(resolved),
        "pending_replay_slots":len(retained),
        "total_fixtures":len(final),
        "pending":" | ".join(fixture_label(f) for f in retained),
        "resolved_conditional_slots":transitions
    }
    DATA.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report(
        "complete",
        status="PASS",
        resolved_ties=len(resolved),
        pending_slots=len(retained),
        total_ties=len(final),
        resolved_conditional_slots=transitions,
        pending_fixtures=[fixture_label(f) for f in retained]
    )
    print("SECOND QUALIFYING RESOLVED SYNC: PASS")
    print("Resolved ties:",len(resolved))
    print("Pending conditional slots:",len(retained))
    print("Conditional slots resolved this run:",len(transitions))
    for transition in transitions:
        print("RESOLVED:",transition["from"],"->",transition["to"])
    print("Total ties:",len(final))

if __name__=="__main__":
    main()
