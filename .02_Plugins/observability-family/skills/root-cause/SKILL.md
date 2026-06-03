---
name: root-cause
description: Perform structured root cause analysis for incidents, regressions, outages, failed deployments, failed agent runs, data issues, reliability problems, or recurring defects. Use after containment or when enough evidence exists to explain what happened, why it happened, how it escaped detection, and what corrective actions prevent recurrence.
---

# Root Cause Analysis

Produce evidence-based RCA with corrective actions, not blame.

## Core procedure

1. Define the incident or failure in one sentence.
2. Reconstruct the timeline from detection through resolution.
3. Identify triggering event, proximate cause, contributing factors, and detection gap.
4. Use `5 whys` only as a support tool; do not force a single cause when the system has multiple contributors.
5. Identify why existing tests, evals, monitoring, reviews, or release gates did not catch it.
6. Create corrective actions with owner, priority, due date/condition, and verification method.

## Output structure

Use `references/root-cause-template.md` for formal RCA. Otherwise provide:

```markdown
## Root cause analysis

**Failure:** ...
**Impact:** ...
**Root cause:** ...
**Contributing factors:** ...

### Timeline
| Time | Event | Evidence |
|---|---|---|

### Detection and response gaps
- ...

### Corrective actions
| Action | Owner | Priority | Verification |
|---|---|---|---|

### Lessons
- ...
```

## Guardrails

- Do not produce RCA from weak evidence; produce a preliminary analysis instead.
- Do not confuse trigger with root cause.
- Avoid person-blaming. Focus on process, design, tooling, monitoring, and control failures.
- Every corrective action must be verifiable.

## Related references

- `references/root-cause-template.md`
- `references/incident-severity-model.md`
- `references/observability-operating-model.md`
