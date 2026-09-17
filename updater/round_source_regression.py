#!/usr/bin/env python3
"""Synthetic source-parser regression for the round-agnostic importer."""
from auto_round_results import parse_fwp_observations


def require(value, message):
    if not value:
        raise SystemExit("ROUND SOURCE REGRESSION: FAIL - " + message)


known = [{"round": "Second Round Qualifying", "home": "Alpha Town", "away": "Beta United", "date": "2026-09-19"}]

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

print("ROUND SOURCE REGRESSION: PASS")
print("Penalty winner note: PASS")
print("P-P postponed event: PASS")
print("FT (AET) preservation: PASS")
print("Unrelated rows ignored: PASS")
