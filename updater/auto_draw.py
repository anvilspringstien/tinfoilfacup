#!/usr/bin/env python3
"""Guarded automatic Emirates FA Cup draw detector/importer.

The official Emirates FA Cup fixtures endpoint (competitionId=1) is authoritative
for fixture publication detection. Only the round immediately after
competition.json/source_round can be promoted.

Existing result/custody history is never rewritten; the outgoing active fixture
map is archived in round_fixtures before the new round becomes active.
"""
import argparse
import html as H
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "competition.json"
REPORT = ROOT / "updater/draw-watch-report.json"
# IMPORTANT: competitionId=1 is the Emirates FA Cup. Do not substitute another
# FA competition ID (for example the FA Trophy) into this production watcher.
FA_PAGE = "https://www.thefa.com/Competitions/Fixtures/Fixtures?competitionId=1&page={}"
OFFICIAL_SOURCE = "https://www.thefa.com/competitions/thefacup/fixtures"
UA = {"User-Agent": "Mozilla/5.0 TinFoilFACupDrawWatcher/1.1", "Accept": "text/html,application/xhtml+xml"}

ROUND_ORDER = [
    "Extra Preliminary Round",
    "Preliminary Round",
    "First Round Qualifying",
    "Second Round Qualifying",
    "Third Round Qualifying",
    "Fourth Round Qualifying",
    "First Round Proper",
    "Second Round Proper",
    "Third Round Proper",
    "Fourth Round Proper",
    "Fifth Round Proper",
    "Quarter Final",
    "Semi Final",
    "Final",
]
ROUND_ALIASES = {
    "Extra Preliminary Round": ["Extra Preliminary Round"],
    "Preliminary Round": ["Preliminary Round"],
    "First Round Qualifying": ["First Round Qualifying", "First Qualifying Round"],
    "Second Round Qualifying": ["Second Round Qualifying", "Second Qualifying Round"],
    "Third Round Qualifying": ["Third Round Qualifying", "Third Qualifying Round"],
    "Fourth Round Qualifying": ["Fourth Round Qualifying", "Fourth Qualifying Round"],
    "First Round Proper": ["First Round Proper", "First Round"],
    "Second Round Proper": ["Second Round Proper", "Second Round"],
    "Third Round Proper": ["Third Round Proper", "Third Round"],
    "Fourth Round Proper": ["Fourth Round Proper", "Fourth Round"],
    "Fifth Round Proper": ["Fifth Round Proper", "Fifth Round"],
    "Quarter Final": ["Quarter Final", "Quarter-Final", "Quarter Finals", "Quarter-Finals"],
    "Semi Final": ["Semi Final", "Semi-Final", "Semi Finals", "Semi-Finals"],
    "Final": ["Final"],
}
_ALIAS_TO_ROUND = {}
for _canonical, _aliases in ROUND_ALIASES.items():
    for _alias in _aliases:
        _ALIAS_TO_ROUND[_alias.lower()] = _canonical
# Longest-first alternatives prevent "Final" from matching inside "Semi Final"
# and "First Round" from matching inside "First Round Qualifying".
ROUND_RE = re.compile(
    r"(?<!\w)(" + "|".join(re.escape(a) for a in sorted(_ALIAS_TO_ROUND, key=len, reverse=True)) + r")(?!\w)",
    re.I,
)
DATE_RE = re.compile(r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})\b", re.I)


def clean(x):
    x = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", x, flags=re.I | re.S)
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", x)).replace("\xa0", " ").split())


def norm(s):
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def canonical_conditional(s):
    s = " ".join((s or "").split())
    if " / " in s:
        parts = [p.strip() for p in s.split(" / ") if p.strip()]
        if len(parts) > 1:
            return " or ".join(parts)
    return s


def alternatives(s):
    return [p.strip() for p in re.split(r"\s+or\s+", s or "", flags=re.I) if p.strip()]


def abbreviation_tokens(value):
    tokens = [token for token in norm(value).split() if token != "and"]
    # Connective "and" (including normalized &) is non-semantic only for\n    # abbreviation comparison; the general club-name normalizer is unchanged.\n    # Apostrophe contractions such as G'borough normalize to ["g","borough"].
    # Rejoin an initial with its retained suffix so it can be compared
    # structurally with the full word without naming a specific club.
    out = []
    i = 0
    while i < len(tokens):
        if len(tokens[i]) == 1 and i + 1 < len(tokens) and len(tokens[i + 1]) >= 3:
            out.append(tokens[i] + tokens[i + 1])
            i += 2
        else:
            out.append(tokens[i])
            i += 1
    return out


def token_compatible(short_token, full_token):
    if short_token == full_token:
        return True
    conventional = {("utd", "united"), ("united", "utd")}
    if (short_token, full_token) in conventional:
        return True
    if len(short_token) < 2:
        return False
    if (len(short_token) >= 3 and full_token.startswith(short_token)) or (len(full_token) >= 3 and short_token.startswith(full_token)):
        return True
    shorter, longer = sorted((short_token, full_token), key=len)
    if len(shorter) >= 4 and shorter[0] == longer[0] and longer.endswith(shorter[1:]):
        return True
    common = 0
    for left, right in zip(shorter, longer):
        if left != right:
            break
        common += 1
    return common >= 4 and len(shorter) >= 5 and len(longer) >= 6

def abbreviation_compatible(a, b):
    aa, bb = abbreviation_tokens(a), abbreviation_tokens(b)
    if not aa or not bb or len(aa) != len(bb):
        return False

    substantive = False
    for x, y in zip(aa, bb):
        if len(x) == 1 or len(y) == 1:
            # A single-letter token is allowed only as one component of a
            # multi-token club name, and only by matching the corresponding
            # full token's initial. Another token must carry substantive proof.
            if len(aa) < 2 or x[0] != y[0]:
                return False
            continue
        if not token_compatible(x, y):
            return False
        if x != y or len(x) >= 3:
            substantive = True
    return substantive


def compatible(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b or a.startswith(b + " ") or b.startswith(a + " "):
        return True
    return abbreviation_compatible(a, b)


def active_source_complete(official_ties, expected_ties):
    return len(official_ties) == int(expected_ties)


def is_conditional_fixture(fixture):
    return len(alternatives(fixture.get("home", ""))) > 1 or len(alternatives(fixture.get("away", ""))) > 1


def side_matches(value, side):
    return any(compatible(value, option) for option in alternatives(side))


def fixture_matches_slot(fixture, slot):
    return (
        not is_conditional_fixture(fixture)
        and side_matches(fixture.get("home", ""), slot.get("home", ""))
        and side_matches(fixture.get("away", ""), slot.get("away", ""))
    )


def reconcile_active_conditionals(current_fixtures, official_fixtures):
    """Collapse saved conditional slots only when the official current-round
    fixture catalogue supplies exactly one compatible definite fixture.

    Non-conditional saved fixtures are retained byte-for-byte in meaning. A
    missing source match leaves the placeholder untouched; multiple matches fail
    closed upstream. This makes same-round replay resolution a producer concern
    rather than a Clubfinder-only inference.
    """
    final = []
    transitions = []
    ambiguities = []
    for saved in current_fixtures:
        if not is_conditional_fixture(saved):
            final.append(dict(saved))
            continue
        matches = [f for f in official_fixtures if fixture_matches_slot(f, saved)]
        if len(matches) > 1:
            ambiguities.append({
                "slot": f'{saved.get("home")} v {saved.get("away")}',
                "matches": [f'{f.get("home")} v {f.get("away")}' for f in matches],
            })
            final.append(dict(saved))
            continue
        if not matches:
            final.append(dict(saved))
            continue
        source = matches[0]
        resolved = dict(saved)
        resolved.update({
            "round": saved.get("round") or source.get("round"),
            "home": source["home"],
            "away": source["away"],
            "date": source.get("date") or saved.get("date", ""),
            "kickoff": source.get("kickoff") or saved.get("kickoff", "15:00"),
        })
        resolved.pop("conditional", None)
        transitions.append({
            "from": f'{saved.get("home")} v {saved.get("away")}',
            "to": f'{resolved.get("home")} v {resolved.get("away")}',
        })
        final.append(resolved)
    return final, transitions, ambiguities


def diagnose_unresolved_conditionals(current_fixtures, official_fixtures):
    diagnostics = []
    for saved in current_fixtures:
        if not is_conditional_fixture(saved):
            continue
        if any(fixture_matches_slot(f, saved) for f in official_fixtures):
            continue
        home_hits = [f for f in official_fixtures if side_matches(f.get("home", ""), saved.get("home", ""))]
        away_hits = [f for f in official_fixtures if side_matches(f.get("away", ""), saved.get("away", ""))]
        diagnostics.append({
            "slot": f'{saved.get("home")} v {saved.get("away")}',
            "home_side_official_candidates": [f'{f.get("home")} v {f.get("away")}' for f in home_hits],
            "away_side_official_candidates": [f'{f.get("home")} v {f.get("away")}' for f in away_hits],
        })
    return diagnostics


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    waits = (2, 5)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=35) as r:
                return r.read().decode("utf-8", "replace")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            transient = not isinstance(e, urllib.error.HTTPError) or e.code in {429, 500, 502, 503, 504}
            if not transient or attempt == 2:
                raise
            wait = waits[attempt]
            print(f"FA SOURCE RETRY: attempt {attempt + 1} failed ({e}); waiting {wait}s.")
            time.sleep(wait)


def round_from_context(context):
    matches = list(ROUND_RE.finditer(clean(context)))
    if not matches:
        return ""
    return _ALIAS_TO_ROUND[matches[-1].group(1).lower()]


def date_from_context(context):
    text = clean(context)
    matches = list(DATE_RE.finditer(text))
    if not matches:
        return ""
    m = matches[-1]
    try:
        return datetime.strptime(f"{m.group(2)} {m.group(3)} {m.group(4)}", "%d %B %Y").date().isoformat()
    except ValueError:
        return ""


def parse_page(page_html):
    rows = []
    for m in re.finditer(r"<tr\b[^>]*>.*?</tr>", page_html, re.I | re.S):
        row = m.group(0)
        cells = [clean(x) for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.I | re.S)]
        if not cells:
            continue
        try:
            vi = next(i for i, c in enumerate(cells) if c.upper() in {"VS", "V", "V."})
        except StopIteration:
            continue
        if vi < 1 or vi + 1 >= len(cells):
            continue
        context = page_html[max(0, m.start() - 18000):m.start()]
        rnd = round_from_context(context)
        date = date_from_context(context)
        home = canonical_conditional(cells[vi - 1])
        away = canonical_conditional(cells[vi + 1])
        kickoff = next((c for c in cells[:vi] if re.fullmatch(r"\d{1,2}:\d{2}", c)), "")
        if rnd and home and away:
            rows.append({"round": rnd, "home": home, "away": away, "date": date, "kickoff": kickoff})
    return rows


def unique_ties(rows):
    out = {}
    for r in rows:
        k = (r["round"], norm(r["home"]), norm(r["away"]), r.get("date", ""))
        out[k] = r
    return list(out.values())


def fixture_values(fixtures):
    vals = fixtures.values() if isinstance(fixtures, dict) else fixtures or []
    out, seen = [], set()
    for f in vals:
        if not isinstance(f, dict) or not f.get("home") or not f.get("away"):
            continue
        k = (norm(f["home"]), norm(f["away"]), f.get("date", ""))
        if k not in seen:
            seen.add(k)
            out.append(dict(f))
    return out


def validate_target(target, ties):
    if len(ties) < 20 and target not in {"Quarter Final", "Semi Final", "Final"}:
        raise SystemExit(f"Publication blocked: only {len(ties)} {target} ties found on official Emirates FA Cup fixture pages.")
    if target == "Quarter Final" and len(ties) != 4:
        raise SystemExit(f"Publication blocked: expected 4 Quarter Final ties, found {len(ties)}.")
    if target == "Semi Final" and len(ties) != 2:
        raise SystemExit(f"Publication blocked: expected 2 Semi Final ties, found {len(ties)}.")
    if target == "Final" and len(ties) != 1:
        raise SystemExit(f"Publication blocked: expected 1 Final tie, found {len(ties)}.")

    concrete = []
    for f in ties:
        for side in (f["home"], f["away"]):
            if " or " not in side.lower():
                concrete.append(norm(side))
    dupes = sorted(k for k, n in Counter(concrete).items() if k and n > 1)
    if dupes:
        raise SystemExit("Publication blocked: concrete clubs appear in more than one target-round tie: " + str(dupes[:12]))

    if not any(f.get("date") for f in ties):
        raise SystemExit("Publication blocked: official target-round rows had no parseable fixture dates.")


def fixture_map(ties):
    out = {}
    suffix = re.compile(r"\s+(FC|AFC|CFC)$", re.I)
    for f in ties:
        rec = dict(f)
        if " or " in rec["home"].lower() or " or " in rec["away"].lower():
            rec["conditional"] = True
        for club in alternatives(rec["home"]) + alternatives(rec["away"]):
            out[club] = rec
            out.setdefault(suffix.sub("", club), rec)
    return out


def write_report(**fields):
    base = {"checked_at": datetime.now(timezone.utc).isoformat(), "official_source": OFFICIAL_SOURCE, "competition_id": 1}
    base.update(fields)
    REPORT.write_text(json.dumps(base, indent=2) + "\n")
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--max-pages", type=int, default=40)
    args = ap.parse_args()

    data = json.loads(DATA.read_text())
    current = data.get("source_round", "")
    if current not in ROUND_ORDER:
        write_report(status="blocked", error=f"Unknown canonical source_round: {current!r}")
        raise SystemExit(f"Draw watcher cannot determine current canonical round from source_round={current!r}.")
    idx = ROUND_ORDER.index(current)
    if idx + 1 >= len(ROUND_ORDER):
        write_report(status="complete", current_round=current, target_round=None, target_ties_detected=0, published=False)
        print("No later Emirates FA Cup round exists after", current)
        return
    target = ROUND_ORDER[idx + 1]

    all_rows = []
    pages_checked = 0
    fetch_stop = "max-pages"
    for page in range(1, args.max_pages + 1):
        try:
            page_html = fetch(FA_PAGE.format(page))
        except urllib.error.HTTPError as e:
            # The FA endpoint returns an error after its last pagination page.
            # That marks the end of the current fixture catalogue, not a failed scan.
            if page > 1 and e.code in {400, 404, 500}:
                fetch_stop = f"end-of-pagination-http-{e.code}"
                break
            write_report(status="error", current_round=current, target_round=target, pages_checked=pages_checked, error=f"HTTP {e.code} on page {page}")
            raise
        except urllib.error.URLError as e:
            write_report(status="error", current_round=current, target_round=target, pages_checked=pages_checked, error=f"URL error on page {page}: {e.reason}")
            raise

        pages_checked += 1
        rows = parse_page(page_html)
        all_rows.extend(rows)
        if not rows and page > 5:
            fetch_stop = "empty-page"
            break

    # Before looking for the next draw, allow the official fixture catalogue to
    # collapse conditional slots in the *current* active round. This is the
    # normal replay-resolution path: the machine updates its canonical fixture
    # producer instead of relying on Clubfinder to infer the winner forever.
    current_official = unique_ties([r for r in all_rows if r["round"] == current])
    saved_current = fixture_values(data.get("fixtures") or {})
    expected_active_ties = int(data.get("source_tie_count") or len(saved_current))
    source_complete = active_source_complete(current_official, expected_active_ties)
    if not source_complete:
        print(
            "ACTIVE ROUND SOURCE INCOMPLETE:",
            f"official={len(current_official)} expected={expected_active_ties}",
        )
        if args.publish:
            write_report(
                status="blocked",
                current_round=current,
                target_round=target,
                pages_checked=pages_checked,
                pagination_stop=fetch_stop,
                active_round_official_ties=len(current_official),
                active_round_expected_ties=expected_active_ties,
                active_round_source_complete=False,
            )
            raise SystemExit("Publication blocked: official active-round fixture catalogue is incomplete.")

    refreshed_current, active_transitions, active_ambiguities = reconcile_active_conditionals(
        saved_current, current_official
    )
    active_unresolved = diagnose_unresolved_conditionals(saved_current, current_official)
    if active_unresolved:
        print(f"ACTIVE ROUND CONDITIONALS UNRESOLVED: {len(active_unresolved)}")
        for diagnostic in active_unresolved:
            print("UNRESOLVED:", diagnostic["slot"])
            print("  HOME CANDIDATES:", diagnostic["home_side_official_candidates"] or ["none"])
            print("  AWAY CANDIDATES:", diagnostic["away_side_official_candidates"] or ["none"])
    if active_ambiguities:
        write_report(
            status="blocked",
            current_round=current,
            target_round=target,
            pages_checked=pages_checked,
            pagination_stop=fetch_stop,
            active_round_official_ties=len(current_official),
            active_round_ambiguities=active_ambiguities,
            active_round_unresolved_diagnostics=active_unresolved,
        )
        raise SystemExit("Publication blocked: active-round conditional slots resolved ambiguously.")

    active_published = False
    if active_transitions:
        print(f"ACTIVE ROUND CONDITIONALS RESOLVED: {len(active_transitions)}")
        for transition in active_transitions:
            print("RESOLVED:", transition["from"], "->", transition["to"])
        if args.publish:
            data["fixtures"] = fixture_map(refreshed_current)
            data["source_tie_count"] = len(refreshed_current)
            data["source_url"] = OFFICIAL_SOURCE
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            active_published = True
        else:
            print("DRY RUN: active-round resolutions not written.")

    target_ties = unique_ties([r for r in all_rows if r["round"] == target])
    report = write_report(
        status="detected" if target_ties else ("active-round-refreshed" if active_published else "no-new-draw"),
        current_round=current,
        target_round=target,
        target_ties_detected=len(target_ties),
        pages_checked=pages_checked,
        pagination_stop=fetch_stop,
        published=active_published,
        active_round_official_ties=len(current_official),
        active_round_conditional_resolutions=active_transitions,
        active_round_unresolved_diagnostics=active_unresolved,
    )

    if not target_ties:
        if active_published:
            print(f"ACTIVE ROUND REFRESH PUBLISHED: {len(active_transitions)} conditional slots collapsed.")
        print(f"NO NEW DRAW: official Emirates FA Cup fixture pages do not yet expose {target}.")
        return

    validate_target(target, target_ties)
    print(f"OFFICIAL EMIRATES FA CUP DRAW DETECTED: {target}: {len(target_ties)} ties")
    if not args.publish:
        print("DRY RUN: competition.json unchanged.")
        return

    old = fixture_values(data.get("fixtures") or {})
    archive = data.setdefault("round_fixtures", {})
    if old and current not in archive:
        archive[current] = old

    data["fixtures"] = fixture_map(target_ties)
    data["source_round"] = target
    data["source_tie_count"] = len(target_ties)
    data["source_url"] = OFFICIAL_SOURCE
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    report.update({
        "status": "published",
        "published": True,
        "archived_outgoing_round": current,
        "archived_outgoing_ties": len(old),
    })
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PUBLISHED: {target}: {len(target_ties)} ties; preserved {len(old)} outgoing ties in round_fixtures/{current}.")


if __name__ == "__main__":
    main()
