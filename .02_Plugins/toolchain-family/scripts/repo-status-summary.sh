#!/usr/bin/env bash
set -euo pipefail
printf "== Repo status ==
"
git status --short || true
printf "
== Branch ==
"
git branch --show-current || true
printf "
== Worktrees ==
"
git worktree list || true
printf "
== Diff stat ==
"
git diff --stat || true
