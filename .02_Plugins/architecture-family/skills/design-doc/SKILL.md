---
name: design-doc
description: create concise technical design documents for features, services, plugins, agents, integrations, migrations, or refactors. use when a user needs a build-ready design, implementation plan, decision context, assumptions, risks, alternatives, rollout plan, or reviewable architecture proposal before coding.
---

# Design Doc


Use this skill to turn a technical idea into a reviewable, implementation-ready design document.

## Inputs

Collect or infer:

- Problem statement and target users.
- Current state and desired state.
- Constraints and non-goals.
- Affected components, APIs, data, agents, plugins, or workflows.
- Quality requirements: security, reliability, observability, performance, compatibility.

## Procedure

1. **Write the problem statement** in one short paragraph.
2. **Define goals and non-goals** so scope cannot silently expand.
3. **Describe the proposed design** using component, data, and control-flow sections.
4. **List interfaces and contracts** that must remain stable.
5. **Record alternatives considered** and why they were rejected.
6. **Define migration and rollout** if existing users, files, state, or deployments are affected.
7. **Add test and eval strategy** linked to acceptance criteria.
8. **Add open questions** that block implementation or change risk.

Use `references/design-doc-template.md` as the default structure.

## Output standard

Produce a document that a separate implementation agent can execute without needing to rediscover intent. Keep prose tight and decisions explicit.

## Guardrails

- Do not bury major tradeoffs in narrative paragraphs.
- Do not create fake certainty. Mark assumptions clearly.
- Do not skip migration, rollback, or testing for stateful systems.
- If the design changes security, data ownership, permissions, or external integrations, require review before implementation.


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
