#!/usr/bin/env bash
set -euo pipefail
tmp="$(mktemp -d)"
echo "TMP=$tmp"
cp -R . "$tmp/repo"
cd "$tmp/repo"

python -m pip install -e . >/dev/null

# create a task
task-new "Smoke test task" --owner tester
orchestrator-once
# find the created plan id
pid=$(ls plans | head -n1 | sed 's/.md$//')
plan-summarize "$pid"
echo "OK: $pid"
