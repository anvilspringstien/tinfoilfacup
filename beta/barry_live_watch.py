#!/usr/bin/env python3
"""Read-only live monitor for scheduled FA Cup scanner health.

Reads GitHub Actions run metadata using GITHUB_TOKEN; emits job summary and
GitHub warning annotations. Does not dispatch scans, write files, or open issues.
The monitor's own schedule is best-effort: silence is NOT proof of health.
"""
import datetime as dt
import json
import os
import urllib.request

UTC = dt.timezone.utc
WORKFLOWS = {
    "Results": "scan-results.yml",
    "Draw": "scan-draw.yml",
    "Heartbeat": "publish-competition-check-status.yml",
}
STALE_AFTER = dt.timedelta(hours=3)


def parse_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def verdict(runs, now):
    """Classify the latest *scheduled main* run, not manual or PR runs."""
    candidates = [r for r in runs if r.get("event") == "schedule"
                  and r.get("head_branch") == "main"]
    if not candidates:
        return "NO_SCHEDULED_RUN", None
    latest = max(candidates, key=lambda r: r["created_at"])
    status = latest.get("status")
    if status != "completed":
        return "UNFINISHED", latest
    if latest.get("conclusion") != "success":
        return "FAILED", latest
    finished = parse_time(latest["updated_at"])
    if finished > now or now - finished > STALE_AFTER:
        return "STALE", latest
    return "OK", latest


def fetch_runs(workflow, token):
    url = f"https://api.github.com/repos/anvilspringstien/tinfoilfacup/actions/workflows/{workflow}/runs?event=schedule&per_page=30"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "barry-schedule-watchdog",
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)["workflow_runs"]


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    now = dt.datetime.now(UTC)
    rows = []
    for label, workflow in WORKFLOWS.items():
        try:
            state, run = verdict(fetch_runs(workflow, token), now)
            url = run.get("html_url", "") if run else ""
            stamp = run.get("updated_at", "none") if run else "none"
        except Exception as exc:
            state, url, stamp = "API_ERROR", "", "unknown"
            print(f"::warning title=Barry API error::{label}: {type(exc).__name__}: {exc}")
        rows.append((label, state, stamp, url))
        if state not in ("OK", "API_ERROR"):
            print(f"::warning title=Barry scheduled scan::{label}: {state}; last update {stamp}; {url}")
    summary = ["## Barry's read-only schedule watch", "",
               f"Observed at {now.isoformat()}. Checks scheduled runs on main only.", "",
               "| Workflow | State | Latest update (UTC) | Run |",
               "|---|---|---|---|"]
    for label, state, stamp, url in rows:
        summary.append(f"| {label} | {state} | {stamp} | {('[View run](' + url + ')') if url else '—'} |")
    summary.extend(["", "Warnings are diagnostic, not automatic replacement launches.",
                    "GitHub Actions scheduling is best-effort; if this monitor does not run, it cannot report an outage."])
    content = "\n".join(summary) + "\n"
    print(content)
    destination = os.environ.get("GITHUB_STEP_SUMMARY")
    if destination:
        with open(destination, "a", encoding="utf-8") as handle:
            handle.write(content)


if __name__ == "__main__":
    main()
