# Agent Handoff: Chainbreaker — PR Branch Locking

## Task ID
NW-REVIEW-INTAKE-002

## Mission
Enforce one active mutating agent per PR branch using `lock_pr_branch.py`.

## Allowed files
- `.03_Harness Governance/scripts/lock_pr_branch.py`
- `.03_Harness Governance/schemas/pr_branch_lock.schema.json`
- `.03_Harness Governance/governance/review-intake/PR_COLLISION_CONTROL_PLAYBOOK.md`
- `.agents/review-intake/locks/*.lock.json`

## Acceptance criteria
- `acquire` succeeds (exit 0) when no active lock exists for the PR.
- Second `acquire` fails (exit 2) while the first lock is still active.
- Expired lock (past `expires_at`) can be replaced by a new `acquire`.
- `release` removes the lock file; subsequent `status` returns `"unlocked"`.

## Stop conditions
- Time parsing fails — log the raw value and halt.
- Lock files cannot be written to `.agents/review-intake/locks/` — check permissions.
- Scenario requires a distributed lock (multi-repo, multi-instance) — flag for Phase 5 (central DB).
