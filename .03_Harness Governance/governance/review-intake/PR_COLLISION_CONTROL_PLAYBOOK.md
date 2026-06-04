# PR Collision Control Playbook

## Purpose

Prevent multiple agents, IDEs, or terminals from mutating the same PR branch concurrently.

## Core rule

One PR branch = one active mutating agent at any time.

## Lock lifecycle

```
acquire → patch → validate → comment → release
```

## Lock fields

| Field | Description |
|---|---|
| `lock_id` | Unique identifier |
| `repo` | `owner/repo` |
| `pr_number` | PR integer |
| `branch` | Branch name |
| `holder` | Agent name |
| `queue_item_id` | NW-... reference |
| `started_at` | ISO 8601 |
| `expires_at` | ISO 8601 (default +30 min) |

## Behavior

- Read-only inspection does not require a lock.
- Write / push / commit requires a successfully acquired lock.
- Expired locks (past `expires_at`) may be replaced.
- Active non-expired locks block new mutation work (exit code 2).

## Commands

```bash
# Acquire
python scripts/lock_pr_branch.py acquire --repo owner/repo --pr-number 42 --holder Sentinel --queue-item-id NW-001

# Check
python scripts/lock_pr_branch.py status --repo owner/repo --pr-number 42

# Release
python scripts/lock_pr_branch.py release --repo owner/repo --pr-number 42
```

## Stop conditions

- Lock cannot be acquired (exit code 2) — another agent is active; wait or escalate.
- Branch changed unexpectedly during patching — release lock and re-evaluate.
- Agent needs files outside `allowed_files` — release lock, mark blocked, escalate.
