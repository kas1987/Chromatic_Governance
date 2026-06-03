#!/usr/bin/env bash
set -euo pipefail
root="${1:-.}"
fail=0
printf 'Docs drift quick check for %s
' "$root"
find "$root" -type f \( -name '*.md' -o -name '*.mdx' \) | while read -r file; do
  if grep -nE 'TODO|FIXME|TBD|needs-owner-review|unverified' "$file" >/tmp/docs_drift_match 2>/dev/null; then
    printf '
%s
' "$file"
    cat /tmp/docs_drift_match
  fi
done
exit "$fail"
