"""Retain source-attributed schedule metadata for the exact played match.

Originals and replays never share metadata merely because the clubs match.
Missing/TBC values may be filled; contradictory populated values fail closed.
"""
from copy import deepcopy
import re

from round_state_engine import norm


def records(value):
    if isinstance(value, dict):
        if value.get("home") and value.get("away"):
            yield value
        else:
            for child in value.values():
                yield from records(child)
    elif isinstance(value, list):
        for child in value:
            yield from records(child)


def identity(row):
    return (norm(row.get("home")), norm(row.get("away")),
            str(row.get("date") or ""), str(row.get("round") or "").casefold())


def known(value):
    return value not in (None, "", {}, []) and "tbc" not in str(value).casefold()


def retain_metadata(result, candidates):
    out = deepcopy(result)
    if not result.get("date") or not result.get("round"):
        return out
    exact = candidates.get(identity(result), []) if isinstance(candidates, dict) else [
        r for r in candidates if identity(r) == identity(result)]
    for key, source_key in (("kickoff", "kickoff_source_url"), ("venue", "venue_source_url")):
        found = []
        for row in [result, *exact]:
            value = row.get(key)
            if not known(value):
                continue
            if key == "kickoff" and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(value)):
                continue
            source = row.get(source_key) or (value.get("source") if isinstance(value, dict) else None) or row.get("source_url")
            if not source:
                continue
            if found:
                previous = found[0][0]
                fields = ("ground", "postcode") if key == "venue" else ()
                conflict = any(known(previous.get(k)) and known(value.get(k)) and previous[k] != value[k]
                               for k in fields) if fields else previous != value
                if conflict:
                    raise ValueError(f"conflicting {key} evidence for {identity(result)}")
            found.append((value, source))
        if found and not known(out.get(key)):
            out[key], out[source_key] = deepcopy(found[0][0]), found[0][1]
    return out


def metadata_candidates(data):
    out = {}
    for row in records({k: data.get(k) for k in
                        ("fixtures", "replays", "round_fixtures", "results", "result_history")}):
        out.setdefault(identity(row), []).append(row)
    return out


def preserve_result_metadata(data):
    candidates = metadata_candidates(data)
    changed = 0
    for row in records({k: data.get(k) for k in ("results", "result_history")}):
        enriched = retain_metadata(row, candidates)
        if enriched != row:
            row.update(enriched)
            changed += 1
    return changed
