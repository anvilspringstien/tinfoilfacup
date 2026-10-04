#!/usr/bin/env python3
"""Construction Law regression for the pure fixture publication boundary."""
from copy import deepcopy\n\nfrom auto_round_results import merge_event, merge_result\nfrom fixture_publishability_shadow import classify_publishability

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


# Apply only accepted fixture decisions to a disposable canonical candidate.
# Retained/quarantined/no-observation ties remain untouched.
candidate = {
    "source_round": round_name,
    "fixtures": {str(i): dict(fixture) for i, fixture in enumerate(known)},
    "result_history": {},
    "results": {},
    "match_events": [],
}
before_fixtures = deepcopy(candidate["fixtures"])
for row in result["publishable"]:
    merge_result(candidate, row["result"])
for row in result["unresolved"]:
    # The pure boundary intentionally retains unresolved fixtures; record only
    # the event semantics when they are available from the original observation.
    fixture = next(f for f in known if f["home"] == row["home"] and f["away"] == row["away"])
    observation = next(x["observation"] for x in observations if x["fixture"] is fixture)
    merge_event(candidate, {
        "round": round_name, "home": fixture["home"], "away": fixture["away"],
        "date": observation["date"], "status": observation["status"],
        "decision": observation.get("decision", ""),
    })

require(candidate["fixtures"] == before_fixtures,
        "candidate merge must not rewrite the canonical draw")
require(candidate["results"]["Pigeon Vale"]["winner"] == "Pigeon Vale",
        "accepted Pigeon Vale result must enter disposable canonical state")
require(candidate["results"]["Anvil Rovers"]["winner"] == "Pigeon Vale",
        "both participant histories must derive the same custodian")
require(not any("Fossil Town" in key for key in candidate["results"]),
        "quarantined tie must not mutate canonical results")
require(not any("Unknown Albion" in key for key in candidate["results"]),
        "no-observation tie must not mutate canonical results")
require(len(candidate["match_events"]) == 1
        and candidate["match_events"][0]["status"] == "POSTPONED",
        "unresolved postponement may be retained as an event without inventing a result")

print("Disposable canonical candidate merge: PASS")
print("Fixture-local quarantine retained unchanged: PASS")
