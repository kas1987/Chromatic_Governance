---
name: agent-retrospective
description: Evaluate agent performance after a sprint, review, incident, build cycle, or multi-agent run. Use when the user asks what worked, what failed, which agents were effective, where delegation broke down, or how to improve future agent workflows.
---

# Agent Retrospective

Turn agent workflow experience into measurable improvements for skills, prompts, policies, and review gates.

## Core procedure

1. Summarize the mission, agents involved, outputs produced, and validation status.
2. Assess each agent against expected output, scope discipline, evidence quality, speed, safety, and handoff quality.
3. Identify failure modes: unclear scope, duplicate work, authority confusion, weak tests, stale context, missing evidence, tool misuse.
4. Separate systemic issues from one-off mistakes.
5. Create improvement actions for skills, policies, templates, hooks, and delegation rules.
6. Assign owners and priority for each improvement.

## Output format

Produce a concise, auditable markdown artifact. Include:

```markdown
## Agent Retrospective

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

Expected output focus: retrospective with scores, findings, root causes, improvement actions, owner, priority, next validation.

## Guardrails

- Prefer the narrowest capable agent and least authority required.
- Do not let an agent approve its own high-risk work.
- Mark assumptions separately from confirmed facts.
- Require human approval for destructive, credentialed, production, external, legal, financial, or security-sensitive actions.
- Do not invent agent capabilities; use the roster, plugin manifests, source files, and explicit user instructions.

## Related references

- `references/agent-retrospective-template.md`
- `references/risk-tier-model.md`
- `references/decision-rules.md`
