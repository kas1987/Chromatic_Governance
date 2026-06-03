---
name: post-release-monitor
description: Plan and summarize post-release monitoring for errors, metrics, feedback, incidents, support signals, and success criteria. Use after deployment, during staged rollout, or when deciding whether to continue, pause, rollback, or close a release.
---

# Post Release Monitor

Define what to watch after release and convert signals into continue, pause, rollback, or close decisions.

## Core procedure

1. Identify release success criteria and expected behavior after deployment.
2. Define monitoring windows: immediate, short-term, and follow-up.
3. List signals: logs, metrics, traces, crash reports, support tickets, user feedback, business KPIs, and security alerts.
4. Set thresholds and decision actions for continue, pause, rollback, or investigate.
5. Summarize observed signals when data is provided.
6. Produce a post-release status and next action.

## Output structure

Use `references/post-release-monitor-template.md` for formal monitoring. Otherwise provide:

```markdown
## Post-release monitor

**Release:** ...
**Window:** ...
**Status:** healthy / watch / degraded / rollback recommended / unknown

### Signals
| Signal | Expected | Observed | Action |
|---|---|---|---|

### Decision
- ...

### Follow-up
- ...
```

## Guardrails

- Do not claim health without data or explicit user confirmation.
- Use `unknown` when telemetry is unavailable.
- For security, data loss, or customer-impacting failures, escalate quickly.
- Record follow-up fixes into changelog/release notes if relevant.

## Related references

- `references/post-release-monitor-template.md`
- `references/release-gate-model.md`
