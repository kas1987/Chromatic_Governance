# Agent Governance Family

Controls delegation, authority boundaries, review chains, conflict resolution, parallel planning, and escalation rules for multi-agent Claude Code / IDE workflows.

## Core skills

- `agent-roster` — define agents, roles, responsibilities, allowed scope, denied scope, reviewers, and escalation triggers.
- `delegate` — choose the narrowest capable agent or plugin family for a task.
- `authority-map` — map who can read, write, execute, approve, merge, deploy, or escalate.
- `review-chain` — define independent review stages and approval gates.
- `parallel-plan` — split complex work across safe workstreams, branches, or worktrees.
- `conflict-resolve` — resolve disagreement between agents, plans, reviews, tests, or docs.
- `escalation` — determine when agents must stop and request human/specialist approval.
- `agent-retrospective` — evaluate agent workflow performance and improve future runs.

## Agents

- `agent-governor` — controls delegation, authority boundaries, review chains, and escalation rules for agent teams.

## Operating model

Use this family when a task involves more than one agent, cross-plugin coordination, unclear authority, high-risk actions, or review sequencing. Keep agents narrow, evidence-backed, and auditable.

## References

- `references/governance-operating-model.md`
- `references/agent-roster-template.md`
- `references/delegation-matrix.md`
- `references/authority-model.md`
- `references/escalation-policy.md`
- `references/risk-tier-model.md`
- `references/review-chain-template.md`
- `references/conflict-resolution-record.md`
- `references/decision-rules.md`
- `references/parallel-execution-plan.md`
- `references/agent-retrospective-template.md`

## Status

Core implementation complete. Skills are usable as governance procedures and can be deepened later with repo-specific scripts or policy integrations.
