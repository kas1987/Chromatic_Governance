# Review Dispatch Playbook

## Purpose

Route queued review findings to the correct agent with bounded scope.

## Dispatch requirements

Every dispatch must include:
- task ID and source finding ID
- PR link / comment link
- owner agent and required specialties
- allowed files (scope boundary)
- forbidden files
- acceptance checks
- confidence score and risk level
- stop conditions

## Agent routing

| Finding type | Agent |
|---|---|
| `security` | Sentinel |
| `test_failure` | Auditor |
| `lint_style` | Janitor |
| `docs` | Archivist |
| `architecture` | Archivist |
| `bug_fix` | Sentinel |
| `repo_hygiene` | Janitor |
| `unclear` | Auditor |

## Dispatch rule

Only dispatch `ready` items unless the user explicitly requests review of blocked items.

## Stop conditions

- Confidence below 75 for mutation work.
- `allowed_files` is empty for a code mutation task.
- Human gate required (`needs-human-decision` status).
- PR branch already has an active mutation lock (exit code 2 from `lock_pr_branch.py acquire`).
