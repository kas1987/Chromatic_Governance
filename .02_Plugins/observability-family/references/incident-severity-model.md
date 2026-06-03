# Incident Severity Model

Use this model to classify incidents consistently. Adapt to project-specific policy when one exists.

| Severity | Meaning | Typical action |
|---|---|---|
| `sev1` | Critical widespread outage, data loss risk, security exposure, or major revenue/user impact | Immediate response, leadership/customer comms, rollback/containment likely |
| `sev2` | Major degradation or partial outage affecting important user paths or production systems | Active incident response, mitigation owner, frequent updates |
| `sev3` | Limited degradation, failed job, localized feature issue, or non-critical release problem | Assign owner, monitor, fix in normal/expedited queue |
| `sev4` | Minor issue, noisy alert, flaky check, documentation/runbook gap | Track and resolve opportunistically |

## Classification factors

- User impact: number/percentage of users, user segment, critical path.
- System impact: service unavailable, degraded, intermittent, or internal-only.
- Data risk: loss, corruption, privacy exposure, irreversible writes.
- Security risk: credential exposure, auth bypass, abuse potential.
- Duration: active, intermittent, resolved, unknown.
- Detectability: clear telemetry or blind spots.

## Rule

When impact is unknown but could be high, classify one level higher until evidence proves otherwise.
