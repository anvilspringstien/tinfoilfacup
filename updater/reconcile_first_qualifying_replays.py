#!/usr/bin/env python3
"""Reconcile every completed 2026-27 FA Cup First Qualifying replay.

Uses the archived 112 First Qualifying fixtures as the canonical tie set, then
identifies the drawn first legs from recorded scores. This deliberately does not
require legacy result rows to carry a round label. Replay rows are discovered
from the FA Cup date pages for 7-9 September, matched by unordered club pair,
and merged idempotently. Known conditional Second Qualifying draw slots are
resolved once a replay winner is verified.
"""
import html as H
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
ROUND = "First Round Qualifying"
REPLAY_ROUND = ROUND + " Replay"
EXPECTED_TIES = 112
EXPECTED_DRAWS = 31
REPLAY_DATES = {
    "2026-09-07": "https://www.footballwebpages.co.uk/fa-cup/20260907",
    "2026-09-08": "https://www.footballwebpages.co.uk/fa-cup/20260908",
    "2026-09-09": "https://www.footballwebpages.co.uk/fa-cup/20260909",
}


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def pair_key(a, b):
    return tuple(sorted((norm(a), norm(b))))


def compatible(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b and (a == b or a.startswith(b + " ") or b.startswith(a + " ")))


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 TinFoilFACupUpdater/7.6",
        "Accept": "text/html,application/xhtml+xml",
    })
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def clean(x):
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", x)).replace("\xa0", " ").split())


def cells(row):
    return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)]


def score_cell(s):
    m = re.fullmatch(r"(?:\(\d+\)\s*)?(\d+)(?:\s*\(\d+\))?", (s or "").strip())
    return int(m.group(1)) if m else None


def score_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def all_results(data):
    out, seen = [], set()
    sources = []
    sources.extend((data.get("results") or {}).values())
    for rows in (data.get("result_history") or {}).values():
        if isinstance(rows, list):
            sources.extend(rows)
    for r in sources:
        if not isinstance(r, dict):
            continue
        ident = (
            norm(r.get("home")), norm(r.get("away")), r.get("date", ""),
            score_int(r.get("home_score")), score_int(r.get("away_score")), str(r.get("round") or "").lower()
        )
        if ident not in seen:
            seen.add(ident)
            out.append(r)
    return out


def archived_ties(data):
    src = (data.get("round_fixtures") or {}).get(ROUND)
    ties = [f for f in fixture_values(src) if isinstance(f, dict) and f.get("home") and f.get("away")]
    if len(ties) != EXPECTED_TIES:
        raise SystemExit(f"Replay reconciliation blocked: expected {EXPECTED_TIES} archived First Qualifying ties, found {len(ties)}")
    return {pair_key(f["home"], f["away"]): (f["home"], f["away"]) for f in ties}


def drawn_originals(data):
    ties = archived_ties(data)
    results = all_results(data)
    draws = {}
    for key, names in ties.items():
        for r in results:
            if pair_key(r.get("home"), r.get("away")) != key:
                continue
            if "replay" in str(r.get("round") or "").lower():
                continue
            hs, aw = score_int(r.get("home_score")), score_int(r.get("away_score"))
            if hs is not None and aw is not None and hs == aw:
                draws[key] = names
                break
    return draws


def parse_date_page(page, date, source_url, draws):
    found = {}
    for row in re.findall(r"<tr\b[^>]*>.*?</tr>", page, re.I | re.S):
        c = [x for x in cells(row) if x]
        try:
            fi = next(i for i, x in enumerate(c) if x.upper().startswith("FT"))
        except StopIteration:
            continue
        status = c[fi].upper()
        tail = c[fi + 1:]
        score = None
        for i in range(len(tail) - 1):
            hs, aw = score_cell(tail[i]), score_cell(tail[i + 1])
            if hs is not None and aw is not None and i >= 1 and i + 2 < len(tail):
                score = (i, hs, aw)
                break
        if not score:
            continue
        i, hs, aw = score
        home = " ".join(tail[:i]).strip()
        away = tail[i + 2].strip()
        key = pair_key(home, away)
        if key not in draws:
            continue
        if hs == aw:
            raise SystemExit(f"Replay reconciliation blocked: replay still level after FT: {home} {hs}-{aw} {away}")
        result = {
            "home": home, "away": away, "home_score": hs, "away_score": aw,
            "winner": home if hs > aw else away,
            "status": "AET" if "AET" in status else "FT",
            "decision": "aet" if "AET" in status else "",
            "date": date, "round": REPLAY_ROUND, "source_url": source_url,
        }
        if key in found and found[key] != result:
            raise SystemExit(f"Replay reconciliation blocked: conflicting rows for {home} v {away}")
        found[key] = result
    return found


def same_result(a, b):
    return (
        norm(a.get("home")) == norm(b.get("home")) and norm(a.get("away")) == norm(b.get("away"))
        and score_int(a.get("home_score")) == score_int(b.get("home_score"))
        and score_int(a.get("away_score")) == score_int(b.get("away_score"))
        and str(a.get("date") or "") == str(b.get("date") or "")
    )


def aliases(name):
    suffix = re.compile(r"\s+(FC|AFC|CFC)$", re.I)
    out = {name, suffix.sub("", name)}
    if not suffix.search(name):
        out |= {name + " FC", name + " AFC"}
    return {x for x in out if x}


def merge(data, result):
    changed = False
    for club in aliases(result["home"]) | aliases(result["away"]):
        rows = data.setdefault("result_history", {}).setdefault(club, [])
        if not any(same_result(x, result) for x in rows if isinstance(x, dict)):
            rows.append(dict(result))
            rows.sort(key=lambda x: (x.get("date", ""), 0 if "Replay" not in str(x.get("round", "")) else 1))
            changed = True
        current = (data.setdefault("results", {}) or {}).get(club)
        if not isinstance(current, dict) or not same_result(current, result):
            data["results"][club] = dict(result)
            changed = True
    return changed


def resolve_conditional_side(side, winners):
    text = str(side or "")
    alts = [x.strip() for x in re.split(r"\s+or\s+", text, flags=re.I) if x.strip()]
    if len(alts) <= 1:
        return text
    matches = [winner for winner in winners if sum(1 for alt in alts if compatible(alt, winner)) == 1]
    matches = list(dict.fromkeys(matches))
    return matches[0] if len(matches) == 1 else text


def second_round_sources(data):
    sources = [data.get("fixtures") or {}]
    rf = data.get("round_fixtures") or {}
    if "Second Round Qualifying" in rf:
        sources.append(rf["Second Round Qualifying"])
    return sources


def resolve_next_round(data, winners):
    changed = 0
    for src in second_round_sources(data):
        for f in fixture_values(src):
            if not isinstance(f, dict):
                continue
            for field in ("home", "away"):
                old = f.get(field, "")
                new = resolve_conditional_side(old, winners)
                if new != old:
                    f[field] = new
                    changed += 1
    return changed


def winner_in_next_round(data, winner):
    for src in second_round_sources(data):
        for f in fixture_values(src):
            if isinstance(f, dict) and (compatible(f.get("home"), winner) or compatible(f.get("away"), winner)):
                return True
    return False


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    draws = drawn_originals(data)
    if len(draws) != EXPECTED_DRAWS:
        raise SystemExit(f"Replay reconciliation blocked: expected {EXPECTED_DRAWS} drawn First Qualifying ties, found {len(draws)}")

    discovered = {}
    for date, url in REPLAY_DATES.items():
        for key, result in parse_date_page(fetch(url), date, url, draws).items():
            if key in discovered and discovered[key] != result:
                raise SystemExit(f"Replay reconciliation blocked: conflicting replay for {key}")
            discovered[key] = result

    missing = sorted(set(draws) - set(discovered))
    if missing or len(discovered) != EXPECTED_DRAWS:
        raise SystemExit(f"Replay reconciliation blocked: discovered {len(discovered)}/{EXPECTED_DRAWS}; missing={missing[:10]}")

    changed = sum(1 for result in discovered.values() if merge(data, result))
    winners = [r["winner"] for r in discovered.values()]
    resolved = resolve_next_round(data, winners)
    unlinked = sorted(w for w in winners if not winner_in_next_round(data, w))
    if unlinked:
        raise SystemExit("Replay reconciliation blocked: replay winners missing from Second Qualifying draw: " + ", ".join(unlinked))

    if changed or resolved:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("FIRST QUALIFYING REPLAY RECONCILIATION: PASS")
    print("Archived First Qualifying ties:", EXPECTED_TIES)
    print("Drawn original ties:", len(draws))
    print("Completed replays discovered:", len(discovered))
    print("Replay records added/updated:", changed)
    print("Conditional Second Qualifying sides resolved:", resolved)
    print("Replay winners linked to Second Qualifying:", len(winners))


if __name__ == "__main__":
    main()
