---
name: incident-brief
description: Create concise incident summaries from logs, metrics, alerts, user reports, CI failures, release notes, or agent observations. Use during active incidents, suspected outages, degraded services, failed deployments, failed agent runs, or when stakeholders need a clear status update with impact, timeline, mitigation, owner, and next update.
---

# Incident Brief

Create a clear, time-bounded incident update without overclaiming.

## Core procedure

1. Establish current state: detected time, status, impacted systems, impacted users, and severity.
2. Build a short timeline from available evidence.
3. Distinguish confirmed facts, probable causes, and open questions.
4. Identify mitigation already taken and the next containment action.
5. Assign owners where possible. If owners are unknown, specify owner needed.
6. Set the next update time or condition.

## Output structure

Use `references/incident-brief-template.md` for formal incident comms. Otherwise provide:

```markdown
## Incident brief

**Status:** investigating / identified / mitigating / monitoring / resolved
**Severity:** sev4 / sev3 / sev2 / sev1
**Impact:** ...
**Started:** ...
**Owner:** ...

### Current understanding
- Confirmed: ...
- Probable: ...
- Unknown: ...

### Timeline
| Time | Event | Evidence |
|---|---|---|

### Actions
- Done: ...
- Next: ...

### Next update
- ...
```

## Guardrails

- Do not declare root cause during an active incident unless evidence is strong.
- Do not bury impact. State user/system impact near the top.
- Avoid blame language. Focus on system behavior, evidence, and recovery.
- If customer-facing language is requested, remove internal speculation and sensitive detail.

## Related references

- `references/incident-brief-template.md`
- `references/incident-severity-model.md`
- `references/root-cause-template.md`
