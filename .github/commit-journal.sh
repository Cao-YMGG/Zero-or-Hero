#!/usr/bin/env bash
# Commit journal/config/evolution changes made by a workflow run and push them.
# On 2026-10-19 a rebase conflict on journal/news (the News feed workflow and the bot's own
# refresh both write it) left the checkout mid-rebase, and every later commit that day failed.
# So: clear any stuck rebase first, and let this run's version win conflicting hunks.
set -euo pipefail
git config user.name "zoh-bot"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git rebase --abort 2>/dev/null || true
git checkout -q main 2>/dev/null || true
git add journal config EVOLUTION.md 2>/dev/null || true
git diff --cached --quiet && exit 0
git commit -m "journal: $(TZ=America/New_York date +%F) $1"
for i in 1 2 3 4; do
  if git pull --rebase -X theirs origin main && git push origin HEAD:main; then exit 0; fi
  git rebase --abort 2>/dev/null || true
  sleep $((i * 5))
done
exit 1
