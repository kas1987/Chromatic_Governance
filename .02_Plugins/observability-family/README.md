# Observability Family

Logs, metrics, tracing, incident summaries, RCA, SLO checks, alert tuning, and health reports.

## Purpose

Use this family when operational signals need to become decisions. It helps Claude Code, IDE agents, and human reviewers diagnose failures, summarize incidents, interpret metrics, map traces, check reliability objectives, tune alerts, and produce health reports.

## Skills

- `logs-triage` - Diagnose noisy logs, stack traces, CI output, deployment logs, and agent/tool failures.
- `metrics-review` - Interpret metric changes against baselines, thresholds, SLOs, and release expectations.
- `trace-map` - Map request, job, event, workflow, or agent/tool execution paths across components.
- `incident-brief` - Create active-incident summaries with impact, status, timeline, owner, mitigation, and next update.
- `root-cause` - Produce evidence-based root cause analysis and corrective actions after containment.
- `slo-check` - Compare SLIs/SLOs, error budgets, and reliability targets against observed behavior.
- `alert-tuning` - Improve alert precision, actionability, routing, thresholds, dedupe, and runbook coverage.
- `health-report` - Generate decision-ready system, release, service, agent, or operational health reports.

## Agents

- `observability-analyst` - Interprets operational telemetry and produces incident, health, and RCA outputs.

## References

- `references/observability-operating-model.md`
- `references/incident-severity-model.md`
- `references/log-triage-template.md`
- `references/metrics-review-template.md`
- `references/incident-brief-template.md`
- `references/root-cause-template.md`
- `references/slo-review-template.md`
- `references/alert-tuning-playbook.md`
- `references/health-report-template.md`
- `references/trace-map-template.md`
- `references/release-health-signals.md`

## Operating rule

Do not turn telemetry into false certainty. Separate confirmed facts, probable causes, hypotheses, and missing evidence. For active incidents, prioritize impact, containment, owner, and next update. For post-incident analysis, require verifiable corrective actions.

## Status

Core skill procedures implemented. Hooks and scripts are advisory until reviewed for each target environment.
