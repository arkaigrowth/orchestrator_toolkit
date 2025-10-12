#!/usr/bin/env bash
set -euo pipefail
MSG="${1:-}"
LOG="${HOME}/.claude/statusline.log"
mkdir -p "$(dirname "$LOG")"
ts="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "[$ts] ${MSG}" >> "$LOG"
echo "$LOG"
