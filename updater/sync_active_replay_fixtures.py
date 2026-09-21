#!/usr/bin/env python3
"""Guardedly populate competition.json replays from proven unresolved draws.

A source fixture can supply schedule details only. Replay ancestry must already
exist as a qualifying-round draw in canonical result history. Ambiguous mappings
fail closed; unrelated source rows are ignored; completed replays are pruned.
"""
import html as H
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from round_state_engine import REPLAY_ROUNDS, base_round, compatible, norm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
REPORT = ROOT / "updater" / "active-replay-fixture-sync-report.json"
SOURCE_URL = "https://www.footballwebpages.co.uk/fa-cup/fixtures-results"
UA = "Mozilla/5.0 TinFoilFACupReplayFixtureSync/7.9.26"


def fetch(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}
    )
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


def clean(value):
    text = H.unescape(re.sub(r"<[^>]+>", " ", str(value or ""))).replace("\xa0", " ")
    return " ".join(text.split())


def cells(row):
    return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)]


def strip_seed(value):
    return re.sub(r"^\(\d+\)\s*|\s*\(\d+\)$", "", str(value or "").strip()).strip()


def date_from_text(text):
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(20\d{2})", str(text or ""), re.I)
    if not m:
        return ""
    try:
        return datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %B %Y").date().isoformat()
    except ValueError:
        return ""


def parse_time(value):
    s = str(value or "").strip().lower().replace(" ", "").replace(".", ":")
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?(am|pm)?", s)
    if not m:
        return ""
    hour, minute, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
    if minute > 59:
        return ""
    if ap:
        if not 1 <= hour <= 12:
            return ""
        if ap == "pm" and hour != 12:
            hour += 12
        if ap == "am" and hour == 12:
            hour = 0
    elif hour > 23:
        return ""
    return f"{hour:02d}:{minute:02d}"


def score_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def pair(row):
    return frozenset((norm(row.get("home")), norm(row.get("away"))))


def result_key(row):
    return (
        str(row.get("round") or "").lower(),
        tuple(sorted(pair(row))),
        str(row.get("date") or ""),
        score_int(row.get("home_score")),
        score_int(row.get("away_score")),
        norm(row.get("winner")),
        str(row.get("decision") or "").lower(),
    )


def all_results(data):
    rows = [x for x in (data.get("results") or {}).values() if isinstance(x, dict)]
    for arr in (data.get("result_history") or {}).values():
        if isinstance(arr, list):
            rows.extend(x for x in arr if isinstance(x, dict))
    out, seen = [], set()
    for row in rows:
        if not row.get("home") or not row.get("away"):
            continue
        key = result_key(row)
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def is_original_draw(row):
    rnd = str(row.get("round") or "")
    base = base_round(rnd)
    if base not in REPLAY_ROUNDS or rnd.lower().endswith(" replay") or row.get("winner"):
        return False
    if str(row.get("decision") or "").lower() == "draw-replay":
        return True
    hs, aw = score_int(row.get("home_score")), score_int(row.get("away_score"))
    return hs is not None and aw is not None and hs == aw


def is_terminal_replay(row, draw):
    if base_round(row.get("round")) != base_round(draw.get("round")):
        return False
    if not str(row.get("round") or "").lower().endswith(" replay"):
        return False
    if pair(row) != pair(draw):
        return False
    if row.get("winner"):
        return True
    hs, aw = score_int(row.get("home_score")), score_int(row.get("away_score"))
    return hs is not None and aw is not None and hs != aw


def unresolved_draws(data):
    rows = all_results(data)
    draws = {}
    for row in rows:
        if not is_original_draw(row):
            continue
        key = (base_round(row.get("round")), tuple(sorted(pair(row))))
        old = draws.get(key)
        if old is None or str(row.get("date") or "") > str(old.get("date") or ""):
            draws[key] = row
    out = [dict(draw) for draw in draws.values() if not any(is_terminal_replay(row, draw) for row in rows)]
    return sorted(out, key=lambda r: (str(r.get("date") or ""), base_round(r.get("round")), norm(r.get("home"))))


def parse_source_fixtures(raw, source_url=SOURCE_URL):
    tokens = list(re.finditer(r"<(h[234]|tr)\b[^>]*>.*?</\1>", raw, re.I | re.S))
    current_date = date_from_text(clean(raw))
    out, seen = [], set()
    for token in tokens:
        tag, block = token.group(1).lower(), token.group(0)
        if tag != "tr":
            current_date = date_from_text(clean(block)) or current_date
            continue
        row = [x for x in cells(block) if x]
        current_date = date_from_text(" ".join(row)) or current_date
        try:
            vi = next(i for i, value in enumerate(row) if value.lower() == "v")
        except StopIteration:
            continue
        if vi < 1 or vi + 1 >= len(row):
            continue
        home, away = strip_seed(row[vi - 1]), strip_seed(row[vi + 1])
        if not home or not away or not current_date:
            continue
        kickoff = parse_time(row[vi - 2]) if vi >= 2 else ""
        fixture = {
            "home": home,
            "away": away,
            "date": current_date,
            "kickoff": kickoff or "Kick-off TBC",
            "source_url": source_url,
        }
        key = (norm(home), norm(away), current_date, fixture["kickoff"])
        if key not in seen:
            seen.add(key)
            out.append(fixture)
    return out


def matches(fixture, draw):
    return (
        compatible(fixture.get("home"), draw.get("home"))
        and compatible(fixture.get("away"), draw.get("away"))
    ) or (
        compatible(fixture.get("home"), draw.get("away"))
        and compatible(fixture.get("away"), draw.get("home"))
    )


def aliases(name):
    name = str(name or "").strip()
    suffix = re.compile(r"\s+(FC|AFC|CFC)$", re.I)
    out = {name, suffix.sub("", name)}
    if name and not suffix.search(name):
        out |= {name + " FC", name + " AFC"}
    return {x for x in out if x}


def fixture_values(src):
    values = src.values() if isinstance(src, dict) else (src or [])
    return [dict(x) for x in values if isinstance(x, dict) and x.get("home") and x.get("away")]


def existing_replays(data):
    out = {}
    for fixture in fixture_values(data.get("replays") or {}):
        key = (
            base_round(fixture.get("round")),
            tuple(sorted(pair(fixture))),
            str(fixture.get("date") or ""),
            str(fixture.get("kickoff") or ""),
        )
        out[key] = fixture
    return list(out.values())


def resolve(data, source_fixtures):
    draws, existing = unresolved_draws(data), existing_replays(data)
    chosen, discovered, retained, awaiting = [], 0, 0, []

    for source in source_fixtures:
        mapped = [draw for draw in draws if matches(source, draw)]
        if len(mapped) > 1:
            raise SystemExit(
                "ACTIVE REPLAY FIXTURE SYNC: ABORT - source fixture maps to multiple draws: "
                f"{source.get('home')} v {source.get('away')}"
            )

    for draw in draws:
        found = [source for source in source_fixtures if matches(source, draw)]
        if len(found) > 1:
            raise SystemExit(
                "ACTIVE REPLAY FIXTURE SYNC: ABORT - multiple source fixtures map to "
                f"{draw.get('home')} / {draw.get('away')}"
            )
        fixture = None
        if found:
            source = found[0]
            fixture = {
                "round": base_round(draw.get("round")) + " Replay",
                "home": source["home"],
                "away": source["away"],
                "date": source["date"],
                "kickoff": source.get("kickoff") or "Kick-off TBC",
                "source_url": source.get("source_url") or SOURCE_URL,
            }
            discovered += 1
        else:
            old = [fixture for fixture in existing if matches(fixture, draw)]
            if len(old) > 1:
                raise SystemExit(
                    "ACTIVE REPLAY FIXTURE SYNC: ABORT - multiple stored replay fixtures map to "
                    f"{draw.get('home')} / {draw.get('away')}"
                )
            if old:
                fixture, retained = old[0], retained + 1
        if fixture is None:
            awaiting.append(draw)
        else:
            chosen.append((draw, fixture))

    replay_map, owners = {}, {}
    for draw, fixture in chosen:
        identity = (
            base_round(fixture.get("round")),
            tuple(sorted(pair(fixture))),
            str(fixture.get("date") or ""),
        )
        names = aliases(draw.get("home")) | aliases(draw.get("away")) | aliases(fixture.get("home")) | aliases(fixture.get("away"))
        for name in names:
            if name in owners and owners[name] != identity:
                raise SystemExit("ACTIVE REPLAY FIXTURE SYNC: ABORT - alias collision for " + name)
            owners[name] = identity
            replay_map[name] = dict(fixture)

    details = {
        "unresolved_draws": len(draws),
        "discovered_replays": discovered,
        "retained_existing_replays": retained,
        "unique_replay_fixtures": len(chosen),
        "awaiting_fixture_details": [
            {
                "round": base_round(draw.get("round")),
                "home": draw.get("home"),
                "away": draw.get("away"),
                "date": draw.get("date"),
            }
            for draw in awaiting
        ],
    }
    return replay_map, details


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    draws = unresolved_draws(data)
    source = parse_source_fixtures(fetch(SOURCE_URL)) if draws else []
    replay_map, details = resolve(data, source)
    changed = (data.get("replays") or {}) != replay_map
    if changed:
        data["replays"] = replay_map
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        tmp = DATA.with_suffix(".json.new")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(DATA)
    REPORT.write_text(
        json.dumps(
            {
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "status": "PASS",
                "source_url": SOURCE_URL,
                "source_fixture_rows": len(source),
                "competition_changed": changed,
                **details,
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    print("ACTIVE REPLAY FIXTURE SYNC: PASS")
    print("Unresolved qualifying draws:", details["unresolved_draws"])
    print("Source fixture rows observed:", len(source))
    print("Replay fixtures discovered:", details["discovered_replays"])
    print("Replay fixtures retained:", details["retained_existing_replays"])
    print("Replay fixtures awaiting details:", len(details["awaiting_fixture_details"]))
    print("Unique replay fixtures published:", details["unique_replay_fixtures"])
    print("Competition data changed:", changed)


if __name__ == "__main__":
    main()
