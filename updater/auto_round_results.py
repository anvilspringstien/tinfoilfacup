#!/usr/bin/env python3
"""Round-agnostic guarded FA Cup result/disposition importer.

The active draw in competition.json is the canonical set of ties. Football Web
Pages supplies structural observations for that set; the shared round-state
engine decides whether each observation is an original result, a replay, an
unresolved postponement/abandonment, or an explicit award/walkover.

Crucially, reversed home/away orientation is never sufficient evidence of a
replay. Replay ancestry exists only after an earlier completed draw in a replay-
eligible qualifying round.
"""
import argparse
import html as H
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from round_state_engine import (
    base_round,
    classify_observation,
    compatible,
    norm,
    pair_key,
    same_result,
    unique_history,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
REPORT = ROOT / "updater" / "results-pilot-report.json"
FWP_FIXTURES_URL = "https://www.footballwebpages.co.uk/fa-cup/fixtures-results"
FWP_LIVE_URL = "https://www.footballwebpages.co.uk/fa-cup"
UA = "Mozilla/5.0 TinFoilFACupRoundState/1.0"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def clean(value):
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", value)).replace("\xa0", " ").split())


def textify(value):
    value = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", value, flags=re.I | re.S)
    return "\n".join(line.strip() for line in H.unescape(re.sub(r"<[^>]+>", "\n", value)).splitlines() if line.strip())


def cells(row):
    return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)]


def date_from_text(text):
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(20\d{2})", text or "")
    if not m:
        return ""
    try:
        return datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %B %Y").date().isoformat()
    except ValueError:
        return ""


def score_cell(value):
    m = re.fullmatch(r"(?:\(\d+\)\s*)?(\d+)(?:\s*\(\d+\))?", (value or "").strip())
    return int(m.group(1)) if m else None


def strip_seed(value):
    return re.sub(r"^\(\d+\)\s*|\s*\(\d+\)$", "", (value or "").strip()).strip()


def fixture_values(src):
    values = src.values() if isinstance(src, dict) else (src or [])
    return [f for f in values if isinstance(f, dict) and f.get("home") and f.get("away")]


def active_fixtures(data):
    round_name = base_round(data.get("source_round"))
    seen = set()
    out = []
    for fixture in fixture_values(data.get("fixtures") or {}):
        fr = base_round(fixture.get("round") or round_name)
        if fr and round_name and fr != round_name:
            continue
        key = pair_key(fixture)
        if len(key) != 2 or key in seen:
            continue
        seen.add(key)
        copy = dict(fixture)
        copy["round"] = round_name or fr
        out.append(copy)
    return round_name, out


def history_rows(data):
    rows = []
    for arr in (data.get("result_history") or {}).values():
        if isinstance(arr, list):
            rows.extend(row for row in arr if isinstance(row, dict))
    return unique_history(rows)


def match_fixture(known, home, away):
    matches = [
        f for f in known
        if (
            compatible(f.get("home"), home) and compatible(f.get("away"), away)
        ) or (
            compatible(f.get("home"), away) and compatible(f.get("away"), home)
        )
    ]
    unique = []
    seen = set()
    for fixture in matches:
        key = pair_key(fixture)
        if key not in seen:
            seen.add(key)
            unique.append(fixture)
    if len(unique) > 1:
        raise ValueError(f"source row maps to multiple canonical ties: {home} v {away}")
    return unique[0] if unique else None


def note_winner(note, home, away):
    lower = (note or "").lower()
    if "penalt" not in lower and "walkover" not in lower and "awarded" not in lower:
        return "", ""
    normalized = norm(note)
    for team in (home, away):
        team_n = norm(team)
        if not team_n:
            continue
        escaped = re.escape(team_n)
        named_as_winner = bool(
            re.search(rf"(?:^|\s){escaped}\s+(?:win|wins|won)(?:\s|$)", normalized)
            or re.search(rf"(?:^|\s){escaped}\s+(?:is|are|was|were)?\s*awarded(?:\s|$)", normalized)
            or re.search(rf"(?:awarded|walkover)\s+(?:to\s+)?{escaped}(?:\s|$)", normalized)
        )
        if not named_as_winner:
            continue
        if "penalt" in lower:
            return team, "penalties"
        return team, "walkover"
    return "", ""


def _fixture_from_row_text(known, row_cells):
    matches = []
    for fixture in known:
        home_hit = any(compatible(fixture.get("home"), c) for c in row_cells)
        away_hit = any(compatible(fixture.get("away"), c) for c in row_cells)
        if home_hit and away_hit:
            matches.append(fixture)
    if len(matches) > 1:
        raise ValueError("non-score source row maps to multiple canonical ties")
    return matches[0] if matches else None


def parse_fwp_observations(raw, known, source_url):
    """Parse only observations that map to the current canonical draw."""
    tokens = list(re.finditer(r"<(h[234]|tr)\b[^>]*>.*?</\1>", raw, re.I | re.S))
    observations = []
    current_date = date_from_text(clean(raw))

    for index, token in enumerate(tokens):
        tag = token.group(1).lower()
        block = token.group(0)
        if tag != "tr":
            found = date_from_text(clean(block))
            if found:
                current_date = found
            continue

        c = [x for x in cells(block) if x]
        if not c:
            continue
        row_date = date_from_text(" ".join(c))
        if row_date:
            current_date = row_date

        fi = next((i for i, value in enumerate(c) if value.upper().startswith("FT")), None)
        if fi is not None:
            tail = c[fi + 1 :]
            pair = None
            for i in range(len(tail) - 1):
                hs = score_cell(tail[i])
                ass = score_cell(tail[i + 1])
                if hs is not None and ass is not None and i >= 1 and i + 2 < len(tail):
                    pair = (i, hs, ass)
                    break
            if not pair:
                continue
            i, hs, ass = pair
            home = strip_seed(" ".join(tail[:i]).strip())
            away = strip_seed(tail[i + 2].strip())
            fixture = match_fixture(known, home, away)
            if not fixture:
                continue
            note = ""
            if index + 1 < len(tokens) and tokens[index + 1].group(1).lower() == "tr":
                note = clean(tokens[index + 1].group(0))
            winner, decision = note_winner(note, home, away)
            observations.append({
                "fixture": fixture,
                "observation": {
                    "home": home,
                    "away": away,
                    "home_score": hs,
                    "away_score": ass,
                    "winner": winner,
                    "status": c[fi].upper(),
                    "decision": decision,
                    "date": current_date or fixture.get("date", ""),
                    "source_url": source_url,
                },
            })
            continue

        for i in range(1, len(c) - 2):
            if c[i].upper() == "P" and c[i + 1].upper() == "P":
                home, away = c[i - 1], c[i + 2]
                fixture = match_fixture(known, home, away)
                if fixture:
                    observations.append({
                        "fixture": fixture,
                        "observation": {
                            "home": home,
                            "away": away,
                            "home_score": None,
                            "away_score": None,
                            "winner": "",
                            "status": "POSTPONED",
                            "decision": "postponed",
                            "date": current_date or fixture.get("date", ""),
                            "source_url": source_url,
                        },
                    })
                break
        else:
            joined = " ".join(c)
            upper = joined.upper()
            if re.search(r"\bABANDONED\b|\bABD\b", upper):
                fixture = _fixture_from_row_text(known, c)
                if fixture:
                    observations.append({
                        "fixture": fixture,
                        "observation": {
                            "home": fixture["home"],
                            "away": fixture["away"],
                            "home_score": None,
                            "away_score": None,
                            "winner": "",
                            "status": "ABANDONED",
                            "decision": "abandoned",
                            "date": current_date or fixture.get("date", ""),
                            "source_url": source_url,
                        },
                    })
    return observations


def parse_primary_awards(raw, known, source_url):
    """Accept an award only when the source explicitly names the beneficiary."""
    text = textify(raw)
    lines = text.splitlines()
    out = []
    for fixture in known:
        for i, line in enumerate(lines):
            if not compatible(fixture.get("home"), line) and not compatible(fixture.get("away"), line):
                continue
            window = " ".join(lines[max(0, i - 2) : i + 10])
            if not ("walkover" in window.lower() or "awarded" in window.lower()):
                continue
            if norm(fixture.get("home")) not in norm(window) or norm(fixture.get("away")) not in norm(window):
                continue
            winner, decision = note_winner(window, fixture["home"], fixture["away"])
            if winner and decision == "walkover":
                out.append({
                    "fixture": fixture,
                    "observation": {
                        "home": fixture["home"],
                        "away": fixture["away"],
                        "home_score": None,
                        "away_score": None,
                        "winner": winner,
                        "status": "AWARDED",
                        "decision": "walkover",
                        "date": fixture.get("date", ""),
                        "source_url": source_url,
                    },
                })
            break
    return out


def observation_key(item):
    obs = item["observation"]
    return (
        str(obs.get("date") or ""),
        tuple(sorted(pair_key(obs))),
        str(obs.get("status") or ""),
        obs.get("home_score"),
        obs.get("away_score"),
        norm(obs.get("winner")),
    )


def semantic_observation_key(item):
    obs = item["observation"]
    return (
        tuple(sorted(pair_key(obs))),
        norm(obs.get("home")),
        norm(obs.get("away")),
        str(obs.get("status") or "").upper(),
        obs.get("home_score"),
        obs.get("away_score"),
        norm(obs.get("winner")),
        str(obs.get("decision") or "").lower(),
    )


def _date_distance_days(left, right):
    try:
        a = datetime.fromisoformat(str(left)).date()
        b = datetime.fromisoformat(str(right)).date()
    except (TypeError, ValueError):
        return None
    return abs((a - b).days)


def dedupe_observations(items):
    exact = {}
    for item in items:
        key = observation_key(item)
        existing = exact.get(key)
        if existing and existing["observation"].get("source_url") != item["observation"].get("source_url"):
            continue
        exact[key] = item

    rows = sorted(exact.values(), key=lambda item: observation_key(item))
    out = []
    for item in rows:
        obs = item["observation"]
        source = obs.get("source_url")
        status = str(obs.get("status") or "").upper()
        collapsed = False

        # The fixtures/results and live pages can briefly publish the same
        # completed match under adjacent calendar headings. Collapse only that
        # narrow cross-source disagreement. Same-source rows remain distinct, so
        # genuine replay chronology is never erased by this rule.
        if status.startswith("FT"):
            semantic_key = semantic_observation_key(item)
            for index, existing in enumerate(out):
                old_obs = existing["observation"]
                if old_obs.get("source_url") == source:
                    continue
                if semantic_observation_key(existing) != semantic_key:
                    continue
                distance = _date_distance_days(old_obs.get("date"), obs.get("date"))
                if distance is None or distance > 1:
                    continue
                if str(obs.get("date") or "") < str(old_obs.get("date") or ""):
                    out[index] = item
                collapsed = True
                break

        if not collapsed:
            out.append(item)

    return sorted(out, key=lambda item: observation_key(item))


def aliases(name):
    suffix = re.compile(r"\s+(FC|AFC|CFC)$", re.I)
    out = {name, suffix.sub("", name)}
    if not suffix.search(name):
        out |= {name + " FC", name + " AFC"}
    return {x for x in out if x}


def merge_result(data, result):
    changed = False
    for club in aliases(result["home"]) | aliases(result["away"]):
        arr = data.setdefault("result_history", {}).setdefault(club, [])
        if not any(isinstance(old, dict) and same_result(old, result) for old in arr):
            arr.append(dict(result))
            arr.sort(key=lambda row: (str(row.get("date") or ""), 1 if str(row.get("round") or "").lower().endswith(" replay") else 0))
            changed = True
        latest = arr[-1]
        if data.setdefault("results", {}).get(club) != latest:
            data["results"][club] = latest
            changed = True
    return changed


def merge_event(data, event):
    events = data.setdefault("match_events", [])
    key = (
        base_round(event.get("round")),
        str(event.get("date") or ""),
        pair_key(event),
        str(event.get("status") or "").upper(),
    )
    for old in events:
        old_key = (
            base_round(old.get("round")),
            str(old.get("date") or ""),
            pair_key(old),
            str(old.get("status") or "").upper(),
        )
        if old_key == key:
            return False
    events.append(dict(event))
    events.sort(key=lambda row: (str(row.get("date") or ""), base_round(row.get("round"))))
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://www.thefa.com/competitions/thefacup/results")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    round_name, known = active_fixtures(data)
    if not round_name or not known:
        raise SystemExit("Active-round scanner health failure: no canonical active draw available.")

    primary_raw = fetch(args.url)
    fixtures_raw = fetch(FWP_FIXTURES_URL)
    live_raw = fetch(FWP_LIVE_URL)

    by_source = {
        "primary_awards": parse_primary_awards(primary_raw, known, args.url),
        "fwp_fixtures": parse_fwp_observations(fixtures_raw, known, FWP_FIXTURES_URL),
        "fwp_live": parse_fwp_observations(live_raw, known, FWP_LIVE_URL),
    }
    observations = dedupe_observations(sum(by_source.values(), []))
    history = history_rows(data)
    classified = []
    blocked = []
    changed = False

    for item in observations:
        fixture, observation = item["fixture"], item["observation"]
        try:
            outcome = classify_observation(fixture, observation, history)
        except ValueError as exc:
            blocked.append({"fixture": f'{fixture.get("home")} v {fixture.get("away")}', "date": observation.get("date", ""), "error": str(exc)})
            continue
        classified.append(outcome)
        if outcome["kind"] == "result":
            result = outcome["result"]
            if merge_result(data, result):
                changed = True
                history.append(result)
                history = unique_history(history)
        elif outcome["kind"] == "event":
            if merge_event(data, outcome["event"]):
                changed = True

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "scan_round": round_name,
        "known_ties": len(known),
        "source_observations": {name: len(rows) for name, rows in by_source.items()},
        "semantic_observations": len(observations),
        "classified_results": sum(1 for item in classified if item["kind"] == "result"),
        "classified_events": sum(1 for item in classified if item["kind"] == "event"),
        "duplicates": sum(1 for item in classified if item["kind"] == "duplicate"),
        "blocked": blocked,
        "publish": bool(args.publish),
        "competition_changed": bool(changed),
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("ROUND-AGNOSTIC RESULT SCAN")
    print("Active round:", round_name)
    print("Canonical ties:", len(known))
    print("FWP fixture observations:", len(by_source["fwp_fixtures"]))
    print("FWP live observations:", len(by_source["fwp_live"]))
    print("Explicit primary awards:", len(by_source["primary_awards"]))
    print("Semantic observations:", len(observations))
    print("Results classified:", report["classified_results"])
    print("Unresolved events classified:", report["classified_events"])
    print("Blocked chronology conflicts:", len(blocked))

    if blocked and args.publish:
        raise SystemExit("Publication blocked by chronology conflict(s): " + str(blocked[:5]))

    if args.publish and changed:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("PUBLISHED: competition state updated")
    elif args.publish:
        print("PUBLISHED: 0 changes")
    else:
        print("DRY RUN: competition.json unchanged")


if __name__ == "__main__":
    main()
