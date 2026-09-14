#!/usr/bin/env python3
"""Read-only audit of 2026-27 FA Cup Extra Preliminary source pages.

Football Web Pages is the project's standard results source. Fetch the relevant
round/replay date pages with a browser user-agent and preserve every parsed row
for reconciliation against Clubfinder's legacy EPR table. Production data is
never modified.
"""
from __future__ import annotations

from io import StringIO
from pathlib import Path
from urllib.request import Request, urlopen
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

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/152 Safari/537.36"


def clean_cell(v):
    if pd.isna(v):
        return None
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return str(v).strip()


def fetch_html(url):
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def main():
    report = {"pages": [], "source": "Football Web Pages"}
    md = ["# Extra Preliminary authoritative source audit", "", "READ ONLY. Production data unchanged.", ""]
    total_tables = total_rows = 0
    for date, expected_round, url in PAGES:
        page = {"date": date, "expected_round": expected_round, "url": url, "tables": []}
        md += [f"## {date} — {expected_round}", "", f"Source: {url}", ""]
        try:
            html = fetch_html(url)
            tables = pd.read_html(StringIO(html))
        except Exception as exc:
            page["error"] = f"{type(exc).__name__}: {exc}"
            md += [f"ERROR: {page['error']}", ""]
            report["pages"].append(page)
            continue
        page["html_bytes"] = len(html.encode("utf-8"))
        total_tables += len(tables)
        md += [f"HTML bytes: **{page['html_bytes']}**", f"Parsed tables: **{len(tables)}**", ""]
        for idx, df in enumerate(tables):
            columns = [str(c) for c in df.columns]
            rows = [[clean_cell(v) for v in row.tolist()] for _, row in df.iterrows()]
            total_rows += len(rows)
            item = {
                "index": idx,
                "shape": [int(df.shape[0]), int(df.shape[1])],
                "columns": columns,
                "rows": rows,
                "sample": rows[:12],
            }
            page["tables"].append(item)
            md += [f"### Table {idx}", f"Shape: {df.shape[0]} × {df.shape[1]}", f"Columns: `{columns}`", ""]
            for row in rows[:8]:
                md.append("- " + " | ".join("" if v is None else str(v) for v in row))
            md.append("")
        report["pages"].append(page)

    report["total_tables"] = total_tables
    report["total_rows"] = total_rows
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("EPR AUTHORITATIVE SOURCE AUDIT: COMPLETE")
    print("Pages:", len(PAGES))
    print("Tables parsed:", total_tables)
    print("Rows preserved:", total_rows)
    print("READ ONLY. Production main untouched.")


if __name__ == "__main__":
    main()
