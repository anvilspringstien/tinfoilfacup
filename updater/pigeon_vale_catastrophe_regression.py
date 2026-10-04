#!/usr/bin/env python3
"""Synthetic catastrophic disposition drill: history survives while competitive authority changes."""
from copy import deepcopy

from auto_round_results import merge_disposition, merge_result, history_rows
from round_state_engine import classify_observation
from fixture_publishability_shadow import classify_publishability
from refresh_beta_embedded_snapshot import refresh, BETA
import json


def require(value, message):
    if not value:
        raise SystemExit("PIGEON VALE CATASTROPHE: FAIL - " + message)


fixture = {
    "round": "Fourth Round Qualifying",
    "home": "Pigeon Vale",
    "away": "Deterministic United",
    "date": "2099-10-10",
}
played = {
    "home": "Pigeon Vale",
    "away": "Deterministic United",
    "date": "2099-10-10",
    "home_score": 1,
    "away_score": 1,
    "status": "FT(AET)",
    "winner": "Pigeon Vale",
    "decision": "penalties",
    "venue": {
        "ground": "The Great Deterministic Boundary",
        "postcode": "ZZ1 1ZZ",
        "verification": "verified",
    },
    "source_url": "synthetic-authoritative-result",
}
data = {"result_history": {}, "results": {}, "match_events": []}

terminal = classify_observation(fixture, played, [])["result"]
require(terminal["winner"] == "Pigeon Vale", "initial penalty winner was not terminal")
merge_result(data, terminal)

# A contradictory later score is NOT enough to infer a replay.
try:
    classify_observation(
        fixture,
        {
            "home": "Deterministic United", "away": "Pigeon Vale",
            "date": "2099-10-14", "home_score": 1, "away_score": 2,
            "status": "FT", "winner": "Pigeon Vale", "source_url": "synthetic",
        },
        history_rows(data),
    )
    raise SystemExit("PIGEON VALE CATASTROPHE: FAIL - replay inferred without explicit disposition")
except ValueError:
    pass

# Governing-body ruling: the match happened, but its competitive authority is withdrawn.
void_observation = {
    "home": "Pigeon Vale",
    "away": "Deterministic United",
    "date": "2099-10-10",
    "status": "VOID",
    "decision": "voided-replay-ordered",
    "source_url": "synthetic-governing-body-ruling",
}
disposition = classify_observation(fixture, void_observation, history_rows(data))
require(disposition["kind"] == "disposition", "explicit void ruling was not classified as a disposition")
voided = disposition["result"]
require(voided["winner"] == "", "voided match retained competitive winner")
require(voided["home_score"] == 1 and voided["away_score"] == 1, "played score was erased")
require(voided["venue"]["postcode"] == "ZZ1 1ZZ", "played venue/postcode was erased")
merge_disposition(data, disposition["supersedes"], voided)

# The ordered replay reverses orientation, moves ground, and resolves on penalties.
replay_observation = {
    "home": "Deterministic United",
    "away": "Pigeon Vale",
    "date": "2099-10-14",
    "home_score": 2,
    "away_score": 2,
    "status": "FT(AET)",
    "winner": "Deterministic United",
    "decision": "penalties",
    "venue": {
        "ground": "Tomorrow Stadium",
        "postcode": "YY1 1YY",
        "verification": "verified",
    },
    "source_url": "synthetic-authoritative-replay",
}
replay = classify_observation(fixture, replay_observation, history_rows(data))["result"]
require(replay["round"] == "Fourth Round Qualifying Replay", "ordered match was not classified as replay")
require(replay["winner"] == "Deterministic United", "replay penalty winner did not become terminal truth")
merge_result(data, replay)

history = history_rows(data)
require(any(r.get("status") == "VOID" and r.get("venue", {}).get("postcode") == "ZZ1 1ZZ" for r in history),
        "voided played match/history did not survive")
require(any(r.get("round") == "Fourth Round Qualifying Replay" and r.get("venue", {}).get("postcode") == "YY1 1YY" for r in history),
        "replay history/new venue did not survive")
require(data["results"]["Pigeon Vale"]["winner"] == "Deterministic United",
        "latest canonical authority did not advance Deterministic United")

# Final Boss: prove the abnormal state crosses the independent publication
# decision and the real BETA fallback boundary as one disposable transaction.
probe = {
    "fixture": fixture,
    "observation": {
        "home": "Pigeon Vale", "away": "Deterministic United",
        "date": "2099-10-10", "status": "VOID",
        "decision": "voided-replay-ordered", "source_url": "synthetic-final-boss",
    },
}
pre_void = {"result_history": {}, "results": {}, "match_events": []}
merge_result(pre_void, terminal)
publication = classify_publishability(
    fixture["round"], [fixture], [probe], history_rows(pre_void)
)
require(len(publication["publishable"]) == 1, "VOID disposition failed publication boundary")
require(publication["publishable"][0]["decision"] == "publishable-disposition",
        "VOID disposition lost semantic publication type")

data.update({
    "schema_version": 1,
    "updated_at": "2099-10-14T22:17:00Z",
    "source_round": fixture["round"],
    "fixtures": {
        "future-next": {
            "round": "First Round Proper", "date": "2099-11-07",
            "home": "Future Wednesday", "away": "Deterministic United",
            "venue": {"ground": "Far Side", "postcode": "XX1 1XX"},
        }
    },
})
fallback = json.loads(refresh(BETA.read_text(encoding="utf-8"), data))
require(fallback == data, "BETA fallback changed continuous Catastrophe state")
require(fallback["results"]["Pigeon Vale"]["winner"] == "Deterministic United",
        "fallback resurrected obsolete winner")
require(fallback["fixtures"]["future-next"]["venue"]["postcode"] == "XX1 1XX",
        "fallback lost unfamiliar next fixture")

print("PIGEON VALE FINAL BOSS DATA PIPELINE: PASS")
print("Publication decision -> disposition -> replay -> next fixture -> fallback: PASS")

print("PIGEON VALE CATASTROPHE — CANONICAL DISPOSITION: PASS")
print("Initial AET/penalty result recorded: PASS")
print("Contradictory result without ruling fails closed: PASS")
print("Explicit VOID/replay order withdraws winner but preserves played score/venue: PASS")
print("Reversed unfamiliar-venue replay ancestry: PASS")
print("New penalty winner becomes canonical terminal truth: PASS")
