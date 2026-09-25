#!/usr/bin/env python3
"""Generate a read-only dependency map from COMPLETE BETA sources.

The report is an investigative index, not a dead-code proof. It records
explicit reference forms and marks unresolved dynamic dependencies. Never
rewrites app HTML, competition data, or saved-user data.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/refactor/2026-09-25-dependency-map.md"
PATHS = {
    "Deck": "beta/challenges-beta.html",
    "Clubfinder": "beta/clubfinder-beta.html",
}
BEGIN = "/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
END = "/* TIN_FOIL_EMBEDDED_COMPETITION_END */"
TICK = chr(96)


def code(value):
    return TICK + str(value) + TICK


def fingerprint(raw):
    return hashlib.sha256(raw).hexdigest()


def mask_embedded(html):
    if html.count(BEGIN) != 1 or html.count(END) != 1:
        raise ValueError("Missing or duplicated BETA competition payload markers")
    start = html.index(BEGIN)
    end = html.index(END, start) + len(END)
    removed = html[start:end]
    # Preserve original line numbers, even when the embedded payload is huge.
    replacement = "/* canonical offline payload masked for structural scan */"
    return html[:start] + replacement + "\n" * removed.count("\n") + html[end:]


def analyse(label, path):
    raw = (ROOT / path).read_bytes()
    html = raw.decode("utf-8")
    scan = mask_embedded(html) if label == "Clubfinder" else html
    css = "\n".join(re.findall(r"<style\b[^>]*>(.*?)</style>", scan, re.I | re.S))
    js = "\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>", scan, re.I | re.S))
    markup = re.sub(r"<(?:style|script)\b[^>]*>.*?</(?:style|script)>",
                    "", scan, flags=re.I | re.S)
    functions = sorted(set(re.findall(
        r"\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", js
    )))
    # A presence count is deliberately conservative: callbacks and bracket
    # lookups do not necessarily appear as direct function-call expressions.
    function_edges = {}
    for name in functions:
        tok = r"\b" + re.escape(name) + r"\b"
        function_edges[name] = {
            "token_occurrences": len(re.findall(tok, js)),
            "call_syntax_occurrences": len(re.findall(tok + r"\s*\(", js)),
        }
    aliases = {}
    for m in re.finditer(
        r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(['\"])([^'\"\n]{1,110})\2",
        js
    ):
        aliases[m.group(1)] = m.group(3)
    storage = []
    for m in re.finditer(
        r"\b(localStorage|sessionStorage)\s*\.\s*(getItem|setItem|removeItem)"
        r"\s*\(\s*(?:(['\"])([^'\"\n]{1,110})\3|([A-Za-z_$][\w$]*))",
        js
    ):
        raw_key = m.group(4) or m.group(5)
        key = aliases.get(raw_key, raw_key)
        storage.append({
            "store": m.group(1), "op": m.group(2), "key": key,
            "key_expression": raw_key,
        })
    # Selectors present in CSS, but absent as whole textual tokens from
    # HTML markup and inline JS. These MAY be dynamically generated.
    css_classes = sorted(set(re.findall(r"(?<![\w-])\.([A-Za-z][\w-]*)", css)))
    markup_tokens = set(re.findall(r"[A-Za-z][\w-]*", markup))
    script_tokens = set(re.findall(r"[A-Za-z][\w-]*", js))
    orphan_candidates = [
        c for c in css_classes if c not in markup_tokens and c not in script_tokens
    ]
    return {
        "label": label, "path": path, "raw": raw, "html": html, "scan": scan,
        "css": css, "js": js, "functions": functions, "edges": function_edges,
        "storage": storage, "aliases": aliases, "orphan_candidates": orphan_candidates,
        "css_class_count": len(css_classes),
    }


def line_of(text, needle):
    i = text.find(needle)
    return text.count("\n", 0, i) + 1 if i >= 0 else None


def evidence_summary(text, names):
    rows = []
    for name in names:
        match = re.search(r"\bfunction\s+" + re.escape(name) + r"\s*\(", text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            rows.append(code(name) + " (line " + str(line) + ")")
    return ", ".join(rows) or "Not found as a named declaration; inspect manually."


def storage_table(deck, cf):
    keys = [
        "tffc.challengeDeck.v1", "tffc.clubfinderCampaign.v1",
        "tffc.clubfinderCampaignIdentity.v1",
        "tffc.clubfinderReturnSnapshot.v1", "tffc.challengeOrigin",
        "tffc.challengeReturnIndex", "tffc.openStatsOnReturn",
    ]
    data = []
    for key in keys:
        row = ["| " + code(key)]
        for app in (deck, cf):
            ops = sorted(set(x["store"] + "." + x["op"]
                             for x in app["storage"] if x["key"] == key))
            literal = key in app["js"]
            row.append(", ".join(code(x) for x in ops) if ops else
                       ("Text present; usage unresolved" if literal else "No direct match"))
        data.append(" | ".join(row) + " |")
    return data


def snapshot_status(cf):
    html = cf["html"]
    canonical = json.loads((ROOT / "competition.json").read_text(encoding="utf-8"))
    payload = html.split(BEGIN, 1)[1].split(END, 1)[0]
    m = re.search(r"const EMBEDDED_COMPETITION_DATA=(.*?);\s*$",
                  payload.strip(), re.S)
    if not m:
        return "Unable to extract embedded fallback: inspect separately."
    embedded = json.loads(m.group(1))
    return (
        ("MATCH" if embedded == canonical else "STALE")
        + "; embedded " + str(embedded.get("updated_at"))
        + "; canonical " + str(canonical.get("updated_at"))
        + ". Live ../competition.json remains authoritative."
    )


def make_report(deck, cf):
    table = []
    for app in (deck, cf):
        table.append("| " + code(app["path"]) + " | " +
                     f"{len(app['raw']):,} | " + code(fingerprint(app["raw"])) +
                     " | " + str(len(app["functions"])) + " | " +
                     str(len(app["storage"])) + " | " +
                     str(app["css_class_count"]) + " |")
    map_rows = []
    for name in deck["functions"]:
        edges = deck["edges"][name]
        # The count includes the function declaration. No static count
        # can prove non-use where dynamic property access is possible.
        extra = max(0, edges["token_occurrences"] - 1)
        map_rows.append("| " + code(name) + " | " + str(extra) +
                        " | " + str(edges["call_syntax_occurrences"]) + " |")
    likely = ", ".join(code(x) for x in deck["orphan_candidates"][:24])
    candidates_count = len(deck["orphan_candidates"])
    contract = {
        "Deck persists existing v1 challenge saves": "tffc.challengeDeck.v1" in deck["js"],
        "Deck reads Clubfinder campaign bridge": "tffc.clubfinderCampaign.v1" in deck["js"],
        "Deck has conditional identity-backup recovery":
            "tffc.clubfinderCampaignIdentity.v1" in deck["js"]
            and "sameOrigin" in deck["js"] and "sameSelection" in deck["js"],
        "Deck migrates legacy journeyTies": "x.journeyTies" in deck["js"]
            and "delete x.journeyTies" in deck["js"],
        "Deck retains old Stats-tab return index":
            "stats-return-v2" in deck["js"] and "tffc.challengeReturnIndex" in deck["js"],
        "Deck returns through explicit Clubfinder route":
            "challenges-exit-v3" in deck["js"],
        "Deck keeps live progress renderer":
            "function renderStats()" in deck["js"],
        "Clubfinder names the campaign bridge":
            "tffc.clubfinderCampaign.v1" in cf["js"],
        "Clubfinder has Challenge entry function":
            "function openChallenges(" in cf["js"],
    }
    contract_rows = [
        "| " + k + " | " + ("Present" if v else "**NOT DETECTED — manual review**") + " |"
        for k, v in contract.items()
    ]
    # Source positions use the newline-preserving mask for Clubfinder;
    # the 3 MB offline data is not printed or reparsed into this source map.
    bridge_names = [
        "openChallenges", "tinFoilChallengeStatsSnapshot",
        "tinFoilCampaignIdentityForSave", "tinFoilPersistCampaignIdentityBackup",
        "tinFoilRecoverCampaignIdentity", "tinFoilSavePigeonName",
        "tinFoilRestoreClubfinderReturnSnapshot",
    ]
    lines = [
        "# BETA dependency map — 25 September 2026",
        "",
        "**Historical, commit-scoped audit.** Generated from full checked-out files by "
        + code("updater/map_beta_dependencies.py") + ". Counts are static "
        "textual observations, **not** proof of dead code. No functional files "
        "or live competition data are written.",
        "",
        "## Full-source fingerprints and structural size",
        "",
        "| File | Bytes | SHA-256 | Named function declarations | Direct storage operations | CSS class tokens |",
        "|---|---:|---|---:|---:|---:|",
        *table,
        "",
        "## Cross-page browser-storage contracts",
        "",
        "Direct calls resolve simple quoted constant aliases; indirect helpers, computed "
        "keys and dynamic markup require manual review.",
        "",
        "| Key | Deck observed access | Clubfinder observed access |",
        "|---|---|---|",
        *storage_table(deck, cf),
        "",
        "### Behavioural compatibility requirements",
        "",
        "| Contract | Static audit |",
        "|---|---|",
        *contract_rows,
        "",
        "### Producer and consumer entry points",
        "",
        "**Clubfinder bridge / return and identity functions:** "
        + evidence_summary(cf["scan"], bridge_names),
        "",
        "**Deck saved state / bridge / render / return:** "
        + evidence_summary(deck["scan"], [
            "blankState", "loadState", "save", "applyClubfinderCampaignTruth",
            "awardCampaignChallenges", "isUnlocked", "renderStats",
            "openTrophy", "advanceTrophy", "applySimulationChange",
            "tinFoilReturnToClubfinder",
        ]),
        "",
        "The campaign bridge carries counters, away ties, pigeon miles, current "
        "round and identity; the Deck falls back to an origin-and-selection "
        "matched identity backup when the bridge lacks the Pigeon Name. "
        "The Deck migrates prototype journeyTies on read. Keep those data and "
        "compatibility boundaries intact before any code split.",
        "",
        "## Deck named function reference index",
        "",
        "The counts below include textual references in the inline script, "
        "**excluding the declaration** for the middle column. The final "
        "column counts call-shaped expressions and includes the declaration. "
        "Do not classify a function as dead from a low number alone.",
        "",
        "| Function | Other token references | Call-shaped occurrences |",
        "|---|---:|---:|",
        *map_rows,
        "",
        "## CSS dependency candidates",
        "",
        f"Deck CSS contains {deck['css_class_count']} distinct class tokens; "
        f"{candidates_count} lack an exact whole-word occurrence in static "
        "markup or inline JS. This is only a candidate scan: computed class "
        "names, template-generated markup, pseudo-classes and third-party "
        "code can produce false positives.",
        "",
        "First 24 candidate names: " + (likely or "None detected."),
        "",
        "Preserve the active 680px iPhone Deck height rule, the Call Sign / "
        "Pigeon Name / Miles Flown frame, and the three-tap Trophy Cabinet. "
        "Treat all further CSS deletions as independent, tested PRs.",
        "",
        "## Offline fallback freshness at this source revision",
        "",
        snapshot_status(cf),
        "",
        "## Dependency-safe next steps",
        "",
        "1. Preserve prototype migration, v1 storage keys, campaign-origin/date "
        "matching, explicit Challenges return and old Stats-tab return; "
        "extend regression tests before renaming or extracting their implementations.",
        "2. Keep the currently active renderer named renderStats despite its legacy "
        "name until call sites and tests are updated together. It powers the "
        "truth frame, simulator and Trophy Cabinet.",
        "3. Do not remove the simulator, its DOM or its callbacks until a "
        "separate verified campaign-progression harness exists.",
        "4. Review any zero-textual-reference CSS candidate manually against "
        "generated markup, selectors and browser behaviours before selecting "
        "a small reversible cleanup.",
        "5. Refresh the embedded offline snapshot in a separate guarded PR "
        "if a strict current-canonical fallback check is required. "
        "Never bundle large competition-data churn with a structural refactor.",
        "",
    ]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true",
                   help="require committed generated report to match source")
    args = p.parse_args()
    deck, cf = (analyse(label, path) for label, path in PATHS.items())
    generated = make_report(deck, cf)
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != generated:
            raise SystemExit("FAIL: full-source dependency report is missing or stale")
        print("PASS: dependency map exactly reproduces checked-out sources")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(generated, encoding="utf-8")
        print("WROTE", OUT.relative_to(ROOT))
    print("Deck functions:", len(deck["functions"]),
          "| Clubfinder functions:", len(cf["functions"]))
    print("No production, BETA app, competition or storage mutations")


if __name__ == "__main__":
    main()
