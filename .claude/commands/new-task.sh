#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(pwd)"
TITLE="${1:-}"; shift || true
OWNER="unknown"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2;;
    *) shift;;
  esac
done
if [[ -z "$TITLE" ]]; then
  echo "Usage: task-new \"TITLE\" --owner NAME" >&2; exit 1
fi

mkdir -p tasks .claude/templates
tmpl=".claude/templates/task.md"
if [[ ! -f "$tmpl" ]]; then echo "Missing $tmpl" >&2; exit 1; fi

# simple counter
IDX_FILE=".claude/.task_index"
idx=1; [[ -f "$IDX_FILE" ]] && idx=$(( $(cat "$IDX_FILE") + 1 ))
printf "%04d" "$idx" > "$IDX_FILE"

id="$(cat "$IDX_FILE")"
date="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
out="tasks/T-${id}.md"

sed -e "s#\${ID}#${id}#g"     -e "s#\${TITLE}#${TITLE}#g"     -e "s#\${OWNER}#${OWNER}#g"     -e "s#\${DATE}#${date}#g" "$tmpl" > "$out"

echo "$out"
