---
name: technical-debt-map
description: map, rank, and convert technical debt into actionable remediation work across code, docs, tests, architecture, dependencies, configuration, agent workflows, or plugin families. use when a project feels messy, brittle, hard to extend, under-tested, over-coupled, or blocked by accumulated shortcuts.
---

# Technical Debt Map


Use this skill to turn vague messiness into ranked, actionable debt work.

## Inputs

Collect or infer:

- Symptoms: slow changes, flaky tests, confusing docs, repeated bugs, fragile deployment, duplicated logic.
- Areas affected: code, data, tests, docs, architecture, dependencies, tools, agents, plugins.
- Business or project impact.
- Risk of doing nothing.
- Time available for cleanup.

## Procedure

1. **Inventory debt items** with evidence.
2. **Classify each item**:
   - Structural debt.
   - Test debt.
   - Documentation debt.
   - Dependency debt.
   - Security debt.
   - Operational debt.
   - Agent/context debt.
3. **Score impact and effort** using `references/technical-debt-scoring.md`.
4. **Rank into waves**:
   - Now: blocks safe work.
   - Next: reduces recurring friction.
   - Later: useful cleanup, not urgent.
   - Ignore: not worth fixing yet.
5. **Convert top items into implementation-ready tasks** with acceptance criteria.
6. **Recommend prevention rules** so debt does not immediately return.

## Output standard

Return a prioritized debt register. Each item must include evidence, impact, effort, owner or likely edit zone, and recommended next action.

## Guardrails

- Do not label unfamiliar code as bad without evidence.
- Do not prioritize aesthetic cleanup over correctness, tests, security, or delivery blockers.
- Do not propose huge rewrites as the first option.
- Escalate security debt to security-family review.


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
