---
name: escalation
description: Decide when an agent must stop and ask a human, higher-authority reviewer, or specialist agent before continuing. Use when a task involves destructive actions, credentials, production systems, external side effects, legal/security risk, ambiguous instructions, failed validation, or unresolved conflict.
---

# Escalation

Prevent agents from crossing risk boundaries without explicit approval or specialist review.

## Core procedure

1. Identify the action the agent wants to take and its potential side effects.
2. Classify risk: low, medium, high, critical using references/risk-tier-model.md.
3. Check automatic escalation triggers: secrets, production, deletion, external communication, legal/financial claims, security exposure, failed tests, unresolved conflict, unclear authority.
4. Define what information the approver needs: options, recommendation, evidence, risk, rollback, deadline.
5. Ask for approval only for the specific next action, not broad future permission.
6. Record the approval outcome and any conditions before continuing.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Escalation

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

Expected output focus: escalation request with action, risk, evidence, options, recommendation, approval needed, safe fallback.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/escalation-policy.md`
- `references/risk-tier-model.md`
- `references/authority-model.md`
