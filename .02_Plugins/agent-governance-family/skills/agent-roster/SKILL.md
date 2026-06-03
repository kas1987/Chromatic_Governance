---
name: agent-roster
description: Create and maintain an auditable roster of agents, roles, responsibilities, capabilities, permissions, and review relationships for Claude Code, IDE agent teams, plugin families, or multi-agent sprints. Use when the user asks which agents exist, what each agent should do, how to define specialist roles, or how to avoid overlapping authority.
---

# Agent Roster

Define who is on the agent team, what each agent owns, what it may touch, and where its authority ends.

## Core procedure

1. Identify the mission, repo scope, plugin families, and active workstreams.
2. List required agent roles by function, not personality: coordinator, implementer, reviewer, security, QA/eval, architect, release, docs, observability, research.
3. For each agent, define inputs, outputs, allowed files/tools, prohibited actions, review obligations, and escalation triggers.
4. Mark one accountable owner for each workstream and one reviewer for material changes.
5. Remove duplicate or vanity agents unless they have a clear responsibility boundary.
6. Produce a roster that can be used by delegate, authority-map, review-chain, and parallel-plan.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Agent Roster

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

Expected output focus: agent roster table with role, mission, inputs, outputs, allowed scope, denied scope, reviewer, escalation triggers.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/agent-roster-template.md`
- `references/authority-model.md`
- `references/governance-operating-model.md`
