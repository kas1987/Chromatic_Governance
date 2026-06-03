---
name: architecture-review
description: review software architecture, plugin architecture, service boundaries, repository structure, technical plans, or proposed refactors for correctness, maintainability, scalability, and risk. use when a user asks whether a design is sound, when agents need a system-level review before implementation, or when major changes could create coupling, data, security, or operational risks.
---

# Architecture Review


Use this skill to evaluate whether a proposed or existing system design is coherent, maintainable, and safe to build on.

## Inputs

Collect or infer:

- System goal and user-facing outcome.
- Current architecture, diagrams, folder structure, code paths, APIs, schemas, or deployment topology.
- Proposed change or decision under review.
- Constraints: budget, time, existing stack, team skill, reliability, compliance, scale, and migration risk.
- Known pain points, incidents, or technical debt.

If evidence is missing, mark findings as assumptions rather than treating them as facts.

## Procedure

1. **State the architecture question** in one sentence.
2. **Identify the architecture unit**: plugin family, repo, module, service, API, data layer, agent workflow, or deployment boundary.
3. **Map the system at the right depth**:
   - Inputs and outputs.
   - Core components.
   - State ownership.
   - External dependencies.
   - Trust boundaries.
   - Runtime and deployment assumptions.
4. **Evaluate against the architecture scorecard** in `references/architecture-review-checklist.md`.
5. **Separate findings by severity**:
   - Blocker: likely data loss, security exposure, unreliable release, or impossible maintenance.
   - High: major coupling, unclear ownership, missing migration path, brittle interface.
   - Medium: debt or ambiguity that can be managed with follow-up.
   - Low: style, naming, or documentation polish.
6. **Recommend a path**: keep, revise, split, simplify, stage, or reject.
7. **Define implementation guardrails** for agents before coding.

## Output standard

Be direct. Do not over-design. Prefer the smallest architecture that protects correctness, boundaries, and future change.

## Guardrails

- Do not propose rewrites when a targeted boundary fix is enough.
- Do not approve designs with unclear state ownership or destructive migration paths.
- Call out coupling that makes testing, rollback, or agent delegation difficult.
- Escalate if auth, secrets, payment, user data, migrations, or production deployment is affected.


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
