#!/usr/bin/env python3
"""Barry's read-only scheduled-flight audit. No GitHub writes or scan dispatches.

Usage:
  python beta/barry_schedule_watchdog.py --csv actions-13-oct.csv --date 2026-10-13
  python beta/barry_schedule_watchdog.py --self-test

Input is the CSV exported from GitHub Actions via gh api --paginate. All source
timestamps are UTC; displayed times are Europe/London (BST where applicable).
A missing schedule event is *inferred* from run history, not proof GitHub dropped it.
"""
import argparse
import csv
import datetime as dt
import json
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
LONDON = ZoneInfo("Europe/London")
SCANS = {
    "results": ("Scan FA Cup results (v7.6 guarded)", 17),
    "draw": ("Scan FA Cup draw (guarded)", 37),
    "publisher": ("Publish verified competition check status", 55),
}
MAX_AGE = dt.timedelta(hours=3)


def parse_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def read_csv(path):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            if not row:
                continue
            if len(row) != 9:
                raise ValueError("Expected nine CSV fields; got %d" % len(row))
            ident, name, event, created, started, updated, status, conclusion, url = row
            rows.append(dict(id=ident, name=name, event=event,
                             created=parse_time(created), started=parse_time(started) if started else None,
                             updated=parse_time(updated), status=status,
                             conclusion=conclusion, url=url))
    return rows


def inspect(rows, date, observed_until):
    start = dt.datetime.combine(date, dt.time.min, tzinfo=UTC)
    end = start + dt.timedelta(days=1)
    # Require explicit cutoff so the last incomplete hour is not marked missing.
    boundary = observed_until.astimezone(UTC)
    report = {"date_utc": date.isoformat(), "observed_through_utc": boundary.isoformat(),
              "note": "Missing launch means no matching schedule run in exported history; root cause unproven.",
              "workflows": {}}
    for key, (name, minute) in SCANS.items():
        found = sorted((r for r in rows if r["name"] == name and r["event"] == "schedule"
                        and start <= r["created"] < end and r["created"] <= boundary), key=lambda r: r["created"])
        # Match a created run to its nominal slot only when within 59 minutes
        # after that slot. Late runs beyond this are reported but not assigned.
        slots = [start + dt.timedelta(hours=h, minutes=minute) for h in range(24)]
        pending_slots = [s for s in slots if s <= boundary < s + dt.timedelta(hours=1)]
        slots = [s for s in slots if s + dt.timedelta(hours=1) <= boundary]
        remaining = found.copy()
        missing = []
        for slot in slots:
            match = next((r for r in remaining if slot <= r["created"] < slot + dt.timedelta(hours=1)), None)
            if match:
                remaining.remove(match)
            else:
                missing.append(slot.astimezone(LONDON).isoformat())
        failures = [r for r in found if r["status"] == "completed" and r["conclusion"] != "success"]
        pending = [r for r in found if r["status"] != "completed"]
        latest = found[-1] if found else None
        report["workflows"][key] = {
            "scheduled_runs": len(found), "successes": sum(r["conclusion"] == "success" for r in found),
            "failures": [{"id": r["id"], "url": r["url"], "conclusion": r["conclusion"]} for r in failures],
            "unfinished": [r["id"] for r in pending],
            "missing_or_delayed_slots_local": missing,
            "not_yet_evaluable_slots_local": [s.astimezone(LONDON).isoformat() for s in pending_slots],
            "unmatched_runs": [r["id"] for r in remaining if not any(s <= r["created"] < s + dt.timedelta(hours=1) for s in pending_slots)],
            "latest": {"id": latest["id"], "created_local": latest["created"].astimezone(LONDON).isoformat(),
                       "updated_local": latest["updated"].astimezone(LONDON).isoformat(),
                       "url": latest["url"]} if latest else None,
        }
    report["other_scheduled_workflows"] = dict(Counter(
        r["name"] for r in rows if r["event"] == "schedule" and
        start <= r["created"] < end and r["name"] not in [n for n, _ in SCANS.values()]))
    return report


def self_test():
    def row(name, stamp, conclusion="success"):
        time = parse_time(stamp)
        return dict(id="1", name=name, event="schedule", created=time, started=time,
                    updated=time, status="completed", conclusion=conclusion, url="https://github.com/example")
    d = dt.date(2026, 10, 13)
    rows = [row(SCANS["results"][0], "2026-10-13T03:34:15Z"),
            row(SCANS["draw"][0], "2026-10-13T03:49:42Z"),
            row(SCANS["publisher"][0], "2026-10-13T03:18:25Z")]
    result = inspect(rows, d, parse_time("2026-10-13T05:00:00Z"))
    assert result["workflows"]["results"]["scheduled_runs"] == 1
    assert result["workflows"]["results"]["successes"] == 1
    assert len(result["workflows"]["results"]["missing_or_delayed_slots_local"]) == 3
    assert not result["workflows"]["publisher"]["unmatched_runs"]
    failed = inspect([row(SCANS["results"][0], "2026-10-13T03:17:00Z", "failure")],
                     d, parse_time("2026-10-13T04:00:00Z"))
    assert len(failed["workflows"]["results"]["failures"]) == 1
    assert not result["workflows"]["results"]["unmatched_runs"]
    print("Barry watchdog self-test: PASS")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv", type=Path)
    p.add_argument("--date", help="UTC creation date, YYYY-MM-DD")
    p.add_argument("--through", required=True, help="UTC observation boundary, ISO timestamp")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.csv or not args.date:
        p.error("--csv and --date are required unless --self-test")
    result = inspect(read_csv(args.csv), dt.date.fromisoformat(args.date),
                     parse_time(args.through) if args.through else None)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
