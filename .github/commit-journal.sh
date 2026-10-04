#!/usr/bin/env bash
# Commit journal/config/evolution changes made by a workflow run and push them.
set -euo pipefail
git config user.name "zoh-bot"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add journal config EVOLUTION.md 2>/dev/null || true
git diff --cached --quiet && exit 0
git commit -m "journal: $(TZ=America/New_York date +%F) $1"
for i in 1 2 3; do git pull --rebase && git push && exit 0; sleep 5; done
exit 1
