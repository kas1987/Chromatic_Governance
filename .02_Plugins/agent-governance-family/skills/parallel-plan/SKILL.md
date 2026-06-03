---
name: parallel-plan
description: Split complex work across agents, branches, or git worktrees with clean boundaries, dependencies, merge order, and review gates. Use when the user asks to run agents in parallel, coordinate a sprint, divide a large implementation, use worktrees, or prevent parallel agents from clobbering each other.
---

# Parallel Plan

Convert a large mission into parallel-safe workstreams with minimal conflict and clear integration points.

## Core procedure

1. Define the shared objective and final integration artifact.
2. Break work into independent lanes by file ownership, subsystem, plugin family, or artifact type.
3. Assign one owner and one reviewer per lane.
4. Define branch/worktree names, allowed file paths, denied file paths, dependencies, and handoff artifacts.
5. Sequence integration from lowest-risk/shared-contract changes to highest-risk feature changes.
6. Require validation after each merge and final system validation before release.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Parallel Plan

**Scope:** ...
**Decision / recommendation:** ...
**Risk level:** low / medium / high / critical

### Findings
- ...

### Plan / matrix / record
| Item | Owner | Scope | Evidence | Gate / next action |
|---|---|---|---|---|

### Escalations
- ...

### Next actions
1. ...
```

Expected output focus: parallel execution plan with lanes, owners, file boundaries, dependencies, merge order, validations, conflict risks.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/parallel-execution-plan.md`
- `references/delegation-matrix.md`
- `references/review-chain-template.md`
