#!/usr/bin/env python3
"""Report trusted scanner freshness separately from scheduled-run freshness."""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

REPOSITORY = "anvilspringstien/tinfoilfacup"
API = "https://api.github.com/repos/" + REPOSITORY + "/actions/workflows/{}/runs?per_page=100{}"
WORKFLOWS = {"results": "scan-results.yml", "draw": "scan-draw.yml"}
MAX_AGE = dt.timedelta(hours=3)
TRUSTED_EVENTS = {"schedule", "push"}


def eligible(run, scheduled=False):
    return (run.get("head_branch") == "main"
            and run.get("event") in ({"schedule"} if scheduled else TRUSTED_EVENTS)
            and (run.get("head_repository") or {}).get("full_name") == REPOSITORY)


def latest(name, scheduled=False):
    req = urllib.request.Request(API.format(name, "&event=schedule" if scheduled else ""), headers={
        "Authorization": "Bearer " + os.environ["GH_TOKEN"],
        "Accept": "application/vnd.github+json",
        "User-Agent": "tffc-competition-heartbeat",
    })
    with urllib.request.urlopen(req, timeout=20) as response:
        runs = json.load(response)["workflow_runs"]
    # A newer queued/failed run must not be hidden by an older success.
    return next((r for r in runs if eligible(r, scheduled)), None)


def diagnostic(run, now):
    if not run:
        return {"reason": "no_trusted_run_on_main", "run_id": None, "url": None,
                "event": None, "status": None, "conclusion": None, "updated_at": None}
    stamp = dt.datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
    age = now - stamp
    if run["status"] != "completed":
        reason = "not_completed"
    elif run["conclusion"] != "success":
        reason = "not_successful"
    elif age < dt.timedelta(0):
        reason = "future_timestamp"
    elif age > MAX_AGE:
        reason = "stale"
    else:
        reason = "verified"
    return {"reason": reason, "run_id": run["id"], "url": run.get("html_url"),
            "event": run.get("event"), "status": run["status"], "conclusion": run["conclusion"],
            "updated_at": run["updated_at"]}


def verdict(runs, now):
    diagnostics = {key: diagnostic(run, now) for key, run in runs.items()}
    checked = all(d["reason"] == "verified" for d in diagnostics.values())
    return {
        "state": "checked" if checked else "unverified",
        "last_checked_at": min(d["updated_at"] for d in diagnostics.values()) if checked else None,
        **{key: "success" if d["reason"] == "verified" else "unverified" for key, d in diagnostics.items()},
        "diagnostics": diagnostics,
    }


def build_payload(runs, scheduled_runs, now):
    return {"schema_version": 1, "monitor_ran_at": now.isoformat().replace("+00:00", "Z"),
            **verdict(runs, now), "scheduled": verdict(scheduled_runs, now)}


def main():
    now = dt.datetime.now(dt.timezone.utc)
    runs = {key: latest(filename) for key, filename in WORKFLOWS.items()}
    scheduled = {key: latest(filename, scheduled=True) for key, filename in WORKFLOWS.items()}
    payload = build_payload(runs, scheduled, now)
    destination = Path("beta/competition-check-status.json")
    old = json.loads(destination.read_text()) if destination.exists() else None
    if old != payload:
        destination.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
