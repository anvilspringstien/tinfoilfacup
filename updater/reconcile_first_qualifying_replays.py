#!/usr/bin/env python3
"""Reconcile every completed 2026-27 FA Cup First Qualifying replay.

The original result scanner intentionally anchors itself to the 112 canonical
First Qualifying ties. Football Web Pages now exposes replay results on the
FA Cup date pages, so this pass explicitly audits the replay window (7-9 Sep),
matches rows back to drawn original ties without assuming venue orientation,
publishes missing decisive replays, and resolves conditional Second Qualifying
fixture sides once a replay winner is known.

This script is safe to run repeatedly. It refuses partial replay coverage and
never invents a result or winner.
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


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 TinFoilFACupUpdater/7.6",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def clean(x):
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", x)).replace("\xa0", " ").split())


def cells(row):
    return [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)]


def score_cell(s):
    m = re.fullmatch(r"(?:\(\d+\)\s*)?(\d+)(?:\s*\(\d+\))?", (s or "").strip())
    return int(m.group(1)) if m else None


def history_rows(data):
    seen = set()
    out = []
    for rows in (data.get("result_history") or {}).values():
        if not isinstance(rows, list):
            continue
        for r in rows:
            if not isinstance(r, dict):
                continue
            ident = (
                norm(r.get("home")), norm(r.get("away")), r.get("date", ""),
                r.get("round", ""), r.get("home_score"), r.get("away_score")
            )
            if ident in seen:
                continue
            seen.add(ident)
            out.append(r)
    return out


def drawn_originals(data):
    out = {}
    for r in history_rows(data):
        if str(r.get("round") or "").lower() != ROUND.lower():
            continue
        hs, aw = r.get("home_score"), r.get("away_score")
        if isinstance(hs, int) and isinstance(aw, int) and hs == aw:
            out[pair_key(r.get("home"), r.get("away"))] = (r.get("home"), r.get("away"))
    return out


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
        pair = None
        for i in range(len(tail) - 1):
            hs = score_cell(tail[i])
            aw = score_cell(tail[i + 1])
            if hs is not None and aw is not None and i >= 1 and i + 2 < len(tail):
                pair = (i, hs, aw)
                break
        if not pair:
            continue
        i, hs, aw = pair
        home = " ".join(tail[:i]).strip()
        away = tail[i + 2].strip()
        key = pair_key(home, away)
        if key not in draws:
            continue
        if hs == aw:
            raise SystemExit(f"Replay reconciliation blocked: replay still level after FT: {home} {hs}-{aw} {away}")
        winner = home if hs > aw else away
        result = {
            "home": home,
            "away": away,
            "home_score": hs,
            "away_score": aw,
            "winner": winner,
            "status": "FT",
            "decision": "aet" if "AET" in status else "",
            "date": date,
            "round": REPLAY_ROUND,
            "source_url": source_url,
        }
        if key in found and found[key] != result:
            raise SystemExit(f"Replay reconciliation blocked: conflicting rows for {home} v {away}")
        found[key] = result
    return found


def same_result(a, b):
    return (
        pair_key(a.get("home"), a.get("away")) == pair_key(b.get("home"), b.get("away"))
        and str(a.get("round") or "").lower() == str(b.get("round") or "").lower()
        and a.get("home_score") == b.get("home_score")
        and a.get("away_score") == b.get("away_score")
        and norm(a.get("home")) == norm(b.get("home"))
        and norm(a.get("away")) == norm(b.get("away"))
    )


def merge(data, result):
    changed = False
    names = {
        result["home"], result["away"],
        re.sub(r"\s+(FC|AFC|CFC)$", "", result["home"], flags=re.I),
        re.sub(r"\s+(FC|AFC|CFC)$", "", result["away"], flags=re.I),
    }
    for club in names:
        rows = data.setdefault("result_history", {}).setdefault(club, [])
        if not any(same_result(x, result) for x in rows if isinstance(x, dict)):
            rows.append(dict(result))
            rows.sort(key=lambda x: x.get("date", ""))
            changed = True
        current = (data.setdefault("results", {}) or {}).get(club)
        if not isinstance(current, dict) or not same_result(current, result):
            data["results"][club] = dict(result)
            changed = True
    return changed


def resolve_conditional_side(side, winners):
    text = str(side or "")
    alternatives = [x.strip() for x in re.split(r"\s+or\s+", text, flags=re.I) if x.strip()]
    if len(alternatives) <= 1:
        return text
    matches = []
    for winner in winners:
        if sum(1 for alt in alternatives if compatible(alt, winner)) == 1:
            matches.append(winner)
    matches = list(dict.fromkeys(matches))
    return matches[0] if len(matches) == 1 else text


def fixture_values(src):
    return src.values() if isinstance(src, dict) else (src or [])


def resolve_next_round(data, winners):
    changed = 0
    sources = [data.get("fixtures") or {}]
    rf = data.get("round_fixtures") or {}
    if "Second Round Qualifying" in rf:
        sources.append(rf["Second Round Qualifying"])
    for src in sources:
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
    sources = [data.get("fixtures") or {}]
    rf = data.get("round_fixtures") or {}
    if "Second Round Qualifying" in rf:
        sources.append(rf["Second Round Qualifying"])
    for src in sources:
        for f in fixture_values(src):
            if not isinstance(f, dict):
                continue
            if compatible(f.get("home"), winner) or compatible(f.get("away"), winner):
                return True
    return False


def main():
    data = json.loads(DATA.read_text())
    draws = drawn_originals(data)
    if len(draws) != EXPECTED_DRAWS:
        raise SystemExit(f"Replay reconciliation blocked: expected {EXPECTED_DRAWS} drawn First Qualifying ties, found {len(draws)}")

    discovered = {}
    for date, url in REPLAY_DATES.items():
        rows = parse_date_page(fetch(url), date, url, draws)
        for key, result in rows.items():
            if key in discovered and discovered[key] != result:
                raise SystemExit(f"Replay reconciliation blocked: duplicate/conflicting replay for {key}")
            discovered[key] = result

    missing = sorted(set(draws) - set(discovered))
    unexpected = sorted(set(discovered) - set(draws))
    if missing or unexpected or len(discovered) != EXPECTED_DRAWS:
        raise SystemExit(
            f"Replay reconciliation blocked: discovered {len(discovered)}/{EXPECTED_DRAWS}; "
            f"missing={missing[:10]} unexpected={unexpected[:10]}"
        )

    added = 0
    for result in discovered.values():
        if merge(data, result):
            added += 1

    winners = [r["winner"] for r in discovered.values()]
    resolved = resolve_next_round(data, winners)
    unlinked = sorted(w for w in winners if not winner_in_next_round(data, w))
    if unlinked:
        raise SystemExit("Replay reconciliation blocked: replay winners missing from Second Qualifying draw: " + ", ".join(unlinked))

    if added or resolved:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print("FIRST QUALIFYING REPLAY RECONCILIATION: PASS")
    print("Drawn original ties:", len(draws))
    print("Completed replays discovered:", len(discovered))
    print("Replay records added/updated:", added)
    print("Conditional Second Qualifying sides resolved:", resolved)
    print("Replay winners linked to Second Qualifying:", len(winners))


if __name__ == "__main__":
    main()
