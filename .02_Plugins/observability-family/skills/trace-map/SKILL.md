---
name: trace-map
description: Map request, job, workflow, event, agent, or tool execution traces across components to identify where time, failure, retries, state transitions, or responsibility shifts occur. Use when debugging distributed flows, multi-agent execution, asynchronous jobs, API chains, pipelines, or unclear handoffs between services/tools.
---

# Trace Map

Turn scattered trace or workflow evidence into a component-level path.

## Core procedure

1. Identify the trace unit: request ID, job ID, user action, deployment, agent run, message, event, or task.
2. List every known hop in order: entrypoint, service/tool, queue, dependency, storage, external API, callback, and exit.
3. Attach timing, status, retry count, error, and owner/component to each hop when available.
4. Identify missing spans, blind spots, long waits, retries, failed handoffs, and ambiguous ownership.
5. Recommend instrumentation or design changes needed to make the path observable.
6. Produce the smallest next diagnostic query/check.

## Output structure

Use `references/trace-map-template.md` for formal trace maps. Otherwise provide:

```markdown
## Trace map

**Trace unit:** ...
**Status:** complete / partial / insufficient evidence
**Primary bottleneck/failure:** ...

### Flow
| Step | Component/tool | Input | Output | Status | Duration |
|---:|---|---|---|---|---:|

### Blind spots
- ...

### Next diagnostic checks
1. ...

### Instrumentation improvements
- ...
```

## Guardrails

- Do not fill missing spans with guesses; mark gaps.
- Keep causal claims tied to timing, error, retry, or state evidence.
- For agent workflows, include tool calls, file writes, approvals, and handoff boundaries.
- Flag sensitive payloads before suggesting trace sharing.

## Related references

- `references/trace-map-template.md`
- `references/observability-operating-model.md`
- `references/log-triage-template.md`
