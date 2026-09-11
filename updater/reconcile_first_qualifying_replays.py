#!/usr/bin/env python3
"""Reconcile all completed 2026-27 FA Cup First Qualifying replays.

The 31 replay results below are the verified 7-9 September replay slate from
Football Web Pages. Publication remains guarded: every replay pair must belong to
the archived 112 First Qualifying ties and its canonical first leg must already
be recorded as a draw. No result is inferred from the draw or from the next
round. The manifest makes this historical repair deterministic even when legacy
result rows have incomplete metadata or the live source is temporarily blocked.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
ROUND = "First Round Qualifying"
REPLAY_ROUND = ROUND + " Replay"
EXPECTED_TIES = 112
EXPECTED_REPLAYS = 31

SOURCES = {
    "2026-09-07": "https://www.footballwebpages.co.uk/fa-cup/20260907",
    "2026-09-08": "https://www.footballwebpages.co.uk/fa-cup/20260908",
    "2026-09-09": "https://www.footballwebpages.co.uk/fa-cup/20260909",
}

# date, home, home score, away score, away, decision
VERIFIED_REPLAYS = [
    ("2026-09-07", "Carshalton Athletic", 1, 2, "Chertsey Town", ""),
    ("2026-09-07", "Redditch United", 4, 0, "Malvern Town", ""),
    ("2026-09-07", "Swindon Supermarine", 3, 1, "Winslow United", ""),
    ("2026-09-08", "AFC Stoneham", 1, 0, "Basingstoke Town", ""),
    ("2026-09-08", "Barton Town", 2, 0, "North Ferriby", ""),
    ("2026-09-08", "Boldmere St Michaels", 2, 1, "Bourne Town", ""),
    ("2026-09-08", "Brentwood Town", 4, 2, "Concord Rangers", ""),
    ("2026-09-08", "Buckhurst Hill", 3, 0, "Yaxley", ""),
    ("2026-09-08", "Cray Wanderers", 1, 0, "Lewes", ""),
    ("2026-09-08", "Dartford", 2, 0, "Westfield", ""),
    ("2026-09-08", "Fakenham Town", 1, 3, "Ware", ""),
    ("2026-09-08", "Felixstowe & Walton United", 0, 2, "Wingate & Finchley", ""),
    ("2026-09-08", "Guiseley", 2, 1, "Stockton Town", ""),
    ("2026-09-08", "Hashtag United", 0, 2, "St Albans City", ""),
    ("2026-09-08", "Havant & Waterlooville", 1, 3, "Chippenham Town", ""),
    ("2026-09-08", "Hitchin Town", 3, 0, "Biggleswade Town", ""),
    ("2026-09-08", "Kettering Town", 2, 1, "Wellingborough Town", ""),
    ("2026-09-08", "Leiston", 5, 0, "Grays Athletic", ""),
    ("2026-09-08", "Mangotsfield United", 0, 4, "Gloucester City", ""),
    ("2026-09-08", "Needham Market", 3, 1, "Stanway Rovers", ""),
    ("2026-09-08", "Newmarket Town", 0, 1, "Canvey Island", ""),
    ("2026-09-08", "Pagham", 2, 0, "Ascot United", ""),
    ("2026-09-08", "Portishead Town", 1, 3, "Wimborne Town", "aet"),
    ("2026-09-08", "Prestwich Heys", 1, 2, "South Liverpool", ""),
    ("2026-09-08", "Tadcaster Albion", 0, 2, "Lancaster City", ""),
    ("2026-09-08", "Warrington Town", 4, 0, "Shildon", ""),
    ("2026-09-08", "Welling United", 2, 1, "Faversham Town", ""),
    ("2026-09-08", "Worcester City", 1, 0, "Knowle", ""),
    ("2026-09-09", "AFC Whyteleafe", 2, 3, "Crowborough Athletic", ""),
    ("2026-09-09", "Bishop Auckland", 0, 2, "Emley AFC", "aet"),
    ("2026-09-09", "Exmouth Town", 2, 1, "Banbury United", ""),
]


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def pair_key(a, b):
    return tuple(sorted((norm(a), norm(b))))


def compatible(a, b):
    a, b = norm(a), norm(b)
    return bool(a and b and (a == b or a.startswith(b + " ") or b.startswith(a + " ")))


def score_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def all_results(data):
    out, seen, sources = [], set(), []
    sources.extend((data.get("results") or {}).values())
    for rows in (data.get("result_history") or {}).values():
        if isinstance(rows, list):
            sources.extend(rows)
    for r in sources:
        if not isinstance(r, dict):
            continue
        ident = (
            norm(r.get("home")), norm(r.get("away")), r.get("date", ""),
            score_int(r.get("home_score")), score_int(r.get("away_score")),
            str(r.get("round") or "").lower(),
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
    return {pair_key(f["home"], f["away"]): f for f in ties}


def first_leg_is_draw(key, rows):
    for r in rows:
        if pair_key(r.get("home"), r.get("away")) != key:
            continue
        if "replay" in str(r.get("round") or "").lower():
            continue
        hs, aw = score_int(r.get("home_score")), score_int(r.get("away_score"))
        if hs is not None and aw is not None and hs == aw:
            return True
    return False


def result_from_manifest(item):
    date, home, hs, aw, away, decision = item
    return {
        "home": home,
        "away": away,
        "home_score": hs,
        "away_score": aw,
        "winner": home if hs > aw else away,
        "status": "AET" if decision == "aet" else "FT",
        "decision": decision,
        "date": date,
        "round": REPLAY_ROUND,
        "source_url": SOURCES[date],
    }


def same_result(a, b):
    return (
        norm(a.get("home")) == norm(b.get("home"))
        and norm(a.get("away")) == norm(b.get("away"))
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
        conflicts = [
            x for x in rows if isinstance(x, dict)
            and pair_key(x.get("home"), x.get("away")) == pair_key(result["home"], result["away"])
            and str(x.get("date") or "") == result["date"]
            and not same_result(x, result)
        ]
        if conflicts:
            raise SystemExit(f"Replay reconciliation blocked: conflicting canonical replay for {result['home']} v {result['away']}")
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
    matches = [w for w in winners if sum(1 for alt in alts if compatible(alt, w)) == 1]
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
    if len(VERIFIED_REPLAYS) != EXPECTED_REPLAYS or len({pair_key(x[1], x[4]) for x in VERIFIED_REPLAYS}) != EXPECTED_REPLAYS:
        raise SystemExit("Replay reconciliation blocked: verified replay manifest is incomplete or duplicated")

    data = json.loads(DATA.read_text(encoding="utf-8"))
    ties = archived_ties(data)
    rows = all_results(data)
    results = [result_from_manifest(x) for x in VERIFIED_REPLAYS]

    bad_pairs = [r for r in results if pair_key(r["home"], r["away"]) not in ties]
    if bad_pairs:
        raise SystemExit("Replay reconciliation blocked: replay pair absent from archived First Qualifying draw: " + ", ".join(f"{r['home']} / {r['away']}" for r in bad_pairs))

    no_draw = [r for r in results if not first_leg_is_draw(pair_key(r["home"], r["away"]), rows)]
    if no_draw:
        raise SystemExit("Replay reconciliation blocked: prerequisite drawn first leg missing: " + ", ".join(f"{r['home']} / {r['away']}" for r in no_draw))

    changed = sum(1 for result in results if merge(data, result))
    winners = [r["winner"] for r in results]
    resolved = resolve_next_round(data, winners)
    unlinked = sorted(w for w in winners if not winner_in_next_round(data, w))
    if unlinked:
        raise SystemExit("Replay reconciliation blocked: replay winners missing from Second Qualifying draw: " + ", ".join(unlinked))

    if changed or resolved:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("FIRST QUALIFYING REPLAY RECONCILIATION: PASS")
    print("Archived First Qualifying ties:", len(ties))
    print("Verified replay manifest:", len(results))
    print("Prerequisite drawn first legs verified:", len(results))
    print("Replay records added/updated:", changed)
    print("Conditional Second Qualifying sides resolved:", resolved)
    print("Replay winners linked to Second Qualifying:", len(winners))


if __name__ == "__main__":
    main()
