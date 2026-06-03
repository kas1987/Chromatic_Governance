#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

if [ ! -d "$ROOT" ]; then
  echo "ERROR: path not found: $ROOT" >&2
  exit 1
fi

printf 'Product scope scan for %s
' "$ROOT"
printf '
Candidate product files:
'
find "$ROOT" -maxdepth 4 -type f   \( -iname '*roadmap*' -o -iname '*requirement*' -o -iname '*prd*' -o -iname '*mvp*' -o -iname '*feedback*' -o -iname '*backlog*' \)   | sort || true

printf '
Potential product markers:
'
grep -RIn --exclude-dir=.git --exclude='*.zip' -E 'TODO|MVP|roadmap|requirement|user story|feedback|acceptance criteria|out of scope|non-goal' "$ROOT" 2>/dev/null | head -n 80 || true
