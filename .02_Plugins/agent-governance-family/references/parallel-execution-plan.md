# Parallel Execution Plan Template

| Lane | Owner agent | Branch/worktree | Allowed files | Denied files | Dependencies | Output | Reviewer |
|---|---|---|---|---|---|---|---|

## Merge order

1. Shared contracts / schemas
2. Tests / eval fixtures
3. Implementation lanes
4. Docs / release notes
5. Final integration validation

## Conflict controls

- Each lane owns distinct paths where possible.
- Shared files require a named integration owner.
- Agents must stop before editing denied paths.
- Every lane produces a handoff note with files changed, validation run, and open risks.
