---
name: metrics-review
description: Review operational metrics, dashboards, KPIs, telemetry summaries, adoption metrics, latency, throughput, error rates, saturation, cost, quality signals, and agent performance indicators. Use when interpreting metric changes, release health, service degradation, model/tool quality, or whether a system is improving, stable, or regressing.
---

# Metrics Review

Convert metric snapshots into an operational interpretation and decision.

## Core procedure

1. Identify the metric set, time window, baseline, comparison period, and environment.
2. Classify each metric as traffic, latency, errors, saturation, quality, cost, adoption, or business outcome.
3. Compare current value against baseline, SLO/SLA, release expectation, and noise threshold.
4. Highlight deltas using absolute values and percentages when available.
5. Separate correlation from causation. Name candidate drivers and missing evidence.
6. Produce a decision: `healthy`, `watch`, `degraded`, `incident`, or `insufficient evidence`.

## Output structure

Use `references/metrics-review-template.md` for formal reviews. Otherwise provide:

```markdown
## Metrics review

**Decision:** healthy / watch / degraded / incident / insufficient evidence
**Window:** ...
**Baseline:** ...

### Key movements
| Metric | Current | Baseline | Change | Interpretation |
|---|---:|---:|---:|---|

### Likely drivers
- ...

### Risks
- ...

### Recommended actions
1. ...
```

## Guardrails

- Do not call a change meaningful without a baseline, threshold, or clear absolute impact.
- Do not average away p95/p99 latency, tail failures, or minority user impact.
- When sample size is small, mark confidence as low.
- Treat cost spikes, error spikes, latency tail shifts, and quality-regression signals as review triggers.

## Related references

- `references/metrics-review-template.md`
- `references/slo-review-template.md`
- `references/health-report-template.md`
