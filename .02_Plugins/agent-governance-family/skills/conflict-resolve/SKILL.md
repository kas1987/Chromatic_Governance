---
name: conflict-resolve
description: Resolve disagreements between agents, skill outputs, plans, reviews, tests, docs, or architecture decisions using evidence hierarchy and explicit decision rules. Use when agents disagree, outputs conflict, recommendations diverge, sources contradict each other, or a coordinator needs a final decision path.
---

# Conflict Resolve

Turn conflicting agent outputs into a clear decision, documented tradeoff, or escalation.

## Core procedure

1. Name each conflicting claim, recommendation, or proposed action.
2. Attach evidence to each position: files inspected, command results, tests, docs, user instructions, source freshness, and assumptions.
3. Classify the conflict type: factual, priority, design tradeoff, security risk, test interpretation, scope ambiguity, or authority dispute.
4. Apply the evidence hierarchy: explicit user instruction, current repo state, passing tests, source-of-truth docs, fresh logs, then inferred reasoning.
5. Choose one of three outcomes: decide, merge positions, or escalate.
6. Record rationale, rejected options, risk, owner, and follow-up validation.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Conflict Resolve

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

Expected output focus: conflict resolution record with positions, evidence, decision, rationale, risk, owner, validation step.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/conflict-resolution-record.md`
- `references/decision-rules.md`
- `references/escalation-policy.md`
