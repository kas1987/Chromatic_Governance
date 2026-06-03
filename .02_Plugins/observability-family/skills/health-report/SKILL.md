---
name: health-report
description: Generate system, release, service, agent, repo, or operational health reports from logs, metrics, incidents, alerts, CI status, test/eval results, release signals, and known risks. Use for periodic status, executive summaries, project health checks, or post-release monitoring summaries.
---

# Health Report

Summarize operational health in a decision-ready format.

## Core procedure

1. Define the reporting scope, time window, systems, environments, and intended audience.
2. Gather signals: availability, errors, latency, throughput, saturation, cost, incidents, alerts, tests, evals, releases, and known risks.
3. Classify health as `green`, `yellow`, `orange`, `red`, or `unknown`.
4. Explain the classification with evidence, trend, and risk.
5. Identify top issues, owners, next actions, and monitoring needs.
6. For leadership summaries, keep operational details brief and link to supporting evidence.

## Output structure

Use `references/health-report-template.md` for formal reports. Otherwise provide:

```markdown
## Health report

**Scope:** ...
**Window:** ...
**Overall health:** green / yellow / orange / red / unknown

### Executive readout
- ...

### Signal summary
| Area | Status | Evidence | Trend |
|---|---|---|---|

### Top risks
1. ...

### Actions
| Action | Owner | Priority | Due/trigger |
|---|---|---|---|
```

## Guardrails

- Do not mark health green when key signals are missing; use `unknown` or `yellow`.
- Mention missing telemetry explicitly.
- Separate current health from future risk.
- Avoid vanity metrics unless they directly inform a decision.

## Related references

- `references/health-report-template.md`
- `references/metrics-review-template.md`
- `references/release-health-signals.md`
