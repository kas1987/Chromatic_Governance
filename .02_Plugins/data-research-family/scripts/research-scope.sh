#!/usr/bin/env bash
set -euo pipefail
root="${CLAUDE_PLUGIN_ROOT:-$(pwd)}"
if [ -d "$root/data-research-family" ]; then
  root="$root/data-research-family"
fi
if [ ! -d "$root/skills" ]; then
  echo '[data-research-family] warning: skills directory not found; advisory only' >&2
  exit 0
fi
missing=0
for skill in source-scan evidence-brief benchmark-compare market-scan docs-digest api-change-watch citation-audit research-handoff; do
  if [ ! -f "$root/skills/$skill/SKILL.md" ]; then
    echo "[data-research-family] missing skill: $skill" >&2
    missing=1
  fi
done
if [ "$missing" -eq 0 ]; then
  echo '[data-research-family] advisory hook: research scope ready' >&2
fi
exit 0
