#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
REPLAY_ROUND = "First Round Qualifying Replay"


def norm(s):
    s = str(s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def replay_rows(data):
    out = []
    seen = set()
    for rows in (data.get("result_history") or {}).values():
        if not isinstance(rows, list):
            continue
        for r in rows:
            if not isinstance(r, dict) or r.get("round") != REPLAY_ROUND:
                continue
            key = (norm(r.get("home")), norm(r.get("away")), r.get("date"))
            if key not in seen:
                seen.add(key)
                out.append(r)
    return out


def find_replay(rows, home, away):
    return next((r for r in rows if norm(r.get("home")) == norm(home) and norm(r.get("away")) == norm(away)), None)


def find_fixture(rows, home, away):
    return next((f for f in rows if norm(f.get("home")) == norm(home) and norm(f.get("away")) == norm(away)), None)


data = json.loads(DATA.read_text(encoding="utf-8"))
replays = replay_rows(data)

# Replay completeness is guarded separately by replay_completion_guard.py. This
# regression deliberately does not freeze a temporary replay count: postponed
# replays are allowed to move from unresolved to resolved without making venue
# enrichment look broken. Keep a floor so historic replay data cannot silently
# disappear, and verify representative enriched replay anchors explicitly.
if len(replays) < 31:
    raise SystemExit(f"FAIL: First Qualifying replay coverage regressed below 31; found {len(replays)}")

replay_anchors = (
    ("Exmouth Town", "Banbury United"),
    ("Welling United", "Faversham Town"),
    ("AFC Whyteleafe", "Crowborough Athletic"),
    ("Jersey Bulls", "Burgess Hill Town"),
)
for home, away in replay_anchors:
    r = find_replay(replays, home, away)
    if not r or r.get("kickoff") != "19:45":
        raise SystemExit(f"FAIL: {home} v {away} kick-off expected 19:45, got {None if not r else r.get('kickoff')}")
    if not r.get("kickoff_source_url"):
        raise SystemExit(f"FAIL: {home} v {away} has no kick-off source URL")

fixtures = fixture_values(data.get("fixtures") or {})
venue_anchors = (
    ("Hampton & Richmond Borough", "Crowborough Athletic", "TW12 2BX"),
    ("Frome Town", "Plymouth Parkway", "BA11 2EH"),
    ("Dulwich Hamlet", "Welling United", "SE22 8BD"),
)
for home, away, postcode in venue_anchors:
    f = find_fixture(fixtures, home, away)
    if not f:
        raise SystemExit(f"FAIL: active fixture not found: {home} v {away}")
    venue = f.get("venue") or {}
    got = str(venue.get("postcode") or "").upper().replace("  ", " ").strip()
    if got != postcode:
        raise SystemExit(f"FAIL: {home} v {away} venue expected {postcode}, got {got or 'TBC'}")

print("KICK-OFF + VENUE REGRESSION: PASS")
print("First Qualifying replays preserved:", len(replays))
print(f"Verified 19:45 replay anchors: {len(replay_anchors)}/{len(replay_anchors)}")
print(f"Verified Second Qualifying venue anchors: {len(venue_anchors)}/{len(venue_anchors)}")
