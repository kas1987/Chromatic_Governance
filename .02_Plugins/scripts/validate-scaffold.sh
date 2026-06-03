#!/usr/bin/env bash
set -euo pipefail
root="${1:-.}"
fail=0
for plugin in "$root"/*; do
  [ -d "$plugin" ] || continue
  name="$(basename "$plugin")"
  case "$name" in scripts) continue ;; esac
  if [ ! -f "$plugin/.claude-plugin/plugin.json" ]; then
    echo "FAIL $name: missing .claude-plugin/plugin.json"
    fail=1
    continue
  fi
  if [ ! -f "$plugin/README.md" ]; then
    echo "FAIL $name: missing README.md"
    fail=1
  fi
  if ! python3 -c 'import json,sys; json.load(open(sys.argv[1], encoding="utf-8"))' "$plugin/.claude-plugin/plugin.json"; then
    echo "FAIL $name: invalid plugin.json"
    fail=1
  fi
  echo "OK $name"
done
exit "$fail"
