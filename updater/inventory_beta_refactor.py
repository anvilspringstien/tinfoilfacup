#!/usr/bin/env python3
"""Read-only BETA refactor inventory; writes only a generated Markdown report.

Intentionally scans actual checked-out files in GitHub Actions so large BETA
Clubfinder and canonical JSON are never truncated by a connector response.
No source, production, ingestion, or canonical data modifications.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/refactor/2026-09-25-generated-source-map.md"
SOURCES = (
    "beta/clubfinder-beta.html",
    "beta/challenges-beta.html",
    "clubfinder.html",
    "competition.json",
)
BEGIN = "/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
END = "/* TIN_FOIL_EMBEDDED_COMPETITION_END */"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def scan_html(path, raw):
    html = raw.decode("utf-8")
    styles = re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.I | re.S)
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.I | re.S)
    # The BETA Clubfinder embeds a large competition-data fallback in JS.
    # Exclude it from the behavioural-JS count; record it separately below.
    stripped_scripts = []
    for script in scripts:
        if BEGIN in script and END in script:
            start = script.index(BEGIN)
            end = script.index(END, start) + len(END)
            script = script[:start] + "/* embedded competition data excluded */" + script[end:]
        stripped_scripts.append(script)
    js = "\n".join(stripped_scripts)
    funcs = sorted(set(re.findall(
        r"\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", js
    )))
    keys = sorted(set(re.findall(r"tffc\.[a-zA-Z0-9._-]+", html)))
    ids = sorted(set(re.findall(r"\bid\s*=\s*[\"']([^\"']+)[\"']", html)))
    return {
        "path": path,
        "bytes": len(raw),
        "sha256": digest(raw),
        "lines": html.count("\n") + 1,
        "css_blocks": len(styles),
        "css_bytes": sum(len(x.encode("utf-8")) for x in styles),
        "js_blocks": len(scripts),
        "behavioural_js_bytes": len(js.encode("utf-8")),
        "functions": funcs,
        "storage_candidates": keys,
        "dom_ids": ids,
        "has_render_stats": "renderStats" in funcs,
        "has_simulator": "applySimulationChange" in funcs,
        "has_trophy_viewer": "openTrophy" in funcs,
        "has_live_refresh": "refreshCompetitionData" in funcs,
        "mobile_breakpoint_680": bool(re.search(r"max-width\s*:\s*680px", html)),
    }


def embedded_snapshot(html, canonical):
    if html.count(BEGIN) != 1 or html.count(END) != 1:
        return {"status": "MARKER_ERROR"}
    payload = html.split(BEGIN, 1)[1].split(END, 1)[0]
    if payload.count("const EMBEDDED_COMPETITION_DATA=") != 1:
        return {"status": "DECLARATION_ERROR"}
    payload = payload.split("const EMBEDDED_COMPETITION_DATA=", 1)[1].rsplit(";", 1)[0].strip()
    try:
        embedded = json.loads(payload)
    except ValueError:
        return {"status": "PARSE_ERROR"}
    return {
        "status": "MATCH" if embedded == canonical else "STALE",
        "embedded_updated_at": embedded.get("updated_at"),
        "canonical_updated_at": canonical.get("updated_at"),
        "canonical_schema_version": canonical.get("schema_version"),
    }


def row(s):
    return (
        f"| `{s['path']}` | {s['bytes']:,} | {s['lines']:,} "
        f"| `{s['sha256']}` |"
    )


def render(scans, snap):
    beta = scans["beta/clubfinder-beta.html"]
    deck = scans["beta/challenges-beta.html"]
    lines = [
        "# Generated BETA source inventory — 25 September 2026",
        "",
        "Generated from the **full checked-out repository files**, not a truncated connector response. "
        "This is a read-only source map; regex matches identify investigation candidates, "
        "**not** proven dead code or permission to delete anything.",
        "",
        "## Full-file source fingerprints",
        "",
        "| File | Bytes | Lines | SHA-256 |",
        "|---|---:|---:|---|",
    ]
    lines += [row(scans[path]) for path in SOURCES]
    lines += [
        "",
        "## BETA structure",
        "",
        "| Measurement | BETA Clubfinder | BETA Challenges |",
        "|---|---:|---:|",
        f"| Embedded CSS blocks | {beta['css_blocks']} | {deck['css_blocks']} |",
        f"| Embedded CSS bytes | {beta['css_bytes']:,} | {deck['css_bytes']:,} |",
        f"| Inline JS blocks | {beta['js_blocks']} | {deck['js_blocks']} |",
        f"| Behavioural JS bytes (excluding Clubfinder embedded competition payload) | {beta['behavioural_js_bytes']:,} | {deck['behavioural_js_bytes']:,} |",
        f"| Named function declarations (unique) | {len(beta['functions'])} | {len(deck['functions'])} |",
        f"| Unique markup IDs | {len(beta['dom_ids'])} | {len(deck['dom_ids'])} |",
        "",
        "### BETA Clubfinder named functions",
        "",
        ", ".join(f"`{f}`" for f in beta["functions"]) or "(none found)",
        "",
        "### BETA Challenges named functions",
        "",
        ", ".join(f"`{f}`" for f in deck["functions"]) or "(none found)",
        "",
        "### Storage key candidates (string scan; validate each read/write before editing)",
        "",
        "**Clubfinder:** " + (", ".join(f"`{k}`" for k in beta["storage_candidates"]) or "(none)"),
        "",
        "**Challenges:** " + (", ".join(f"`{k}`" for k in deck["storage_candidates"]) or "(none)"),
        "",
        "### Investigation candidates (presence only)",
        "",
        f"- Challenge `renderStats` declaration: **{deck['has_render_stats']}**; separate Challenges Stats UI was removed by PR #84. Follow its references before removing.",
        f"- Challenge simulator `applySimulationChange`: **{deck['has_simulator']}**; preserve until an independent test mechanism is proved.",
        f"- Trophy inspection `openTrophy`: **{deck['has_trophy_viewer']}**; preserve the three-tap experience.",
        f"- BETA Clubfinder `refreshCompetitionData`: **{beta['has_live_refresh']}**; preserve canonical live fetch and offline fallback.",
        f"- 680px mobile breakpoint detected: Clubfinder **{beta['mobile_breakpoint_680']}**, Challenges **{deck['mobile_breakpoint_680']}**.",
        "",
        "## Embedded competition fallback freshness",
        "",
        f"- Snapshot comparison against checked-out canonical JSON: **{snap['status']}**.",
        f"- Embedded timestamp: `{snap.get('embedded_updated_at', 'unavailable')}`.",
        f"- Current canonical timestamp: `{snap.get('canonical_updated_at', 'unavailable')}`.",
        "- **Do not modify either data source as part of this report.** If stale, run the separate guarded BETA snapshot repair on a new branch; leave live competition updates intact.",
        "",
        "## Next manual analysis",
        "",
        "1. Cross-reference candidate function calls, DOM IDs and CSS selectors; prove no listeners/storage/legacy URLs depend on any proposed deletion.",
        "2. Capture before/after source fingerprints for each narrow cleanup PR; pass Deck, Trophy, identity, Petts Wood, Exmouth, Weston and replay regressions.",
        "3. Preserve the checkpoint branch `checkpoint/accepted-beta-20260925` at `89f0338e5f11f8e7a36d3bf69e57e3be88fc264f`.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="require generated report to match committed source files")
    args = parser.parse_args()
    scans = {}
    for path in SOURCES:
        raw = (ROOT / path).read_bytes()
        scans[path] = scan_html(path, raw) if path.endswith(".html") else {
            "path": path, "bytes": len(raw), "lines": raw.count(b"\n") + 1,
            "sha256": digest(raw),
        }
    canonical = json.loads((ROOT / "competition.json").read_text(encoding="utf-8"))
    snap = embedded_snapshot((ROOT / "beta/clubfinder-beta.html").read_text(encoding="utf-8"), canonical)
    report = render(scans, snap)
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != report:
            raise SystemExit("FAIL: generated inventory missing or out of date")
        print("PASS: full-source inventory matches", OUT.relative_to(ROOT))
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(report, encoding="utf-8")
        print("WROTE:", OUT.relative_to(ROOT))
    print("BETA offline fallback:", snap["status"],
          "| canonical:", snap.get("canonical_updated_at"))
    print("Full BETA source and production files: READ ONLY")


if __name__ == "__main__":
    main()
