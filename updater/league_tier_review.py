"""Review League & Tier candidates and cup-date evidence without approving tiers."""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from updater.league_tier_readonly import (
    AMENDMENTS, DEFAULT_SOURCES, MATCH_STATUSES, MEMBERSHIP, ROOT, SEASON,
    build_audit, key, load_allocations, load_amendments,
)

COMPETITION = ROOT / "competition.json"
PREMIER_LEAGUE_START = date(2026, 6, 5)
PREMIER_LEAGUE_START_URL = "https://www.premierleague.com/en/news/4673099/the-202627-premier-league-season-officially-starts/"
MK_DONS_IDENTITY_URL = "https://www.mkdons.com/news/2026/may/02/league-one-awaits/"
PROFESSIONAL_TIERS = {
    ("Premier League", "Premier League"): 1,
    ("English Football League", "Championship"): 2,
    ("English Football League", "League One"): 3,
    ("English Football League", "League Two"): 4,
}
FINISHED_STATUSES = {"ft", "ft (aet)", "aet"}


def spelling(name):
    """Remove case and a terminal club suffix, preserving the rest of the spelling."""
    return re.sub(r"\s+(?:fc|afc)$", "", name.strip().casefold())


def match_method(row):
    if row["match_status"] not in MATCH_STATUSES:
        return "unresolved"
    if row["match_status"] == "matched_post_may":
        return "documented_identity"
    if row["source_status"] == MEMBERSHIP and row["source_club"] == "Milton Keynes Dons":
        return "documented_publisher_alias"
    if row["club"].casefold() == row["source_club"].casefold():
        return "exact"
    if spelling(row["club"]) == spelling(row["source_club"]):
        return "suffix_only"
    return "spelling_normalization"


def cup_observations(competition, rows, as_of):
    """Index scored results and flag inconsistent dates without choosing one."""
    if competition["season"] != SEASON:
        raise ValueError("Cup and membership seasons differ")
    labels = defaultdict(set)
    for row in rows:
        for label in (row["club"], row["source_club"]):
            if label:
                labels[key(label)].add(row["club"])
    observations = defaultdict(set)
    unmatched = set()
    results = list(competition["results"].values())
    for history in competition["result_history"].values():
        results.extend(history)
    for tie in results:
        if (tie.get("status", "").strip().casefold() not in FINISHED_STATUSES
                or any(type(tie.get(field)) is not int for field in ("home_score", "away_score"))
                or not all(tie.get(field) for field in ("round", "home", "away", "date"))):
            continue
        played = date.fromisoformat(tie["date"])
        if played <= as_of:
            observations[tie["round"], key(tie["home"]), key(tie["away"])].add(played)
            unmatched.update(tie[side] for side in ("home", "away") if not labels.get(key(tie[side])))
    played_dates = defaultdict(set)
    identity_holds = defaultdict(set)
    date_holds = defaultdict(set)
    for (round_name, home, away), dates in observations.items():
        sides = f"{round_name}: {home} v {away}"
        for team in (home, away):
            identities = labels[team]
            for name in sorted(identities):
                if len(identities) > 1:
                    identity_holds[name].add(sides)
                elif len(dates) > 1:
                    date_holds[name].add(f"{sides} ({', '.join(d.isoformat() for d in sorted(dates))})")
                else:
                    played_dates[name].update(dates)
    return played_dates, identity_holds, date_holds, sorted(unmatched, key=str.casefold)


def validate_candidate(row, baseline, amendments, step_by_division, as_of):
    """Verify the proposed tuple against source evidence and pyramid structure."""
    if row["approved_tier"]:
        raise ValueError(f"Approved Tier present in review input: {row['club']}")
    if row["match_status"] not in MATCH_STATUSES:
        if row["proposed_tier"]:
            raise ValueError(f"Unresolved row carries a proposed Tier: {row['club']}")
        return None
    club, source = row["club"], row["source_status"]
    step, tier = row["source_fa_step"], row["proposed_tier"]
    league_division = row["league"], row["division"]
    url = urlsplit(row["source_url"])
    if url.scheme != "https" or not url.hostname or date.fromisoformat(row["source_as_of"]) > as_of:
        raise ValueError(f"Invalid source provenance: {club}")
    if source == MEMBERSHIP:
        expected_domain = "www.premierleague.com" if tier == 1 else "www.efl.com"
        if step != "" or PROFESSIONAL_TIERS.get(league_division) != tier or url.hostname != expected_domain:
            raise ValueError(f"Professional division/Tier mismatch: {club}")
    elif type(step) is not int or step_by_division.get(league_division) != step or tier != step + 4:
        raise ValueError(f"NLS division/Step/Tier mismatch: {club}")
    if row["match_status"] == "matched_post_may":
        claim = next((item for item in amendments.get(club, [])
                      if item["action"] == "allocate" and item["available_on"] <= as_of
                      and item["authority"] == source and item["source_url"] == row["source_url"]
                      and item["source_club"] == row["source_club"] and item["fa_step"] == step
                      and (item["league"], item["division"]) == league_division), None)
        if claim is None:
            raise ValueError(f"Missing exact post-May evidence: {club}")
        return claim
    claims = baseline[key(club)]
    if (len(claims) != 1 or claims[0]["club"] != row["source_club"]
            or claims[0]["source_url"] != row["source_url"]
            or claims[0]["source_status"] != source
            or claims[0]["source_as_of"] != row["source_as_of"]
            or claims[0]["tier"] != tier
            or (claims[0]["league"], claims[0]["division"]) != league_division):
        raise ValueError(f"Candidate does not match its unique source row: {club}")
    if source != MEMBERSHIP and (url.hostname != "www.thefa.com" or "/2026-27/" not in url.path):
        raise ValueError(f"Initial source is not the season-specific FA allocation: {club}")
    return None


def review(competition, as_of):
    rows, metadata = build_audit(as_of=as_of)
    baseline, provisional, _ = load_allocations(DEFAULT_SOURCES)
    claims = [row for matches in baseline.values() for row in matches] + provisional
    step_by_division = {}
    for row in claims:
        if row["fa_step"] is not None:
            division = row["league"], row["division"]
            if step_by_division.setdefault(division, row["fa_step"]) != row["fa_step"]:
                raise ValueError(f"Conflicting source Steps for {division}")
    amendments = load_amendments([AMENDMENTS])
    dates, alias_holds, date_holds, unmatched = cup_observations(competition, rows, as_of)
    decisions = {change["club"]: change for change in metadata["changes_from_baseline"]}
    report = []
    for row in rows:
        amendment = validate_candidate(row, baseline, amendments, step_by_division, as_of)
        name, source = row["club"], row["source_status"]
        method = match_method(row)
        date_source = ""
        documented_start = None
        if amendment and amendment["effective_on"]:
            documented_start = date.fromisoformat(amendment["effective_on"])
            date_source = amendment["source_url"]
        elif source == MEMBERSHIP and row["proposed_tier"] == 1:
            documented_start = PREMIER_LEAGUE_START
            date_source = PREMIER_LEAGUE_START_URL
        played = dates[name]
        checks = []
        if method == "unresolved":
            checks.append(row["evidence_required"])
        elif method == "documented_identity":
            checks.append("Review the named post-May evidence and its identity link.")
        elif method in {"documented_publisher_alias", "spelling_normalization"}:
            checks.append("Verify the source spelling and senior club identity on the approval record.")
        if source == "official_initial_allocation":
            checks.append("Obtain a final constitution or current official season membership for this initial allocation.")
        if alias_holds[name]:
            checks.append("Resolve the cup participant identity before assigning a tie-time Tier.")
        if date_holds[name]:
            checks.append("Resolve conflicting cup dates before assigning a tie-time Tier.")
        if played and (not documented_start or min(played) < documented_start):
            checks.append("Obtain dated league evidence covering the earliest scored cup result.")
        if played and documented_start and min(played) >= documented_start:
            checks.append("Confirm membership still applied on the tie dates before approving a dated interval.")
        phase3_prior = decisions.get(name, {}).get("before", {}).get("match_status", "")
        report.append({
            **{field: row[field] for field in (
                "club", "population", "match_status", "league", "division", "source_fa_step",
                "proposed_tier", "approved_tier", "source_club", "source_status", "source_url", "source_as_of",
            )},
            "matching_method": method,
            "identity_url": (amendment["identity_url"] if amendment else
                             MK_DONS_IDENTITY_URL if method == "documented_publisher_alias" else ""),
            "prior_match_status": phase3_prior,
            "evidence_note": row["review_note"],
            "documented_membership_start": documented_start.isoformat() if documented_start else "",
            "membership_start_source": date_source,
            "first_scored_cup_date": min(played).isoformat() if played else "",
            "last_scored_cup_date": max(played).isoformat() if played else "",
            "cup_identity_holds": " | ".join(sorted(alias_holds[name])),
            "cup_date_holds": " | ".join(sorted(date_holds[name])),
            "individual_membership_review": method in {
                "documented_identity", "documented_publisher_alias", "spelling_normalization", "unresolved",
            },
            "review_required": " ".join(checks),
        })
    return report, unmatched


def write_review(rows, unmatched, as_of, out):
    out.mkdir(parents=True, exist_ok=True)
    with (out / "league-tier-readiness-2026-27.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    groups = Counter((row["source_status"], row["matching_method"]) for row in rows)
    report = [
        "# League & Tier approval readiness (2026–27)", "", f"Evidence cut-off: {as_of.isoformat()}.", "",
        "| Source evidence | Match method | Clubs |", "| --- | --- | ---: |",
    ]
    for (source, method), count in sorted(groups.items()):
        report.append(f"| {source} | {method} | {count} |")
    report += [
        "", "## Tie-date evidence", "",
        f"- Clubs with an unambiguous dated scored cup result: {sum(bool(r['first_scored_cup_date']) for r in rows)}.",
        f"- Those clubs with a documented membership start: {sum(bool(r['first_scored_cup_date'] and r['documented_membership_start']) for r in rows)}.",
        f"- Clubs with a conflicting cup date: {sum(bool(r['cup_date_holds']) for r in rows)}.",
        f"- Clubs with a competing cup identity: {sum(bool(r['cup_identity_holds']) for r in rows)}.",
        f"- Scored-result labels without an audit identity link: {len(unmatched)}.",
        "- A documented start alone does not establish a reviewed membership interval through the tie date.",
        "- The comparison uses scored results as date leads and does not infer membership from cup participation.",
        "", "## Named cases for individual review", "",
    ]
    for row in rows:
        if row["individual_membership_review"] or row["cup_identity_holds"] or row["cup_date_holds"]:
            evidence = f" <{row['source_url']}>" if row["source_url"] else ""
            report.append(f"- **{row['club']}** — {row['review_required']}{evidence}")
            for field in ("cup_identity_holds", "cup_date_holds"):
                if row[field]:
                    report.append(f"  - {row[field]}")
    if unmatched:
        report += ["", "## Unlinked scored-result labels", "", *[f"- {name}" for name in unmatched]]
    (out / "league-tier-readiness-2026-27.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--competition", type=Path, default=COMPETITION)
    parser.add_argument("--as-of", type=date.fromisoformat, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    competition = json.loads(args.competition.read_text(encoding="utf-8"))
    rows, unmatched = review(competition, args.as_of)
    write_review(rows, unmatched, args.as_of, args.out)


if __name__ == "__main__":
    main()
