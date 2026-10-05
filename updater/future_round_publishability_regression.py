#!/usr/bin/env python3
"""Construction Law regression for the pure fixture publication boundary."""
from fixture_publishability_shadow import classify_publishability

def require(value, message):
    if not value:
        raise SystemExit("FUTURE ROUND PUBLISHABILITY: FAIL - " + message)

round_name = "Fourth Round Qualifying"
known = [
    {"round": round_name, "home": "Pigeon Vale", "away": "Anvil Rovers", "date": "2099-10-10"},
    {"round": round_name, "home": "Tin Foil Athletic", "away": "Mission Control", "date": "2099-10-10"},
    {"round": round_name, "home": "Fossil Town", "away": "Deterministic United", "date": "2099-10-10"},
    {"round": round_name, "home": "Unknown Albion", "away": "Future Wednesday", "date": "2099-10-10"},
]

def item(index, **observation):
    fixture = known[index]
    base = {"home": fixture["home"], "away": fixture["away"], "home_score": None,
            "away_score": None, "winner": "", "status": "", "decision": "",
            "date": fixture["date"], "source_url": "synthetic-future-round"}
    base.update(observation)
    return {"fixture": fixture, "observation": base}

observations = [
    item(0, home_score=3, away_score=1, status="FT"),
    item(1, status="POSTPONED"),
    item(2, home_score=1, away_score=1, status="FT", winner="Pigeon Vale", decision="penalties"),
]
result = classify_publishability(round_name, known, observations, [])
require(len(result["publishable"]) == 1, "ordinary unfamiliar result should be publishable")
require(result["publishable"][0]["result"]["winner"] == "Pigeon Vale", "winner must derive from score")
require(len(result["unresolved"]) == 1 and result["unresolved"][0]["status"] == "POSTPONED",
        "postponed unfamiliar tie must remain unresolved")
require(len(result["quarantined"]) == 1, "contradictory unfamiliar winner must quarantine")
require(len(result["no_observation"]) == 1 and result["no_observation"][0]["home"] == "Unknown Albion",
        "unseen unfamiliar tie must remain explicitly unobserved")
print("FUTURE ROUND PUBLISHABILITY: PASS")
