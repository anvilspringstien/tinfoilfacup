#!/usr/bin/env python3
"""Synthetic source-parser regression for the round-agnostic importer."""
from auto_round_results import dedupe_observations, fwp_round_label, fwp_round_url, parse_fwp_observations


def require(value, message):
    if not value:
        raise SystemExit("ROUND SOURCE REGRESSION: FAIL - " + message)


known = [{"round": "Second Round Qualifying", "home": "Alpha Town", "away": "Beta United", "date": "2026-09-19"}]

require(
    fwp_round_url("Second Round Qualifying").endswith("/second-qualifying-round"),
    "active-round source must be pinned to the Second Qualifying Round archive",
)
require(
    fwp_round_label("Second Round Qualifying") == "Second Qualifying Round",
    "FA/FWP qualifying-round naming must be normalized",
)

penalty_html = """
<h3>Tuesday 22nd September 2026</h3>
<table>
<tr><td>FT</td><td>Beta United</td><td>1</td><td>1</td><td>Alpha Town</td></tr>
<tr><td>Beta United win 5-4 on penalties</td></tr>
</table>
"""
rows = parse_fwp_observations(penalty_html, known, "synthetic")
require(len(rows) == 1, "penalty row should map to canonical pair")
obs = rows[0]["observation"]
require(obs["winner"] == "Beta United" and obs["decision"] == "penalties", "penalty winner note should be captured")
require(obs["date"] == "2026-09-22", "date heading should be attached to result")

postponed_html = """
<h3>Saturday 19th September 2026</h3>
<table><tr><td>3pm</td><td>Alpha Town</td><td>P</td><td>P</td><td>Beta United</td></tr></table>
"""
rows = parse_fwp_observations(postponed_html, known, "synthetic")
require(len(rows) == 1 and rows[0]["observation"]["status"] == "POSTPONED", "P-P should become a postponed event")

aet_html = """
<h3>Tuesday 22nd September 2026</h3>
<table><tr><td>FT (AET)</td><td>Beta United</td><td>2</td><td>3</td><td>Alpha Town</td></tr></table>
"""
rows = parse_fwp_observations(aet_html, known, "synthetic")
require(len(rows) == 1 and rows[0]["observation"]["status"] == "FT (AET)", "AET status should survive parsing")

unrelated_html = "<table><tr><td>FT</td><td>Other FC</td><td>2</td><td>0</td><td>Elsewhere Town</td></tr></table>"
require(not parse_fwp_observations(unrelated_html, known, "synthetic"), "unrelated round rows must be ignored")

cross_source = [
    {
        "fixture": known[0],
        "observation": {
            "home": "Alpha Town",
            "away": "Beta United",
            "home_score": 2,
            "away_score": 1,
            "winner": "",
            "status": "FT",
            "decision": "",
            "date": "2026-09-18",
            "source_url": "synthetic-fixtures",
        },
    },
    {
        "fixture": known[0],
        "observation": {
            "home": "Alpha Town",
            "away": "Beta United",
            "home_score": 2,
            "away_score": 1,
            "winner": "",
            "status": "FT",
            "decision": "",
            "date": "2026-09-19",
            "source_url": "synthetic-live",
        },
    },
]
collapsed = dedupe_observations(cross_source)
require(len(collapsed) == 1, "adjacent-date copies from different sources should collapse")
require(collapsed[0]["observation"]["date"] == "2026-09-18", "cross-source collapse should retain the earlier match date")

same_source = [dict(item) for item in cross_source]
same_source[1] = {
    "fixture": known[0],
    "observation": dict(cross_source[1]["observation"], source_url="synthetic-fixtures"),
}
require(len(dedupe_observations(same_source)) == 2, "same-source adjacent dates must remain distinct for replay chronology")

different_score = [
    cross_source[0],
    {
        "fixture": known[0],
        "observation": dict(cross_source[1]["observation"], home_score=3),
    },
]
require(len(dedupe_observations(different_score)) == 2, "different cross-source scorelines must never collapse")

print("ROUND SOURCE REGRESSION: PASS")
print("Penalty winner note: PASS")
print("P-P postponed event: PASS")
print("FT (AET) preservation: PASS")
print("Unrelated rows ignored: PASS")
print("Cross-source adjacent-date dedupe: PASS")
print("Same-source replay chronology preserved: PASS")
print("Different scorelines preserved: PASS")
print("Active-round FWP archive pinning: PASS")
