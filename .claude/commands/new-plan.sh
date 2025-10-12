#!/usr/bin/env bash
set -euo pipefail
TITLE="${1:-}"; shift || true
OWNER="unknown"; TASK_ID=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --owner) OWNER="$2"; shift 2;;
    --task) TASK_ID="$2"; shift 2;;
    *) shift;;
  esac
done
if [[ -z "$TITLE" ]]; then
  echo "Usage: plan-new \"TITLE\" [--owner NAME] [--task T-XXXX]" >&2; exit 1
fi

mkdir -p plans .claude/templates
tmpl=".claude/templates/plan.md"
[[ -f "$tmpl" ]] || { echo "Missing $tmpl" >&2; exit 1; }

IDX_FILE=".claude/.plan_index"
idx=1; [[ -f "$IDX_FILE" ]] && idx=$(( $(cat "$IDX_FILE") + 1 ))
printf "%04d" "$idx" > "$IDX_FILE"

id="$(cat "$IDX_FILE")"
date="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
out="plans/P-${id}.md"

sed -e "s#\${ID}#${id}#g"     -e "s#\${TITLE}#${TITLE}#g"     -e "s#\${OWNER}#${OWNER}#g"     -e "s#\${DATE}#${date}#g"     -e "s#\${TASK_ID}#${TASK_ID}#g" "$tmpl" > "$out"

echo "$out"
