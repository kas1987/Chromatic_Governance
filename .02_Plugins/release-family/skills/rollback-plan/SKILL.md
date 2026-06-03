---
name: rollback-plan
description: Create rollback and recovery plans for releases, deployments, migrations, plugins, or feature launches. Use when a user needs stop conditions, revert steps, backup strategy, feature flag fallback, incident response, or pre-release recovery planning.
---

# Rollback Plan

Create a rollback plan that can be executed under pressure without interpretation.

## Core procedure

1. Identify what is being released and the failure modes that require rollback.
2. Define measurable rollback triggers: error rate, failed smoke test, data issue, customer impact, security signal, or deployment failure.
3. Specify rollback method: revert commit, redeploy prior artifact, disable flag, restore config, reverse migration, or manual recovery.
4. List prerequisites: backups, previous artifact, access, owner, commands, and communication channel.
5. Define verification after rollback.
6. Include escalation and communication steps.

## Output structure

Use `references/rollback-plan-template.md` for formal plans. Otherwise provide:

```markdown
## Rollback plan

**Release/change:** ...
**Owner:** ...
**Rollback method:** ...

### Triggers
- ...

### Steps
1. ...

### Verification
- ...

### Communications
- ...

### Residual risks
- ...
```

## Guardrails

- Do not assume rollback is possible for data or schema changes; verify reversibility.
- Do not provide destructive commands without confirmation and backup notes.
- For high-risk migrations, require a recovery plan even if rollback is impossible.
- Keep rollback instructions short, ordered, and executable.

## Related references

- `references/rollback-plan-template.md`
- `references/migration-check-template.md`
