#!/usr/bin/env python3
"""Read-only, season-scoped League & Tier candidate audit.

Never modifies Clubfinder, Public, BETA, competition.json, a saved Campaign,
Mission Control, or Challenge records. All source classifications remain
unapproved until separate review. Output is explicitly opt-in under --out.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "updater/league-tier-sources/fa-nls-steps-1-4-2026-27-initial.csv"
STEPS_5_6_SOURCE = SOURCE.with_name("fa-nls-steps-5-6-2026-27-initial.csv")
ROSTER = ROOT / "tester-club-postcodes.csv"
COMPANION = ROOT / "journey-club-registry.json"
SEASON = "2026-27"

FIELDS = (
    "club", "population", "entry_round", "postcode", "match_status",
    "source_club", "source_fa_step", "proposed_tier", "approved_tier",
    "league", "division", "source_as_of", "source_url",
    "source_status", "review_note", "suggestions",
)


def key(name: str) -> str:
    """Only conservative *trailing* FC/AFC contractions, never leading AFC."""
    name = unicodedata.normalize("NFKD", str(name or ""))
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.casefold().replace("&", " and ")
    name = re.sub(r"\bf[.]c[.]\b", "fc", name)
    name = re.sub(r"[^a-z0-9]+", " ", name).strip()
    name = re.sub(r"\s+(?:fc|afc)$", "", name)
    return " ".join(name.split())


def load_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_population(roster: Path = ROSTER, companion: Path = COMPANION):
    original = load_csv(roster)
    if not original or len({row["Club"] for row in original}) != len(original):
        raise ValueError("Missing or duplicate original Clubfinder names")
    population = []
    norm_used = defaultdict(list)
    for row in original:
        name = row["Club"].strip()
        if not name:
            raise ValueError("Empty Clubfinder identity")
        item = {"club": name, "population": "original-clubfinder",
                "entry_round": row.get("Entry Round", ""),
                "postcode": row.get("Postcode", "")}
        population.append(item)
        norm_used[key(name)].append(item)
    companion_data = json.loads(companion.read_text(encoding="utf-8"))
    if companion_data.get("season") != SEASON:
        raise ValueError("Companion registry season is not 2026-27")
    for entry in companion_data.get("clubs", []):
        name = entry.get("club", "").strip()
        if not name:
            raise ValueError("Empty companion club identity")
        match = norm_used.get(key(name), [])
        if match:
            # Preserve the original population entry and never duplicate its
            # classification; aliases remain a review matter.
            continue
        item = {"club": name, "population": "companion-journey-registry",
                "entry_round": entry.get("entry_round") or "", "postcode": ""}
        population.append(item)
        norm_used[key(name)].append(item)
    return population, len(original)


def load_allocations(paths):
    definite = defaultdict(list)
    provisional = []
    seen = set()
    source_counts = Counter()
    for path in paths:
        for row in load_csv(path):
            try:
                step = int(row["fa_step"])
            except (TypeError, KeyError, ValueError) as e:
                raise ValueError(f"Invalid FA Step in {path}: {row}") from e
            if not 1 <= step <= 6 or not row.get("club", "").strip():
                raise ValueError(f"Invalid source allocation: {row}")
            status = row.get("source_status", "")
            if status not in {"official_initial_allocation", "provisional_ambiguous"}:
                raise ValueError(f"Unknown source evidence status: {status}")
            if not row.get("source_url", "").startswith("https://"):
                raise ValueError(f"Source URL not HTTPS: {row}")
            if row.get("source_as_of", "")[:4] != "2026":
                raise ValueError(f"Source lacks 2026 season evidence: {row}")
            club = row["club"].strip()
            source_key = (key(club), str(step), row["league"], row["division"])
            if source_key in seen:
                raise ValueError(f"Repeated source allocation: {club}")
            seen.add(source_key)
            row = dict(row, fa_step=step, club=club)
            source_counts[status] += 1
            if status == "provisional_ambiguous":
                provisional.append(row)
            else:
                definite[key(club)].append(row)
    return definite, provisional, dict(source_counts)


def match_population(population, definite, provisional):
    outputs = []
    available = sorted(definite)
    pending = defaultdict(list)
    for row in provisional:
        for name in row["club"].split(" or "):
            pending[key(name)].append(row)
    for club in population:
        name = club["club"]
        k = key(name)
        matches = definite.get(k, [])
        data = dict.fromkeys(FIELDS, "")
        data.update(club)
        data["approved_tier"] = ""  # never approved automatically
        unresolved = pending.get(k, [])
        if unresolved:
            data["match_status"] = "provisional_ambiguous"
            data["source_club"] = " | ".join(dict.fromkeys(r["club"] for r in unresolved))
            data["source_url"] = " | ".join(dict.fromkeys(r["source_url"] for r in unresolved))
            data["source_status"] = "provisional_ambiguous"
            data["review_note"] = "Initial FA allocation is conditional; check later league evidence."
        elif len(matches) == 1:
            hit = matches[0]
            data.update({
                "match_status": ("matched_exact_initial" if
                                 name.casefold() == hit["club"].casefold()
                                 else "matched_normalized_initial"),
                "source_club": hit["club"],
                "source_fa_step": hit["fa_step"],
                "proposed_tier": hit["fa_step"] + 4,
                "league": hit["league"],
                "division": hit["division"],
                "source_as_of": hit["source_as_of"],
                "source_url": hit["source_url"],
                "source_status": hit["source_status"],
                "review_note": "Initial FA allocation: recheck amendments and club identity before approval.",
            })
        elif len(matches) > 1:
            data["match_status"] = "ambiguous_source"
            data["review_note"] = "More than one official allocation has this normalized club name."
            data["suggestions"] = " | ".join(
                f"{row['club']} (Step {row['fa_step']}, {row['league']} / {row['division']})"
                for row in matches
            )
        else:
            data["match_status"] = "missing_allocation"
            data["review_note"] = "Check season membership, amendments and club aliases."
        if data["match_status"] in {"provisional_ambiguous", "missing_allocation"}:
            data["suggestions"] = " | ".join(
                definite[s][0]["club"] for s in difflib.get_close_matches(k, available, n=3, cutoff=0.72)
            )
        outputs.append(data)
    return outputs


def build_audit(roster=ROSTER, companion=COMPANION, source_paths=None):
    sources = [SOURCE, STEPS_5_6_SOURCE] if source_paths is None else [Path(s) for s in source_paths]
    population, original_count = load_population(Path(roster), Path(companion))
    definite, provisional, source_counts = load_allocations(sources)
    rows = match_population(population, definite, provisional)
    step_counts = Counter(row["fa_step"] for matches in definite.values() for row in matches)
    step_counts.update(row["fa_step"] for row in provisional)
    status = Counter(row["match_status"] for row in rows)
    originals = Counter(row["match_status"] for row in rows if row["population"] == "original-clubfinder")
    return rows, {
        "schema_version": 1, "season": SEASON, "read_only": True,
        "public_promotion": False, "giant_killer_awards_enabled": False,
        "source_scope": "Initial FA NLS allocations; PL/EFL and amendments outside this audit",
        "initial_fa_rows_by_step": {str(step): step_counts[step] for step in sorted(step_counts)},
        "original_clubfinder_clubs": original_count,
        "companion_only_clubs": len(rows) - original_count,
        "total_distinct_clubs": len(rows),
        "initial_fa_source_rows": sum(source_counts.values()),
        "source_evidence_status": source_counts,
        "original_match_status": dict(sorted(originals.items())),
        "all_match_status": dict(sorted(status.items())),
        "historical_preliminary_15_november": {
            "matched": 629, "exceptions": 22,
            "qualification": "Historical result only; source table not retained. Not a benchmark of this partial-source audit."
        },
    }


def write_audit(rows, metadata, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    # Only writes generated diagnostics to the explicit output directory.
    with (out / "league-tier-candidates-2026-27.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    waiting = [r for r in rows if r["match_status"] not in {"matched_exact_initial", "matched_normalized_initial"}]
    with (out / "league-tier-review-queue-2026-27.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(waiting)
    (out / "league-tier-audit-summary-2026-27.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    summary = [
        "# Tin Foil FA Cup — League & Tier read-only audit (2026–27)",
        "", "**NOT APPROVED FOR PUBLICATION. GIANT KILLER DISABLED.**", "",
        "Source: FA initial NLS allocations dated 14 May 2026; explicitly subject to later amendments.",
        f"Imported FA Steps: {', '.join(metadata.get('initial_fa_rows_by_step', {})) or 'none'}.",
        "", f"Original Clubfinder clubs: **{metadata['original_clubfinder_clubs']}**",
        f"Companion-only entries: **{metadata['companion_only_clubs']}**", "",
        "## Current status (original Clubfinder population)", "",
    ]
    for k, v in sorted(metadata["original_match_status"].items()):
        summary.append(f"- {k}: {v}")
    summary += ["", f"## Unclassified or ambiguous: {len(waiting)} across both populations",
                "", "Every matched Tier is a *proposed* Tier. Approved Tier is intentionally blank.",
                "The historical 629/651 tally has not been reproduced and must not be presented as current.",
                "Further evidence required: 2026–27 Premier League/EFL membership and subsequent league amendments.",
                ""]
    (out / "league-tier-audit-2026-27.md").write_text("\n".join(summary), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--roster", type=Path, default=ROSTER)
    p.add_argument("--companion", type=Path, default=COMPANION)
    p.add_argument("--source", action="append", type=Path, default=None,
                   help="Override the default FA Steps 1–6 CSVs with the supplied allocation CSVs")
    p.add_argument("--out", type=Path, required=True,
                   help="Explicit directory for read-only report artifacts")
    args = p.parse_args()
    rows, metadata = build_audit(args.roster, args.companion, args.source)
    write_audit(rows, metadata, args.out)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
