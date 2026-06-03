# Agent Governance Family Policy

## Boundary

This plugin controls multi-agent delegation, authority maps, conflict resolution, review chains, parallel planning, retrospective learning, and escalation policy.

## Default stance

- Use the narrowest capable agent for each task.
- Keep agents read-only or recommendation-only unless write authority is explicitly delegated.
- Require independent review for high-risk work.
- Escalate to human approval before destructive, credentialed, production, legal, financial, external-system, or security-sensitive actions.
- Record assumptions, evidence, decisions, owners, and validation status.

## Separation of duties

- An implementation agent may not be the sole approver for its own high-risk changes.
- Research agents should not modify code unless explicitly delegated.
- Release agents should not bypass QA/eval or security gates.
- Hooks should be advisory unless a user deliberately promotes them to enforcement.

## Stop conditions

An agent must stop when scope is ambiguous, files outside its lane are needed, validation fails, source-of-truth files conflict, tool access is broader than approved, or the next action creates external side effects.
