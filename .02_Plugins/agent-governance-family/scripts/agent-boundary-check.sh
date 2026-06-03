#!/usr/bin/env bash
set -euo pipefail
cat >&2 <<'MSG'
[agent-governance-family] advisory hook: agent boundary check active.
Confirm delegated scope, denied paths, review owner, and escalation triggers before agent work proceeds.
MSG
exit 0
