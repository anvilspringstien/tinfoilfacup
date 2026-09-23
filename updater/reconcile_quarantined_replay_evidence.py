#!/usr/bin/env python3
"""Fail-closed independent evidence reconciliation for quarantined replay results.

Evidence is supplied as source-attributed JSON, never inferred from FWP's
inconsistent record. This module cannot write competition.json.
"""
import json
import sys
from pathlib import Path

TRUSTED = {"thefa.com": "fa", "wimbornetownfc.co.uk": "club", "wsmafc.co.uk": "club", "southwestsportsnews.com": "regional_news"}
def reconcile(blocked, evidence):
    if "penalty decision with non-level source score" not in blocked.get("reason", ""):
        raise ValueError("unsupported quarantine reason")
    target = {blocked.get("home", "").casefold(), blocked.get("away", "").casefold()}
    accepted = []
    for item in evidence:
        host = item.get("domain", "").lower().removeprefix("www.")
        if host not in TRUSTED or not any(item.get("url", "").startswith(prefix)
                                         for prefix in ("https://" + host + "/", "https://www." + host + "/",
                                                        "https://mail." + host + "/")):
            continue
        if {item.get("home", "").casefold(), item.get("away", "").casefold()} != target:
            continue
        if item.get("date") != blocked.get("date") or item.get("decision") != "penalties":
            continue
        if not isinstance(item.get("home_score"), int) or item["home_score"] != item.get("away_score"):
            continue
        if item.get("winner", "").casefold() not in target:
            continue
        if not isinstance(item.get("home_pens"), int) or not isinstance(item.get("away_pens"), int):
            continue
        if item["home_pens"] == item["away_pens"]:
            continue
        expected = item["home"] if item["home_pens"] > item["away_pens"] else item["away"]
        if item["winner"].casefold() != expected.casefold():
            continue
        accepted.append(item)
    # Two distinct independent publishers must agree on all match facts.
    for first in accepted:
        for second in accepted:
            if first["domain"] == second["domain"]:
                continue
            keys = ("home", "away", "date", "home_score", "away_score",
                    "home_pens", "away_pens", "winner", "decision")
            if all(first[k] == second[k] for k in keys):
                return {"status": "independently_verified", "result": {k:first[k] for k in keys},
                        "sources": [first["url"], second["url"]], "production_mutation": False}
    return {"status": "quarantined", "reason": "two agreeing independent authoritative sources required",
            "accepted_sources": [x["url"] for x in accepted], "production_mutation": False}

if __name__ == "__main__":
    blocked = json.loads(Path(sys.argv[1]).read_text())
    evidence = json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(reconcile(blocked, evidence), indent=2))
