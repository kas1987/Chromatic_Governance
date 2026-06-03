---
name: module-boundaries
description: analyze, define, or enforce module boundaries, dependency direction, ownership, layering, folder structure, and allowed imports. use when a codebase is becoming coupled, a refactor is planned, agents need safe edit zones, or responsibilities across modules/plugins/services are unclear.
---

# Module Boundaries


Use this skill to prevent coupling and clarify where code should live.

## Inputs

Collect or infer:

- Current folder/module structure.
- Main responsibilities by module.
- Imports or dependencies, if available.
- Proposed new code or refactor.
- Pain points: circular imports, duplicate logic, unclear ownership, difficult tests.

## Procedure

1. **List current modules and responsibilities**.
2. **Classify each dependency** as allowed, questionable, or forbidden.
3. **Define desired dependency direction**: UI to application to domain to infrastructure, or another project-specific layering model.
4. **Assign ownership** for shared utilities, state, schemas, and integration code.
5. **Create safe edit zones** for agents.
6. **Recommend moves**: extract, merge, invert dependency, create adapter, or leave as-is.
7. **Define enforcement**: lint rule, import boundary rule, review checklist, or tests.

Use `references/module-boundary-rules.md` for default boundary principles.

## Output standard

Return a boundary map with allowed dependencies, forbidden dependencies, and concrete refactor steps.

## Guardrails

- Do not split modules purely for aesthetics.
- Do not create abstract layers without a concrete boundary problem.
- Avoid global utility dumping grounds.
- Escalate when boundary violations create security, data integrity, or deployment risks.


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
