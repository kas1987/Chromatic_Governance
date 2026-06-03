---
name: migration-check
description: Review database, schema, config, data, API, plugin, or dependency migrations before release. Use when a change may alter stored data, contracts, environment variables, installation steps, configuration, or backwards compatibility and needs preflight validation.
---

# Migration Check

Check whether a release migration is safe, reversible, observable, and clearly documented.

## Core procedure

1. Identify migration type: database, schema, config, file format, API contract, dependency, infra, auth, or plugin manifest.
2. Map before/after state and all affected consumers.
3. Check forward path, backward compatibility, rollback behavior, and data integrity.
4. Require backup/export guidance for destructive or irreversible steps.
5. Verify monitoring, smoke tests, and post-migration validation.
6. Classify migration risk and blockers.

## Output structure

Use `references/migration-check-template.md` for formal checks. Otherwise provide:

```markdown
## Migration check

**Type:** ...
**Risk:** low / medium / high / blocked
**Recommendation:** pass / conditional / fail

### Before / after
- Before: ...
- After: ...

### Safety checks
| Check | Status | Evidence |
|---|---|---|

### Rollback / recovery
- ...

### Blockers
- ...
```

## Guardrails

- Treat destructive migrations as `high` risk unless backup and recovery are proven.
- Do not approve migrations without validation and rollback discussion.
- Flag silent config/env changes as release blockers.
- Separate technical migration steps from customer/user communication needs.

## Related references

- `references/migration-check-template.md`
- `references/rollback-plan-template.md`
- `references/release-gate-model.md`
