#!/usr/bin/env python3
"""Publish only verified scheduled Results and Draw scan freshness."""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

API = "https://api.github.com/repos/anvilspringstien/tinfoilfacup/actions/workflows/{}/runs?event=schedule&per_page=10"
WORKFLOWS = {"results": "scan-results.yml", "draw": "scan-draw.yml"}
NOW = dt.datetime.now(dt.timezone.utc)
MAX_AGE = dt.timedelta(hours=3)

def latest(name):
    req = urllib.request.Request(API.format(name), headers={
        "Authorization": "Bearer " + os.environ["GH_TOKEN"],
        "Accept": "application/vnd.github+json",
        "User-Agent": "tffc-competition-heartbeat",
    })
    with urllib.request.urlopen(req, timeout=20) as response:
        runs = json.load(response)["workflow_runs"]
    return next((r for r in runs if r["head_branch"] == "main"), None)

def checked_time(run):
    if not run or run["status"] != "completed" or run["conclusion"] != "success":
        return None
    completed = dt.datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
    if not (dt.timedelta(0) <= NOW - completed <= MAX_AGE):
        return None
    return completed

runs = {key: latest(filename) for key, filename in WORKFLOWS.items()}
times = {key: checked_time(run) for key, run in runs.items()}
both = all(times.values())
payload = {
    "schema_version": 1,
    "monitor_ran_at": NOW.isoformat().replace("+00:00", "Z"),
    "state": "checked" if both else "unverified",
    "last_checked_at": min(times.values()).isoformat().replace("+00:00", "Z") if both else None,
    "results": "success" if times["results"] else "unverified",
    "draw": "success" if times["draw"] else "unverified",
}
# Keep the public health verdict strict, but expose why each scanner was rejected.
# These fields describe GitHub Actions metadata, not competition data.
def diagnostic(run):
    if not run:
        return {"reason": "no_scheduled_run_on_main", "run_id": None, "url": None,
                "status": None, "conclusion": None, "updated_at": None}
    stamp = dt.datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
    age = NOW - stamp
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
            "status": run["status"], "conclusion": run["conclusion"],
            "updated_at": run["updated_at"]}

payload["diagnostics"] = {key: diagnostic(run) for key, run in runs.items()}
destination = Path("beta/competition-check-status.json")
old = json.loads(destination.read_text()) if destination.exists() else None
if old != payload:
    destination.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps(payload))
