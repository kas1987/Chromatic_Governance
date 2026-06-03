#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
cd "$ROOT"
missing=0
for plugin in */.claude-plugin/plugin.json; do
  family="${plugin%/.claude-plugin/plugin.json}"
  test -f "$family/README.md" || { echo "missing README $family"; missing=1; }
  test -d "$family/skills" || { echo "missing skills $family"; missing=1; }
  count=$(find "$family/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')
  if [ "$count" = "0" ]; then echo "no skills $family"; missing=1; fi
  grep -RIl "Placeholder scaffold\|Until this skill is implemented" "$family/skills" >/tmp/ecosystem_placeholder_matches 2>/dev/null && { echo "active placeholder language in $family"; missing=1; } || true
done
if [ "$missing" != "0" ]; then exit 1; fi
echo "ecosystem_polish_audit OK"
