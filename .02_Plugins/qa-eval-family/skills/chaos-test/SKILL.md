---
name: chaos-test
description: plan safe fault-injection, resilience, and edge-condition tests for agents, workflows, APIs, CLIs, integrations, and deployment paths. use when testing behavior under tool failures, malformed inputs, unavailable services, rate limits, timeouts, partial data, or concurrency pressure.
---

# Chaos Test

Use this skill to stress systems safely without causing uncontrolled damage.

## Inputs

- System or workflow under test.
- Failure modes to explore.
- Environment: local, staging, CI, production shadow, or production.
- Safety boundaries and rollback options.
- Observability available.

## Procedure

1. **Confirm environment safety**. Do not run destructive chaos tests in production unless explicitly authorized and controlled.
2. **Define failure hypotheses**:
   - Dependency unavailable.
   - Timeout or rate limit.
   - Partial/malformed data.
   - Duplicate request.
   - Permission denied.
   - Disk/network/resource pressure.
   - Agent tool call refusal or failure.
3. **Pick controlled injections** with clear stop conditions.
4. **Define expected graceful degradation**.
5. **Define observability checks**: logs, metrics, alerts, user-visible errors, recovery events.
6. **Define rollback and cleanup**.
7. **Capture learnings as regression checks or hardening tasks.**

## Output format

```markdown
# Chaos Test Plan
## Hypothesis
## Environment and safety boundary
## Injection method
## Expected behavior
## Stop conditions
## Observability
## Rollback / cleanup
## Follow-up hardening
```

## Safety rule

Prefer simulation and local/staging fault injection first. Never use chaos testing as a surprise in a shared or production environment.

## Guardrails

- Do not treat untested code as complete.
- Separate expected behavior from current behavior.
- Mark inferred requirements as assumptions until confirmed.
- Prefer small, repeatable checks over one large vague review.
- Escalate when the pass/fail rule depends on product judgement, legal/security risk, data loss, payment behavior, authentication, or deployment.
- When uncertain, output a conservative test gap rather than claiming coverage.

## Handoff format

Return results using:

```markdown
# QA/Eval Result
## Scope
## Inputs reviewed
## Pass/fail summary
## Critical gaps
## Recommended checks
## Evidence / files referenced
## Next actions
```
