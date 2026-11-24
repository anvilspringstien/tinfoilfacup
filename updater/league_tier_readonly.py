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
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "updater/league-tier-sources/fa-nls-steps-1-4-2026-27-initial.csv"
STEPS_5_6_SOURCE = SOURCE.with_name("fa-nls-steps-5-6-2026-27-initial.csv")
PREMIER_LEAGUE_SOURCE = SOURCE.with_name("premier-league-2026-27-membership.csv")
EFL_SOURCE = SOURCE.with_name("efl-2026-27-membership.csv")
DEFAULT_SOURCES = (SOURCE, STEPS_5_6_SOURCE, PREMIER_LEAGUE_SOURCE, EFL_SOURCE)
AMENDMENTS = SOURCE.with_name("nls-2026-27-post-may-evidence.csv")
ROSTER = ROOT / "tester-club-postcodes.csv"
COMPANION = ROOT / "journey-club-registry.json"
SEASON = "2026-27"
MEMBERSHIP = "official_season_membership"
AMENDMENT_PRIORITY = {"participation": 1, "constitution": 2, "allocation_decision": 3}
MATCH_STATUSES = {
    "matched_exact_initial", "matched_normalized_initial",
    "matched_exact_membership", "matched_normalized_membership",
    "matched_post_may",
}
REVIEW_EVIDENCE = {
    "missing_allocation": "Find a 2026–27 senior division listing and evidence linking the exact club identity.",
    "ambiguous_source": "Find a senior-team registration, venue or club identifier that separates the competing entries.",
    "provisional_ambiguous": "Find the final decision or a dated senior division registration resolving the provisional place.",
    "conflicting_amendments": "Find an official decision that resolves the competing later sources and states which applies.",
    "withdrawn_allocation": "Find an official replacement allocation for this senior team before proposing a tier.",
}

FIELDS = (
    "club", "population", "entry_round", "postcode", "match_status",
    "source_club", "source_fa_step", "proposed_tier", "approved_tier",
    "league", "division", "source_as_of", "source_url",
    "source_status", "review_note", "suggestions", "evidence_required",
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
                step = int(row["fa_step"]) if row.get("fa_step") else None
                tier = int(row["tier"]) if row.get("tier") else None
            except ValueError as e:
                raise ValueError(f"Invalid Tier or FA Step in {path}: {row}") from e
            club = (row.get("club") or "").strip()
            if not club:
                raise ValueError(f"Invalid source allocation: {row}")
            status = row.get("source_status", "")
            if status == MEMBERSHIP:
                if step is not None or tier not in range(1, 5) or row.get("season") != SEASON:
                    raise ValueError(f"Invalid season membership: {row}")
            elif status in {"official_initial_allocation", "provisional_ambiguous"}:
                if step not in range(1, 7) or (tier is not None and tier != step + 4):
                    raise ValueError(f"Invalid source allocation: {row}")
                tier = step + 4
            else:
                raise ValueError(f"Unknown source evidence status: {status}")
            if not row.get("source_url", "").startswith("https://"):
                raise ValueError(f"Source URL not HTTPS: {row}")
            if row.get("source_as_of", "")[:4] != "2026":
                raise ValueError(f"Source lacks 2026 season evidence: {row}")
            source_key = (key(club), tier, row["league"], row["division"])
            if source_key in seen:
                raise ValueError(f"Repeated source allocation: {club}")
            seen.add(source_key)
            row = dict(row, fa_step=step, tier=tier, club=club)
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
            data["review_note"] = "The initial FA allocation is conditional."
        elif len(matches) == 1:
            hit = matches[0]
            membership = hit["source_status"] == MEMBERSHIP
            match_kind = "exact" if name.casefold() == hit["club"].casefold() else "normalized"
            evidence_kind = "membership" if membership else "initial"
            data.update({
                "match_status": f"matched_{match_kind}_{evidence_kind}",
                "source_club": hit["club"],
                "source_fa_step": hit["fa_step"] if hit["fa_step"] is not None else "",
                "proposed_tier": hit["tier"],
                "league": hit["league"],
                "division": hit["division"],
                "source_as_of": hit["source_as_of"],
                "source_url": hit["source_url"],
                "source_status": hit["source_status"],
                "review_note": (
                    "Official season membership: check club identity before approval." if membership
                    else "Initial FA allocation: recheck amendments and club identity before approval."
                ),
            })
        elif len(matches) > 1:
            data["match_status"] = "ambiguous_source"
            data["review_note"] = "More than one official allocation has this normalized club name."
            suggestions = []
            for row in matches:
                step = row["fa_step"]
                level = f"Step {step}" if step is not None else f"Tier {row['tier']}"
                suggestions.append(f"{row['club']} ({level}, {row['league']} / {row['division']})")
            data["suggestions"] = " | ".join(suggestions)
        else:
            data["match_status"] = "missing_allocation"
            data["review_note"] = "No single senior allocation matches the club identity."
        if data["match_status"] in {"provisional_ambiguous", "missing_allocation"}:
            data["suggestions"] = " | ".join(
                definite[s][0]["club"] for s in difflib.get_close_matches(k, available, n=3, cutoff=0.72)
            )
        outputs.append(data)
    return outputs


def load_amendments(paths):
    by_club = defaultdict(list)
    for path in paths:
        for row in load_csv(path):
            try:
                published = date.fromisoformat(row["published_on"]) if row["published_on"] else None
                effective = date.fromisoformat(row["effective_on"]) if row["effective_on"] else None
                observed = date.fromisoformat(row["observed_on"])
                step = int(row["fa_step"]) if row["fa_step"] else None
            except (KeyError, ValueError) as error:
                raise ValueError(f"Invalid post-May evidence in {path}: {row}") from error
            status = row["action"]
            if (
                row["season"] != SEASON or observed <= date(2026, 5, 14)
                or (published and not date(2026, 5, 14) < published <= observed)
                or row["authority"] not in AMENDMENT_PRIORITY
                or not all(row[name].strip() for name in ("club", "source_club", "note"))
                or not row["source_url"].startswith("https://")
                or (row["identity_url"] and not row["identity_url"].startswith("https://"))
                or status not in {"allocate", "withdraw"}
                or (status == "allocate" and (step not in range(1, 7) or not row["league"] or not row["division"]))
                or (status == "withdraw" and (step is not None or row["league"] or row["division"]))
            ):
                raise ValueError(f"Invalid post-May evidence in {path}: {row}")
            by_club[row["club"]].append(dict(
                row, fa_step=step, source_as_of=(published or observed).isoformat(),
                available_on=max(published or observed, effective or date.min),
            ))
    return by_club


def apply_amendments(row, evidence, as_of):
    eligible = [item for item in evidence if item["available_on"] <= as_of]
    if not eligible:
        return row
    priority = max(AMENDMENT_PRIORITY[item["authority"]] for item in eligible)
    strongest = sorted(
        (item for item in eligible if AMENDMENT_PRIORITY[item["authority"]] == priority),
        key=lambda item: (item["source_as_of"], item["source_url"], item["source_club"], item["note"]),
        reverse=True,
    )
    outcomes = {(item["action"], item["fa_step"], item["league"], item["division"]) for item in strongest}
    hit = strongest[0]
    result = dict(
        row, source_fa_step="", proposed_tier="", league="", division="", source_club=hit["source_club"],
        source_as_of=hit["source_as_of"], source_url=hit["source_url"], source_status=hit["authority"],
        review_note=hit["note"], suggestions="",
    )
    if row.get("source_status") == MEMBERSHIP:
        result.update(
            match_status="conflicting_amendments",
            source_club=f"{row['source_club']} | {hit['source_club']}",
            source_url=f"{row['source_url']} | {hit['source_url']}",
            review_note="Professional membership and later NLS evidence conflict for this identity.",
        )
    elif len(outcomes) > 1:
        result.update(
            match_status="conflicting_amendments",
            source_club=" | ".join(sorted({item["source_club"] for item in strongest})),
            source_url=" | ".join(sorted({item["source_url"] for item in strongest})),
            review_note="Equally authoritative post-May sources disagree about the senior allocation.",
            suggestions=" | ".join(sorted({item["note"] for item in strongest})),
        )
    elif hit["action"] == "withdraw":
        result["match_status"] = "withdrawn_allocation"
    else:
        step = hit["fa_step"]
        result.update(match_status="matched_post_may", source_fa_step=step, proposed_tier=step + 4,
                      league=hit["league"], division=hit["division"])
    return result


def build_audit(roster=ROSTER, companion=COMPANION, source_paths=None, amendment_paths=None, as_of=None):
    sources = DEFAULT_SOURCES if source_paths is None else [Path(s) for s in source_paths]
    if amendment_paths is None:
        amendment_paths = [AMENDMENTS] if source_paths is None else []
    amendments = load_amendments(Path(path) for path in amendment_paths)
    as_of = date.today() if as_of is None else as_of
    population, original_count = load_population(Path(roster), Path(companion))
    definite, provisional, source_counts = load_allocations(sources)
    baseline = match_population(population, definite, provisional)
    rows = []
    changes = []
    for before in baseline:
        row = apply_amendments(before, amendments.get(before["club"], []), as_of)
        row["evidence_required"] = REVIEW_EVIDENCE.get(row["match_status"], "")
        rows.append(row)
        if any(before[field] != row[field] for field in ("match_status", "league", "division", "proposed_tier")):
            changes.append({
                "club": row["club"], "population": row["population"],
                "before": {field: before[field] for field in ("match_status", "league", "division", "proposed_tier")},
                "after": {field: row[field] for field in ("match_status", "league", "division", "proposed_tier")},
                "source_url": row["source_url"],
            })
    evidence = [row for matches in definite.values() for row in matches] + provisional
    step_counts = Counter(row["fa_step"] for row in evidence if row["fa_step"] is not None)
    membership_counts = Counter(row["tier"] for row in evidence if row["source_status"] == MEMBERSHIP)
    status = Counter(row["match_status"] for row in rows)
    originals = Counter(row["match_status"] for row in rows if row["population"] == "original-clubfinder")
    companions = status - originals
    return rows, {
        "schema_version": 2, "season": SEASON, "read_only": True,
        "public_promotion": False, "giant_killer_awards_enabled": False,
        "as_of": as_of.isoformat(),
        "source_scope": "Professional season membership, initial FA NLS allocations and sourced post-May evidence",
        "post_may_evidence_rows": sum(len(items) for items in amendments.values()),
        "changes_from_baseline": changes,
        "initial_fa_rows_by_step": {str(step): step_counts[step] for step in sorted(step_counts)},
        "season_membership_rows_by_tier": {str(tier): membership_counts[tier] for tier in sorted(membership_counts)},
        "original_clubfinder_clubs": original_count,
        "companion_only_clubs": len(rows) - original_count,
        "total_distinct_clubs": len(rows),
        "initial_fa_source_rows": sum(step_counts.values()),
        "season_membership_source_rows": sum(membership_counts.values()),
        "source_evidence_status": source_counts,
        "original_match_status": dict(sorted(originals.items())),
        "companion_match_status": dict(sorted(companions.items())),
        "all_match_status": dict(sorted(status.items())),
        "historical_preliminary_15_november": {
            "matched": 629, "exceptions": 22,
            "qualification": "Historical tally; the original matching table was not retained."
        },
    }


def write_audit(rows, metadata, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    # Only writes generated diagnostics to the explicit output directory.
    with (out / "league-tier-candidates-2026-27.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    waiting = [r for r in rows if r["match_status"] not in MATCH_STATUSES]
    with (out / "league-tier-review-queue-2026-27.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(waiting)
    exception_report = ["# Clubfinder and Journey allocation exceptions (2026–27)", ""]
    for row in waiting:
        exception_report += [
            f"## {row['club']}", "",
            f"- Population — {row['population']}",
            f"- Reason — {row['review_note']}",
            f"- Evidence required — {row.get('evidence_required') or REVIEW_EVIDENCE[row['match_status']]}",
        ]
        if row["suggestions"]:
            exception_report.append(f"- Unresolved leads — {row['suggestions']}")
        if row["source_url"]:
            links = row["source_url"].split(" | ")
            exception_report.append("- Evidence — " + ", ".join(f"<{link}>" for link in links))
        exception_report.append("")
    if not waiting:
        exception_report += ["No unresolved clubs in the audited populations at this date.", ""]
    resolved = sorted(
        (change for change in metadata.get("changes_from_baseline", [])
         if change["before"]["match_status"] not in MATCH_STATUSES
         and change["after"]["match_status"] in MATCH_STATUSES),
        key=lambda change: change["club"].casefold(),
    )
    if resolved:
        exception_report += ["## Earlier exceptions with a candidate in this pass", ""]
        for change in resolved:
            after = change["after"]
            exception_report.append(
                f"- **{change['club']}** — proposed Tier {after['proposed_tier']}, "
                f"{after['league']} / {after['division']}. <{change['source_url']}>"
            )
        exception_report.append("")
    (out / "league-tier-exceptions-2026-27.md").write_text("\n".join(exception_report), encoding="utf-8")
    (out / "league-tier-audit-summary-2026-27.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    summary = [
        "# Tin Foil FA Cup — League & Tier read-only audit (2026–27)",
        "", "**NOT APPROVED FOR PUBLICATION. GIANT KILLER DISABLED.**", "",
        "Source: FA initial NLS allocations dated 14 May 2026; explicitly subject to later amendments.",
        f"Imported FA Steps: {', '.join(metadata.get('initial_fa_rows_by_step', {})) or 'none'}.",
        f"Imported official season membership Tiers: {', '.join(metadata.get('season_membership_rows_by_tier', {})) or 'none'}.",
        f"Post-May evidence rows: {metadata.get('post_may_evidence_rows', 0)}.",
        "", f"Original Clubfinder clubs: **{metadata['original_clubfinder_clubs']}**",
        f"Companion-only entries: **{metadata['companion_only_clubs']}**", "",
        "## Current status (original Clubfinder population)", "",
    ]
    for k, v in sorted(metadata["original_match_status"].items()):
        summary.append(f"- {k}: {v}")
    summary += ["", "## Current status (companion-only Journey population)", ""]
    for k, v in sorted(metadata.get("companion_match_status", {}).items()):
        summary.append(f"- {k}: {v}")
    summary += ["", f"## Unclassified or ambiguous: {len(waiting)} across both populations",
                "", "Every matched Tier is a *proposed* Tier. Approved Tier is intentionally blank.",
                "Historical reference: 629/651 reported, with no original matching table retained.",
                "The named exception report lists the evidence needed for each outstanding club.",
                ""]
    (out / "league-tier-audit-2026-27.md").write_text("\n".join(summary), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--roster", type=Path, default=ROSTER)
    p.add_argument("--companion", type=Path, default=COMPANION)
    p.add_argument("--source", action="append", type=Path, default=None,
                   help="Override the default source ledgers with the supplied evidence CSVs")
    p.add_argument("--amendment", action="append", type=Path,
                   help="Post-May evidence CSV; custom --source runs omit amendments unless supplied")
    p.add_argument("--as-of", type=date.fromisoformat, help="Use evidence available by this date (YYYY-MM-DD)")
    p.add_argument("--out", type=Path, required=True,
                   help="Explicit directory for read-only report artifacts")
    args = p.parse_args()
    rows, metadata = build_audit(args.roster, args.companion, args.source, args.amendment, args.as_of)
    write_audit(rows, metadata, args.out)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
