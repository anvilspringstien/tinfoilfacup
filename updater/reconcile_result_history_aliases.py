#!/usr/bin/env python3
"""Keep replay-participant result-history identity aliases semantically identical.

Clubfinder origins use canonical eligible-club names (often with FC/AFC suffixes),
while source updaters can encounter suffix-free names. A decisive replay that exists
only in one alias bucket can therefore leave a Campaign stranded on an earlier draw.

Default mode repairs existing alias buckets for clubs whose chronology contains a
replay. --check is read-only and fails closed if any of those aliases contain a
different chronology, or if their latest `results` pointer disagrees with it.
"""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "competition.json"


def norm(value):
    text = str(value or "").lower().replace("&", " and ")
    text = re.sub(r"\b(fc|afc|cfc|football club)\b", " ", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def score_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def semantic_key(row):
    return (
        str(row.get("round") or "").strip().lower(),
        str(row.get("date") or ""),
        norm(row.get("home")),
        norm(row.get("away")),
        score_int(row.get("home_score")),
        score_int(row.get("away_score")),
    )


def sort_key(row):
    round_name = str(row.get("round") or "")
    return (
        str(row.get("date") or ""),
        1 if round_name.lower().endswith(" replay") else 0,
        round_name.lower(),
        norm(row.get("home")),
        norm(row.get("away")),
    )


def involves(row, identity):
    return norm(row.get("home")) == identity or norm(row.get("away")) == identity


def is_replay(row):
    return "replay" in str(row.get("round") or "").lower()


def merge_row(existing, incoming):
    """Fill blank metadata without replacing already populated canonical values."""
    out = dict(existing)
    for key, value in incoming.items():
        if key not in out or out[key] in (None, "", [], {}):
            if value not in (None, "", [], {}):
                out[key] = copy.deepcopy(value)
    return out


def identity_groups(data):
    names = set((data.get("result_history") or {}).keys()) | set((data.get("results") or {}).keys())
    groups = {}
    for name in names:
        identity = norm(name)
        if identity:
            groups.setdefault(identity, []).append(name)
    return {identity: sorted(set(names)) for identity, names in groups.items() if len(set(names)) > 1}


def canonical_rows(data, identity, aliases):
    history = data.get("result_history") or {}
    latest = data.get("results") or {}
    rows = {}
    for alias in aliases:
        for row in history.get(alias, []) or []:
            if isinstance(row, dict) and involves(row, identity):
                key = semantic_key(row)
                rows[key] = merge_row(rows[key], row) if key in rows else copy.deepcopy(row)
        row = latest.get(alias)
        if isinstance(row, dict) and involves(row, identity):
            key = semantic_key(row)
            rows[key] = merge_row(rows[key], row) if key in rows else copy.deepcopy(row)
    return sorted(rows.values(), key=sort_key)


def check(data):
    history = data.get("result_history") or {}
    results = data.get("results") or {}
    failures = []
    checked = 0
    replay_rows = 0
    for identity, aliases in identity_groups(data).items():
        canonical = canonical_rows(data, identity, aliases)
        if not canonical or not any(is_replay(row) for row in canonical):
            continue
        canonical_keys = [semantic_key(row) for row in canonical]
        checked += 1
        replay_rows += sum(1 for row in canonical if is_replay(row))
        expected = set(canonical_keys)
        for alias in aliases:
            rows = [row for row in (history.get(alias, []) or []) if isinstance(row, dict) and involves(row, identity)]
            actual = {semantic_key(row) for row in rows}
            if actual != expected:
                missing = expected - actual
                extra = actual - expected
                failures.append(
                    f"{alias}: replay-participant chronology differs from identity '{identity}' "
                    f"(missing={len(missing)}, extra={len(extra)})"
                )
                continue
            current = results.get(alias)
            if not isinstance(current, dict) or semantic_key(current) != canonical_keys[-1]:
                failures.append(f"{alias}: latest results pointer does not match reconciled chronology")

    # Incident-specific fail-closed assertion. This is deliberately redundant with
    # the generic alias check so the exact HP7 failure can never become invisible.
    amersham_identity = norm("Amersham Town")
    amersham_groups = identity_groups(data).get(amersham_identity, [])
    for alias in amersham_groups:
        rows = history.get(alias, []) or []
        decisive = any(
            isinstance(row, dict)
            and str(row.get("round") or "").lower() == "extra preliminary round replay"
            and norm(row.get("home")) == amersham_identity
            and norm(row.get("away")) == norm("North Leigh")
            and score_int(row.get("home_score")) == 1
            and score_int(row.get("away_score")) == 2
            for row in rows
        )
        if not decisive:
            failures.append(f"{alias}: missing decisive Amersham Town 1-2 North Leigh replay")

    if failures:
        raise SystemExit("RESULT HISTORY ALIAS GUARD: FAIL\n" + "\n".join(f"- {item}" for item in failures[:50]))
    print("RESULT HISTORY ALIAS GUARD: PASS")
    print("Replay-participant alias groups checked:", checked)
    print("Replay rows protected across alias groups:", replay_rows)
    print("Amersham Town FC/bare/AFC decisive replay parity: PASS")


def repair(data):
    history = data.setdefault("result_history", {})
    results = data.setdefault("results", {})
    changed_aliases = []
    for identity, aliases in identity_groups(data).items():
        canonical = canonical_rows(data, identity, aliases)
        if not canonical or not any(is_replay(row) for row in canonical):
            continue
        canonical_keys = [semantic_key(row) for row in canonical]
        for alias in aliases:
            current_rows = [row for row in (history.get(alias, []) or []) if isinstance(row, dict) and involves(row, identity)]
            current_keys = [semantic_key(row) for row in sorted(current_rows, key=sort_key)]
            current_latest = results.get(alias)
            latest_ok = isinstance(current_latest, dict) and semantic_key(current_latest) == canonical_keys[-1]
            if current_keys != canonical_keys or not latest_ok:
                history[alias] = [copy.deepcopy(row) for row in canonical]
                results[alias] = copy.deepcopy(canonical[-1])
                changed_aliases.append(alias)
    return changed_aliases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="read-only fail-closed validation")
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    if args.check:
        check(data)
        return

    changed_aliases = repair(data)
    check(data)
    if changed_aliases:
        DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("RESULT HISTORY ALIAS RECONCILIATION: UPDATED")
        print("Alias buckets repaired:", len(changed_aliases))
        print("First repaired aliases:", ", ".join(changed_aliases[:20]))
    else:
        print("RESULT HISTORY ALIAS RECONCILIATION: NO CHANGE")


if __name__ == "__main__":
    main()
