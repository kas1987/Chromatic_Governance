---
name: adr-create
description: create architecture decision records for meaningful technical decisions, tradeoffs, standards, dependency choices, interface boundaries, data ownership, plugin structure, or agent governance. use when a decision should be durable, explainable, reviewable, or preserved for future contributors and agents.
---

# ADR Create


Use this skill to capture durable architecture decisions in a compact Architecture Decision Record.

## Inputs

Collect or infer:

- Decision being made.
- Current context and forces.
- Options considered.
- Chosen option.
- Consequences, risks, and follow-up work.
- Date, status, and owner if available.

## Procedure

1. **Decide whether an ADR is warranted**. Use ADRs for decisions that affect future maintenance, interfaces, dependencies, data, deployment, security, or agent behavior.
2. **Write one decision per ADR**. Split unrelated choices.
3. **Use the template** in `references/adr-template.md`.
4. **Keep options factual**: describe tradeoffs, not preferences alone.
5. **State consequences** including what becomes easier, harder, and riskier.
6. **Add review triggers**: what future condition should cause this ADR to be revisited.

## Output standard

Return a file-ready ADR in markdown. Use a stable title and status: proposed, accepted, superseded, deprecated, or rejected.

## Guardrails

- Do not use ADRs as long design docs.
- Do not combine decision, implementation plan, and backlog into one blob.
- Do not mark a decision accepted unless the user or project authority has approved it.
- If the decision is uncertain, use status `proposed`.


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
