#!/usr/bin/env python3
"""Reject a candidate built before upstream changed its inputs.

Run after pull --rebase and before final validation/push. Only independent
monitor/fallback outputs may be rebased without rebuilding the candidate.
A non-fast-forward push still protects a change arriving after this check.
"""
import argparse
import subprocess

INDEPENDENT_OUTPUTS = {
    "beta/competition-check-status.json",
    "beta/competition-fallback.json",
    "ground-health.md",
    "updater/ground-health.json",
}


def changed_inputs(base, upstream, cwd=None):
    result = subprocess.run(["git", "diff", "--name-only", "-z", base, upstream],
                            cwd=cwd, check=True, capture_output=True)
    paths = result.stdout.decode().split("\0")
    return sorted(path for path in paths if path and path not in INDEPENDENT_OUTPUTS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--upstream", required=True)
    args = parser.parse_args()
    changed = changed_inputs(args.base, args.upstream)
    if changed:
        raise SystemExit("STALE COMPETITION CANDIDATE: upstream inputs changed; rebuild from the latest branch head. " + ", ".join(changed))
    print("PUBLICATION BASE GUARD: PASS; candidate inputs unchanged upstream")


if __name__ == "__main__":
    main()
