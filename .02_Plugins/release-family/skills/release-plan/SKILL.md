---
name: release-plan
description: Plan a safe release from scoped changes, risks, dependencies, deployment steps, validation gates, rollback path, owners, and timing. Use when preparing a release, deciding whether work is ready to ship, coordinating feature freeze, defining release scope, or creating a go/no-go plan for Claude Code, IDE agents, or human reviewers.
---

# Release Plan

Create a practical release plan that turns finished work into a controlled ship decision.

## Core procedure

1. Identify release scope: included changes, excluded changes, target users, target environment, and release type.
2. Gather readiness evidence: tests, evals, code review status, docs, migrations, security review, known defects, and unresolved risks.
3. Classify release risk as `low`, `medium`, `high`, or `blocked`.
4. Define gates: build, test, migration, security, observability, rollback, and approval requirements.
5. Create a release sequence with owners, commands/checks to run, validation points, and stop conditions.
6. Produce a go/no-go recommendation. If evidence is missing, mark the release as `conditional` or `blocked`.

## Output structure

Use `references/release-plan-template.md` for formal release plans. Otherwise provide:

```markdown
## Release plan

**Release:** ...
**Recommendation:** go / conditional / no-go
**Risk:** low / medium / high / blocked

### Scope
- Included: ...
- Excluded: ...

### Readiness gates
| Gate | Status | Evidence | Owner |
|---|---|---|---|

### Release sequence
1. ...

### Rollback path
- Trigger: ...
- Action: ...

### Open blockers
- ...
```

## Guardrails

- Do not mark a release `go` without test/eval evidence or an explicit human waiver.
- Do not hide risks inside prose; list them as release blockers or accepted risks.
- Treat schema, auth, payment, data-loss, and migration changes as elevated risk by default.
- When in doubt, recommend a staged rollout or feature flag.

## Related references

- `references/release-gate-model.md`
- `references/release-plan-template.md`
- `references/rollback-plan-template.md`
