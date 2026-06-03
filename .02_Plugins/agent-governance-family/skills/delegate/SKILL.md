---
name: delegate
description: Choose the right agent, skill, plugin family, or workstream owner for a task using scope, risk, authority, and required evidence. Use when the user asks to assign work, split a request among agents, decide who should act next, route tasks across plugin families, or prevent the wrong agent from taking action.
---

# Delegate

Route work to the narrowest capable agent while preserving least privilege and clear review ownership.

## Core procedure

1. Restate the task objective and classify it by domain: context, security, QA/eval, architecture, release, toolchain, observability, product, docs, research, or implementation.
2. Identify required capabilities and risk level: read-only analysis, file edits, commands, network, secrets, deployment, destructive changes.
3. Select the narrowest qualified agent or plugin family; avoid broad delegation when a specialist exists.
4. Define the agent mission, allowed scope, denied scope, expected output, review gate, and stop conditions.
5. If several agents are needed, order them by dependency and review path.
6. Escalate to human approval when the task requires credentials, production changes, external side effects, or ambiguous authority.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Delegate

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

Expected output focus: delegation plan with chosen agent, rationale, scope, permissions, expected artifact, reviewer, stop conditions.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/delegation-matrix.md`
- `references/authority-model.md`
- `references/escalation-policy.md`
