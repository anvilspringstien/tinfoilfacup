#!/usr/bin/env python3
"""Read-only audit of authoritative 2026-27 FA Cup Extra Preliminary source pages.

Fetches Football Web Pages date pages covering the Extra Preliminary Round and
its replays, enumerates all HTML tables pandas can parse, and writes a compact
JSON/Markdown inspection report. No production data is changed.
"""
from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "epr-authoritative-source-audit.json"
OUT_MD = ROOT / "epr-authoritative-source-audit.md"

PAGES = [
    ("2026-08-07", "Extra Preliminary Round", "https://www.footballwebpages.co.uk/fa-cup/20260807"),
    ("2026-08-08", "Extra Preliminary Round", "https://www.footballwebpages.co.uk/fa-cup/20260808"),
    ("2026-08-09", "Extra Preliminary Round", "https://www.footballwebpages.co.uk/fa-cup/20260809"),
    ("2026-08-11", "Extra Preliminary Round Replay", "https://www.footballwebpages.co.uk/fa-cup/20260811"),
    ("2026-08-12", "Extra Preliminary Round Replay", "https://www.footballwebpages.co.uk/fa-cup/20260812"),
    ("2026-08-18", "Extra Preliminary Round Replay", "https://www.footballwebpages.co.uk/fa-cup/20260818"),
]


def clean_cell(v):
    if pd.isna(v):
        return None
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return str(v).strip()


def main():
    report = {"pages": []}
    md = ["# Extra Preliminary authoritative source audit", "", "READ ONLY. Production data unchanged.", ""]
    total_tables = 0
    for date, expected_round, url in PAGES:
        page = {"date": date, "expected_round": expected_round, "url": url, "tables": []}
        md += [f"## {date} — {expected_round}", "", f"Source: {url}", ""]
        try:
            tables = pd.read_html(url)
        except Exception as exc:
            page["error"] = f"{type(exc).__name__}: {exc}"
            md.append(f"ERROR: {page['error']}")
            md.append("")
            report["pages"].append(page)
            continue
        total_tables += len(tables)
        md.append(f"Parsed tables: **{len(tables)}**")
        md.append("")
        for idx, df in enumerate(tables):
            columns = [str(c) for c in df.columns]
            sample = []
            for _, row in df.head(12).iterrows():
                sample.append([clean_cell(v) for v in row.tolist()])
            item = {
                "index": idx,
                "shape": [int(df.shape[0]), int(df.shape[1])],
                "columns": columns,
                "sample": sample,
            }
            page["tables"].append(item)
            md += [
                f"### Table {idx}",
                f"Shape: {df.shape[0]} × {df.shape[1]}",
                f"Columns: `{columns}`",
                "",
            ]
            for row in sample[:8]:
                md.append("- " + " | ".join("" if v is None else str(v) for v in row))
            md.append("")
        report["pages"].append(page)

    report["total_tables"] = total_tables
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("EPR AUTHORITATIVE SOURCE AUDIT: COMPLETE")
    print("Pages:", len(PAGES))
    print("Tables parsed:", total_tables)
    print("Wrote:", OUT_JSON.name, "and", OUT_MD.name)
    print("READ ONLY. Production main untouched.")


if __name__ == "__main__":
    main()
