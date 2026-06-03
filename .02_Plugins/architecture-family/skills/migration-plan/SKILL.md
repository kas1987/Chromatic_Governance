---
name: migration-plan
description: plan safe migrations for databases, schemas, files, APIs, plugin layouts, configuration, state models, dependency changes, or architecture refactors. use when existing users, persisted data, deployed systems, agents, or workflows could be disrupted by a change.
---

# Migration Plan


Use this skill to convert architecture change into a safe staged migration.

## Inputs

Collect or infer:

- Current state and desired state.
- Data, files, APIs, configs, agents, or deployments affected.
- Compatibility requirements.
- Rollback expectations.
- Expected downtime or user impact.
- Validation evidence available.

## Procedure

1. **Describe current and target states**.
2. **Classify migration risk**: low, medium, high, or critical.
3. **Split into stages**:
   - Prepare.
   - Dual-read or dual-write if needed.
   - Backfill or transform.
   - Cutover.
   - Validate.
   - Remove old path.
4. **Define preflight checks** and backups.
5. **Define rollback or recovery plan**.
6. **Define success metrics and smoke tests**.
7. **List human approval points**.

Use `references/migration-plan-template.md` as the default structure.

## Output standard

Return an ordered plan that can be executed by an implementation agent with clear stop conditions.

## Guardrails

- Never assume destructive changes are safe without backup and rollback.
- Do not combine migration and cleanup in the same irreversible step.
- Prefer expand-and-contract migrations for live systems.
- Escalate for user data, auth, payments, production databases, or irreversible deletes.


## Handoff format

Return results using:

```markdown
# Architecture Result
## Scope
## Inputs reviewed
## Executive finding
## Decisions / recommendations
## Risks and tradeoffs
## Required follow-ups
## Files or interfaces affected
## Evidence / assumptions
```
