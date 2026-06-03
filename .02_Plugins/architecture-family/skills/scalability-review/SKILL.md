---
name: scalability-review
description: review designs, systems, agents, plugins, APIs, databases, queues, workflows, or repositories for scalability, performance bottlenecks, reliability limits, concurrency risks, and growth constraints. use before scaling usage, adding automation, increasing agent concurrency, or releasing architecture that may face larger workloads.
---

# Scalability Review


Use this skill to identify growth limits before they become failures.

## Inputs

Collect or infer:

- Expected load now and later.
- Workload type: request/response, batch, streaming, agent loop, file processing, UI, database, or external API.
- Current bottlenecks or incidents.
- Resource constraints: CPU, memory, GPU, storage, network, API rate limits, human review.
- Consistency, latency, and availability needs.

## Procedure

1. **Define scale target** with numbers if available. If not, provide low/medium/high assumptions.
2. **Map the critical path** from input to output.
3. **Identify bottleneck classes**:
   - CPU/GPU heavy work.
   - I/O and database queries.
   - External API rate limits.
   - Synchronous waits.
   - Shared mutable state.
   - Agent coordination overhead.
   - Human approval queues.
4. **Evaluate failure modes** under load.
5. **Recommend scaling pattern**: cache, queue, shard, batch, async worker, rate limit, backpressure, pooling, or split service.
6. **Define metrics** to prove the change helped.

## Output standard

Return a scalability risk table with likelihood, impact, evidence, and recommended mitigation.

## Guardrails

- Do not optimize without a stated bottleneck or scale target.
- Prefer observability before expensive architecture changes.
- Avoid making distributed systems unless the workload justifies it.
- Escalate when load failure could cause data loss, security gaps, billing problems, or production outage.


## Handoff format

Return results using:

```markdown
# Architecture Result
## Scope
## Inputs reviewed
## Executive finding
## Decisions / recommendations
## Risks and tradeoffs
## Required follow-ups
## Files or interfaces affected
## Evidence / assumptions
```
