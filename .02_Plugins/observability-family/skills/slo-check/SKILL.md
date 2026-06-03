---
name: slo-check
description: Check service level objectives, SLIs, error budgets, reliability targets, latency/error/availability thresholds, release health gates, and operational risk against observed metrics. Use when validating whether a system meets reliability expectations, whether a release should continue, or whether error budget burn requires action.
---

# SLO Check

Compare observed behavior to reliability objectives and recommend action.

## Core procedure

1. Identify the SLI, SLO target, measurement window, calculation method, and source system.
2. Calculate current performance and error budget use when data is available.
3. Compare against target, alert threshold, release gate, and historical baseline.
4. Classify status as `within target`, `watch`, `budget risk`, `breach`, or `insufficient data`.
5. Recommend whether to continue, slow, freeze, rollback, or escalate.
6. Define the minimum monitoring needed for the next decision point.

## Output structure

Use `references/slo-review-template.md` for formal checks. Otherwise provide:

```markdown
## SLO check

**Status:** within target / watch / budget risk / breach / insufficient data
**SLI:** ...
**SLO target:** ...
**Window:** ...

### Measurements
| Signal | Value | Target | Status |
|---|---:|---:|---|

### Error budget
- Consumed: ...
- Remaining: ...
- Burn risk: ...

### Recommendation
- ...
```

## Guardrails

- Do not invent SLO targets. Ask for or mark them missing.
- Do not rely on average latency when p95/p99 is the actual user pain.
- Treat repeated near-breaches as operational risk even if the formal SLO has not yet failed.
- For release decisions, connect SLO status to go/hold/rollback recommendations.

## Related references

- `references/slo-review-template.md`
- `references/metrics-review-template.md`
- `references/release-health-signals.md`
