#!/usr/bin/env python3
"""Apply *reviewed unverified* new entrant home-ground postcodes to BETA only.

Requires the canonical Second Round fixture list, official-source evidence and
exact AFC-aware identity. No fixture, coordinate, mileage, verified badge or
public production source is ever changed. Strictly idempotent.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from updater.audit_active_custodian_locations import identity_key, display_key, next_round_entrants

ROOT=Path(__file__).resolve().parents[1]
BETA=ROOT / "beta/clubfinder-beta.html"
EVIDENCE=ROOT / "updater/entrant-home-ground-evidence-2026.json"
COMPETITION=ROOT / "competition.json"
DECODER=json.JSONDecoder()

def literal(html,name):
    match=re.search(r"\\b(?:const|let|var)\\s+"+re.escape(name)+r"\\s*=\\s*",html)
    if not match: raise ValueError("Missing original "+name+" data")
    data,size=DECODER.raw_decode(html[match.end():])
    if not isinstance(data,list): raise ValueError("Expected location array: "+name)
    return match.end(),match.end()+size,data

def ground_record(row):
    url=row.get("official_home_ground_source","")
    parsed=urlparse(url)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Missing acceptable official evidence URL")
    if row.get("source_review")!="official-ground-and-postcode-confirmed" or row.get("review_status") not in ("awaiting-coordinates-and-human-promotion","awaiting-human-promotion"):
        raise ValueError("Cannot promote unreconciled ground evidence")
    if not row.get("ground") or not re.fullmatch(r"[A-Z]{1,2}\\d[A-Z\\d]? \\d[A-Z]{2}",row.get("postcode","")):
        raise ValueError("Invalid ground name or postcode")
    return {"name":row["official_identity"],"ground":row["ground"],
       "postcode":row["postcode"],"verification":"unverified",
       "source":url,
       "ground_source":"Official club source — pending independent coordinate verification",
       "preview_evidence_only":True}

def transform(html,evidence,competition):
    if evidence.get("season")!="2026-27" or evidence.get("safety",{}).get("automated_ground_promotion") is not False or evidence.get("safety",{}).get("verified_location_badge_authorized") is not False or evidence.get("safety",{}).get("coordinates_required_before_location_promotion") is not True:
        raise ValueError("Ground verification and non-promotion gates changed")
    if competition.get("season")!=evidence["season"]:
        raise ValueError("Canonical competition season mismatch")
    entrants=next_round_entrants(competition)
    if len(entrants)!=40:
        raise ValueError("Second Round participant count changed: fail closed")
    start,end,grounds=literal(html,"GROUNDS")
    _,_,law=literal(html,"LAW2_ORIGIN_LOCATIONS")
    known={}
    for rec in grounds+law:
        known.setdefault(display_key(rec.get("name")),[]).append(rec)
    if len(evidence.get("clubs",[]))!=37: raise ValueError("Evidence inventory changed")
    by_id={}
    for item in evidence["clubs"]:
        key=identity_key(item.get("official_identity"))
        if not key or key in by_id: raise ValueError("Missing/duplicate reviewed identity")
        by_id[key]=item
    blocked={identity_key(x.get("official_identity")) for x in evidence.get("unresolved_conflicts",[])}
    created=[];existing=[];already=[]
    for key,club in sorted(entrants.items()):
        possible=known.get(display_key(club),[])
        exact=[r for r in possible if identity_key(r.get("name"))==key]
        if len(exact)>1: raise ValueError("Ambiguous existing home-ground identity: "+club)
        if len(exact)==1:
            rec=exact[0]
            if rec.get("preview_evidence_only"):
                reviewed=ground_record(by_id.get(key,{}))
                if any(rec.get(k)!=v for k,v in reviewed.items()) or any(k in rec for k in ("lat","lon","latitude","longitude","distance")):
                    raise ValueError("Reviewed unverified ground drift: "+club)
                already.append(club)
            existing.append(club)
            continue
        if possible: raise ValueError("Unsafe loose-key collision: "+club)
        row=by_id.get(key)
        if not row or key in blocked: raise ValueError("Missing or blocked official home-ground evidence: "+club)
        rec=ground_record(row)
        created.append(rec)
        known.setdefault(display_key(club),[]).append(rec)
    if len(created)+len(already)!=31 or len(existing)+len(created)!=40:
        raise ValueError("Expected 31 reviewed pending and 9 existing entrant grounds")
    changed=html[:start]+json.dumps(grounds+created,ensure_ascii=False,separators=(",",":"))+html[end:] if created else html
    start_marker="function findGround(c){"
    end_marker="}function verification(c,g){"
    if changed.count(start_marker)!=1 or changed.count(end_marker)!=1:
        raise ValueError("Clubfinder ground lookup structure drift")
    before,tail=changed.split(start_marker,1);lookup,after=tail.split(end_marker,1)
    guard=r"  const previewAfcBoundary=(requested,record)=>/^\\s*afc\\b/i.test(requested||'')===/^\\s*afc\\b/i.test(record||'');" + "\\n"
    if "previewAfcBoundary" not in lookup:
        if lookup.count("if(g)return g;")!=1 or lookup.count("if(s)return s;")!=1:
            raise ValueError("Unsafe Clubfinder identity lookup drift")
        lookup=guard+lookup.replace("if(g)return g;","if(g&&previewAfcBoundary(c.name,g.name))return g;").replace("if(s)return s;","if(s&&previewAfcBoundary(c.name,s.name))return s;")
        changed=before+start_marker+lookup+end_marker+after
    elif not ("if(g&&previewAfcBoundary(c.name,g.name))return g;" in lookup and "if(s&&previewAfcBoundary(c.name,s.name))return s;" in lookup):
        raise ValueError("Partial AFC identity safeguard")
    return changed,{"new_pending":len(created),"already_pending":len(already),"other_existing":len(existing)-len(already),
     "approved_second_round":len(entrants),"automatic_verified":False,"mileage_changed":False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--apply",action="store_true")
    group.add_argument("--check",action="store_true")
    opts=parser.parse_args()
    original=BETA.read_text(encoding="utf-8")
    transformed,report=transform(original,json.loads(EVIDENCE.read_text(encoding="utf-8")),
       json.loads(COMPETITION.read_text(encoding="utf-8")))
    if opts.check and original!=transformed:
        raise SystemExit("BETA pending entrant ground source needs generated refresh")
    if opts.apply and original!=transformed:
        BETA.write_text(transformed,encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
