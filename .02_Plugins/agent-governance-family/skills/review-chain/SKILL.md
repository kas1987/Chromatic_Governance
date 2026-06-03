---
name: review-chain
description: Design reviewer order, approval gates, and separation-of-duties rules for agent-generated work. Use when the user asks who should review an implementation, how to set up multi-agent review, when human approval is required, or how to keep coding, security, QA, architecture, and release checks distinct.
---

# Review Chain

Ensure important work is reviewed by the right specialists before merge, release, or external action.

## Core procedure

1. Classify the change by risk: low, medium, high, critical.
2. Determine required review lanes: implementation, architecture, security, QA/eval, docs, release, observability, product.
3. Enforce separation of duties for high-risk work: implementer cannot be the only approver.
4. Order reviews so blockers are found early: architecture/security before large implementation, QA before release, docs before handoff.
5. Define required evidence for approval: diffs, tests, commands, screenshots, logs, metrics, risk register, rollback path.
6. State merge/release criteria and human approval triggers.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Review Chain

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

Expected output focus: review chain table with stage, reviewer, evidence required, pass criteria, fail action, human approval trigger.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/review-chain-template.md`
- `references/risk-tier-model.md`
- `references/authority-model.md`
