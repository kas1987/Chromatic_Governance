# Observability Operating Model

## Purpose

Observability-family turns operational signals into decisions. It should not merely summarize telemetry; it should identify impact, confidence, severity, likely cause, and the next safest action.

## Signal categories

| Category | Examples | Primary use |
|---|---|---|
| Logs | stack traces, CI output, app logs, agent traces | Diagnose specific failures |
| Metrics | latency, errors, throughput, saturation, cost | Detect trend and health changes |
| Traces | request spans, job steps, agent/tool paths | Locate bottlenecks and handoff failures |
| Alerts | pages, warnings, monitors | Trigger response and escalation |
| Incidents | user reports, outage records, failed releases | Coordinate containment and learning |
| Quality signals | tests, evals, golden cases, regressions | Connect operations to QA/eval gates |

## Decision states

- `healthy`: evidence supports normal operation.
- `watch`: non-critical movement or incomplete evidence requires monitoring.
- `degraded`: confirmed reduction in reliability, quality, or performance.
- `incident`: active user/system impact requires response coordination.
- `unknown`: key telemetry is missing or contradictory.

## Evidence rules

1. Separate confirmed facts, probable causes, and hypotheses.
2. Use time windows and baselines whenever possible.
3. Include absolute numbers and percentages when available.
4. Surface missing telemetry instead of hiding it.
5. Recommend the smallest safe diagnostic step before large operational changes.

## Integration with other families

- Use `release-family` for rollout, rollback, and post-release gates.
- Use `qa-eval-family` when operational signals imply test/eval gaps.
- Use `security-family` when logs or traces expose secrets, abuse, auth failures, or suspicious activity.
- Use `architecture-family` when failures suggest systemic design boundaries or scalability issues.
- Use `context-family` to preserve incident state, decisions, and handoffs.
