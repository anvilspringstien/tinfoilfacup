#!/usr/bin/env python3
"""Propagate verified active-fixture venues to every semantic fixture copy.

The canonical top-level `fixtures` collection is enriched first by the existing
venue stages. Clubfinder also consumes derived/copy fixture records elsewhere
in competition.json. This stage copies a verified venue only to records that
represent the same fixture (same home/away, with compatible round/date), and
never overwrites a conflicting verified venue.

No venue is guessed here: this script only propagates venue data that has
already been verified by the guarded enrichment stages.
"""
import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "competition.json"
REPORT = ROOT / "updater" / "venue-copy-consistency-report.json"


def norm(s):
    s = str(s or "").lower().replace("&", " and ")
    s = re.sub(r"\b(fc|afc|cfc|football club)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def fixture_values(src):
    return list(src.values()) if isinstance(src, dict) else list(src or [])


def venue_postcode(row):
    v = row.get("venue") if isinstance(row, dict) else None
    if not isinstance(v, dict):
        return ""
    return re.sub(r"\s+", " ", str(v.get("postcode") or "").upper()).strip()


def valid_venue(row):
    pc = venue_postcode(row)
    return bool(pc) and "TBC" not in pc


def has_played_score(row):
    if not isinstance(row, dict):
        return False
    return row.get("home_score") is not None or row.get("away_score") is not None


def same_fixture(candidate, source):
    if not isinstance(candidate, dict) or not isinstance(source, dict):
        return False
    if norm(candidate.get("home")) != norm(source.get("home")):
        return False
    if norm(candidate.get("away")) != norm(source.get("away")):
        return False
    # A scored row is result/history data, not an upcoming fixture copy.
    if has_played_score(candidate):
        return False
    for field in ("round", "date"):
        a = str(candidate.get(field) or "").strip()
        b = str(source.get(field) or "").strip()
        if a and b and a != b:
            return False
    return True


def walk_dicts(obj, path="$", seen=None):
    if seen is None:
        seen = set()
    oid = id(obj)
    if oid in seen:
        return
    if isinstance(obj, dict):
        seen.add(oid)
        yield path, obj
        for key, value in obj.items():
            yield from walk_dicts(value, f"{path}.{key}", seen)
    elif isinstance(obj, list):
        seen.add(oid)
        for i, value in enumerate(obj):
            yield from walk_dicts(value, f"{path}[{i}]", seen)


def canonical_active_fixtures(data):
    rows = []
    for f in fixture_values(data.get("fixtures") or {}):
        if not isinstance(f, dict) or not f.get("home") or not f.get("away"):
            continue
        if has_played_score(f) or not valid_venue(f):
            continue
        rows.append(f)
    return rows


def main():
    data = json.loads(COMP.read_text(encoding="utf-8"))
    sources = canonical_active_fixtures(data)
    all_rows = list(walk_dicts(data))
    changed = 0
    matched_copies = 0
    conflicts = []
    touched = []

    for source in sources:
        source_pc = venue_postcode(source)
        for path, candidate in all_rows:
            if candidate is source or not same_fixture(candidate, source):
                continue
            matched_copies += 1
            candidate_pc = venue_postcode(candidate)
            if candidate_pc and "TBC" not in candidate_pc:
                if candidate_pc != source_pc:
                    conflicts.append(
                        f"{source.get('home')} v {source.get('away')} at {path}: "
                        f"canonical {source_pc}, copy {candidate_pc}"
                    )
                continue
            candidate["venue"] = copy.deepcopy(source["venue"])
            changed += 1
            touched.append({
                "path": path,
                "home": source.get("home"),
                "away": source.get("away"),
                "round": source.get("round"),
                "date": source.get("date"),
                "postcode": source_pc,
            })

    if conflicts:
        raise SystemExit("ABORT: conflicting verified venue copies: " + " | ".join(conflicts[:10]))

    # Exact production regression anchors. Every matching future fixture copy
    # must carry the verified postcode, not merely the first top-level record.
    anchors = (
        ("Hampton & Richmond Borough", "Crowborough Athletic", "TW12 2BX"),
        ("Frome Town", "Plymouth Parkway", "BA11 2EH"),
        ("Dulwich Hamlet", "Welling United", "SE22 8BD"),
    )
    anchor_counts = {}
    for home, away, postcode in anchors:
        source_matches = [s for s in sources if norm(s.get("home")) == norm(home) and norm(s.get("away")) == norm(away)]
        if len(source_matches) != 1:
            raise SystemExit(f"ABORT: expected one canonical active fixture for {home} v {away}, found {len(source_matches)}")
        source = source_matches[0]
        copies = [(path, row) for path, row in all_rows if same_fixture(row, source)]
        if not copies:
            raise SystemExit(f"ABORT: no semantic fixture copies found for {home} v {away}")
        bad = [(path, venue_postcode(row) or "TBC") for path, row in copies if venue_postcode(row) != postcode]
        if bad:
            details = ", ".join(f"{path}={pc}" for path, pc in bad[:10])
            raise SystemExit(f"ABORT: inconsistent venue copies for {home} v {away}; expected {postcode}: {details}")
        anchor_counts[f"{home} v {away}"] = len(copies)

    if changed:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        COMP.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "canonical_active_fixtures_with_verified_venues": len(sources),
        "semantic_fixture_copies_examined": matched_copies,
        "fixture_copies_updated": changed,
        "anchor_copy_counts": anchor_counts,
        "updated_copies": touched,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ACTIVE FIXTURE VENUE COPY CONSISTENCY: PASS")
    print("Canonical verified active fixtures:", len(sources))
    print("Semantic fixture copies examined:", matched_copies)
    print("Fixture copies updated:", changed)
    for name, count in anchor_counts.items():
        print(f"Anchor copies verified: {name}: {count}")


if __name__ == "__main__":
    main()
