---
name: authority-map
description: Map decision rights and action permissions across humans, agents, skills, plugin families, hooks, scripts, MCP servers, CI jobs, and external systems. Use when the user asks who can approve, edit, merge, deploy, access secrets, run commands, or make final decisions in an agent workflow.
---

# Authority Map

Make authority explicit so agents know what they may decide, what they may recommend, and what requires approval.

## Core procedure

1. List actors and components: user, coordinator, specialist agents, hooks, skills, scripts, MCP servers, CI, release process.
2. List action categories: read, write, execute, network, secrets, dependency changes, merge, deploy, delete, external communication.
3. Assign authority level for each actor/action: observe, recommend, draft, modify, approve, execute, or forbidden.
4. Define escalation triggers for ambiguous, destructive, credentialed, production, legal, financial, or security-sensitive actions.
5. Align the map with security-family permissions-plan when available.
6. Produce a matrix and highlight over-broad or missing authority.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Authority Map

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

Expected output focus: authority matrix plus overreach findings, missing owner findings, escalation gates, recommended corrections.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/authority-model.md`
- `references/delegation-matrix.md`
- `references/escalation-policy.md`
