#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

check() { if bash -c "$2"; then echo "PASS: $1"; PASS=$((PASS + 1)); else echo "FAIL: $1"; FAIL=$((FAIL + 1)); fi; }

check "SKILL.md exists" "[ -f '$SKILL_DIR/SKILL.md' ]"
check "SKILL.md has YAML frontmatter" "head -1 '$SKILL_DIR/SKILL.md' | grep -q '^---$'"
check "SKILL.md has ## Examples" "grep -q '## Examples' '$SKILL_DIR/SKILL.md'"
check "SKILL.md has ## Troubleshooting" "grep -q '## Troubleshooting' '$SKILL_DIR/SKILL.md'"
check "SKILL.md has ## See Also" "grep -q '## See Also' '$SKILL_DIR/SKILL.md'"
check "references/support.md exists" "[ -f '$SKILL_DIR/references/support.md' ]"

echo ""; echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && exit 0 || exit 1
