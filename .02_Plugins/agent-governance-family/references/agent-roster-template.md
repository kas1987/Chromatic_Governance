# Agent Roster Template

| Agent | Mission | Inputs | Outputs | Allowed scope | Denied scope | Reviewer | Escalation triggers |
|---|---|---|---|---|---|---|---|
| coordinator | Convert user goal into bounded lanes | User request, repo state, context brief | Delegation plan | Planning and coordination | Final approval for high-risk changes | Human | Ambiguous authority, destructive action |

## Roster quality checks

- Every active workstream has exactly one owner.
- Every high-risk workstream has an independent reviewer.
- No agent has vague ownership such as "help with everything".
- Read-only research and write-capable implementation are separated unless explicitly approved.
