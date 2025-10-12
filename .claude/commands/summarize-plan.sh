#!/usr/bin/env bash
set -euo pipefail
PID="${1:-}"
if [[ -z "$PID" ]]; then echo "Usage: plan-summarize P-XXXX" >&2; exit 1; fi
in="plans/${PID}.md"
out="plans/${PID}.summary.md"
if [[ ! -f "$in" ]]; then echo "Missing $in" >&2; exit 1; fi

{
  echo "# ${PID} — Ready for Review"
  echo
  echo "## Checklist"
  echo "- [ ] Gather documents"
  echo "- [ ] Validate assumptions"
  echo "- [ ] Produce deliverable"
  echo
  echo "## Linked Plan"
  echo "- ${in}"
} > "$out"

echo "$out"
