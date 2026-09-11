#!/usr/bin/env python3
"""Retry updater commands on transient public-source failures.

Transport trouble is not the same thing as bad competition data. Commands are
retried with a short exponential backoff. If every attempt fails for a known
transport reason, the wrapper exits successfully in degraded mode so the existing
verified canonical state can still be audited by the normal health and regression
guards.

Any parser, coverage, validation or data-integrity failure remains a hard failure.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

TRANSIENT_PATTERNS = [
    r"HTTP Error (?:403|408|425|429|500|502|503|504)\b",
    r"<HTTPError .*?: (?:403|408|425|429|500|502|503|504)\b",
    r"URLError",
    r"urlopen error",
    r"timed out",
    r"TimeoutError",
    r"RemoteDisconnected",
    r"ConnectionResetError",
    r"Connection reset by peer",
    r"Temporary failure in name resolution",
    r"Name or service not known",
    r"Network is unreachable",
    r"TLSV1_ALERT_INTERNAL_ERROR",
    r"UNEXPECTED_EOF_WHILE_READING",
]
TRANSIENT_RE = re.compile("|".join(f"(?:{p})" for p in TRANSIENT_PATTERNS), re.I)


def emit(text: str, stream) -> None:
    if text:
        print(text, file=stream, end="" if text.endswith("\n") else "\n")


def append_summary(message: str) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        return
    try:
        with Path(summary).open("a", encoding="utf-8") as fh:
            fh.write(message.rstrip() + "\n")
    except OSError:
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="Public source command")
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--base-delay", type=float, default=2.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("a command is required after --")
    if args.attempts < 1:
        parser.error("--attempts must be at least 1")

    last_output = ""
    for attempt in range(1, args.attempts + 1):
        print(f"SOURCE RESILIENCE: {args.label} attempt {attempt}/{args.attempts}")
        proc = subprocess.run(command, text=True, capture_output=True)
        combined = (proc.stdout or "") + (proc.stderr or "")
        last_output = combined

        if proc.returncode == 0:
            emit(proc.stdout, sys.stdout)
            emit(proc.stderr, sys.stderr)
            if attempt > 1:
                msg = f"SOURCE RESILIENCE: RECOVERED — {args.label} succeeded on attempt {attempt}."
                print(msg)
                append_summary(f"✅ {msg}")
            else:
                print(f"SOURCE RESILIENCE: HEALTHY — {args.label}.")
            return 0

        if not TRANSIENT_RE.search(combined):
            emit(proc.stdout, sys.stdout)
            emit(proc.stderr, sys.stderr)
            print(
                f"SOURCE RESILIENCE: HARD FAILURE — {args.label} failed for a non-transport reason; "
                "normal fail-closed behaviour preserved.",
                file=sys.stderr,
            )
            append_summary(
                f"❌ **{args.label}: hard failure.** The failure was not classified as transient transport trouble; publication remained blocked."
            )
            return proc.returncode or 1

        print(f"SOURCE RESILIENCE: transient source failure detected on attempt {attempt}.")
        if attempt < args.attempts:
            delay = args.base_delay * (2 ** (attempt - 1))
            print(f"SOURCE RESILIENCE: retrying after {delay:g}s.")
            time.sleep(delay)

    match = TRANSIENT_RE.search(last_output)
    reason = match.group(0) if match else "transient transport failure"
    warning = (
        f"{args.label} unavailable after {args.attempts} attempts ({reason}). "
        "Retaining the last verified canonical competition state; downstream health and regression guards remain active."
    )
    print(f"::warning title=Tin Foil FA Cup source degraded::{warning}")
    print(f"SOURCE RESILIENCE: DEGRADED — {warning}")
    append_summary(f"⚠️ **Source degraded:** {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
