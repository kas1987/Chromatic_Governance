# Release Health Signals

Use these signals when checking whether a release is safe to continue, expand, hold, or roll back.

## Core signals

- Error rate versus pre-release baseline.
- p95/p99 latency versus pre-release baseline.
- Throughput or conversion path drop-off.
- Crash/retry/timeout increase.
- Queue depth, saturation, memory, CPU, GPU, or database pressure.
- Failed background jobs or migration errors.
- Support/user reports.
- Test/eval regression after release.
- Alert volume and severity.
- Cost spike or runaway usage.

## Decision mapping

| Signal state | Suggested action |
|---|---|
| All core signals normal | Continue rollout or monitor normally |
| Minor metric movement without user impact | Watch and set next checkpoint |
| Confirmed degradation on important path | Hold rollout and investigate |
| SLO breach, data risk, security exposure, or major outage | Roll back or contain immediately |
| Missing key telemetry | Hold expansion until visibility improves |
