#!/usr/bin/env bash
# Ground Health builds an origin view for auditing; it publishes reports only.
set -euo pipefail

git config user.name "Tin Foil FA Cup Ground Monitor"
git config user.email "actions@users.noreply.github.com"
# These two audit builders intentionally rewrite the local presentation. The
# Competition Health publisher owns that presentation, so retain the checkout's
# version here rather than publishing it or carrying it into a rebase.
git restore --worktree -- clubfinder.html
git add ground-health.md updater/ground-health.json law2-location-verification-audit.md updater/law2-location-verification-audit.json tester-club-postcodes.csv
# Unexpected tracked mutations must fail closed, not be stashed or discarded.
git diff --exit-code
if git diff --cached --quiet; then
  echo "Ground Health outputs unchanged."
else
  git commit -m "Update Ground Health outputs"
  git pull --rebase origin "${GITHUB_REF_NAME:?GITHUB_REF_NAME is required}"
  git push origin "HEAD:${GITHUB_REF_NAME}"
fi
