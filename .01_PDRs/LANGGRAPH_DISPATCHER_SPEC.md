# LangGraph Dispatcher Spec

Last updated: 2026-06-04

## Purpose

Define a lock-safe, auditable multi-agent dispatcher that processes review-intake queue items through scoped execution, validation, and resolution.

## Implementation Asset

- Dispatcher scaffold: `.03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py`

Example commands:

```powershell
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --check-langgraph
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --queue-id "NW-REVIEW-INTAKE-001"
```

## Scope

- Dispatcher design for queue -> lock -> agent -> validate -> resolve
- Integrates with existing queue and lock artifacts
- Does not replace existing deterministic policy scripts

## Inputs

### Queue item contract (minimum)

```json
{
  "queue_id": "q-20260604-001",
  "pr_number": 1,
  "repo": "kas1987/Chromatic_Governance",
  "branch": "claude/test-coverage-analysis-XoxC1",
  "finding_type": "review_comment|check_failure|governance_drift",
  "confidence": 0.92,
  "target_files": [".01_PDRs/pdr_zip_intake.py"],
  "resolution_policy": "code_change_with_validation"
}
```

## State Model

- `queued`: Item is ready for dispatch
- `lock_pending`: Dispatcher is attempting branch lock acquisition
- `locked`: Branch lock acquired
- `planning`: Agent generates mission plan and patch intent
- `executing`: Agent applies scoped edits
- `validating`: Validation checks run
- `resolving`: Resolution artifacts/comments prepared
- `completed`: Success path complete
- `failed_retryable`: Failure with retry policy available
- `failed_terminal`: Failure requiring human intervention

## Graph Nodes

1. `LoadQueueItem`
- Reads next eligible queue item from `.agents/review-intake/next-work.queue.json`.

2. `AcquireBranchLock`
- Uses lock mechanism compatible with `.agents/review-intake/locks/`.
- If lock unavailable, transition to `failed_retryable` with backoff.

3. `BuildMissionPacket`
- Produces bounded execution packet:
  - allowed files
  - prohibited operations
  - required validations
  - rollback strategy

4. `DispatchAgent`
- Executes selected agent against mission packet.
- Enforces scoped write boundaries.

5. `RunValidation`
- Runs required checks (lint/test/script-specific checks).
- Collects structured results.

6. `ResolutionComposer`
- Generates resolution body and update artifacts only if validations pass.

7. `ReleaseLock`
- Always execute in finally path.

8. `TelemetrySink`
- Emits run trace, duration, retries, failure class, and decision path.

## Routing Rules

- `confidence < threshold`: route to manual-review lane before agent dispatch.
- `lock_acquire_failed`: retry with exponential backoff and max attempts.
- `validation_failed`: branch to retry policy or manual intervention based on failure class.
- `policy_violation_detected`: immediate terminal failure and escalation.

## Guardrails

- Single mutating writer per PR branch via lock requirement.
- No state mutation without recorded queue_id, actor, and timestamp.
- No completion state if validation did not pass.
- All failures must include remediation hint for operators.

## Retry Policy

- Retryable classes:
  - transient lock contention
  - transient tool/network failure
  - flaky non-deterministic validation (bounded retries)
- Non-retryable classes:
  - policy violation
  - out-of-scope file mutation attempt
  - deterministic test failure tied to known regression

## Telemetry Schema (minimum)

```json
{
  "trace_id": "uuid",
  "queue_id": "q-20260604-001",
  "branch": "claude/test-coverage-analysis-XoxC1",
  "state_path": ["queued", "locked", "executing", "validating", "completed"],
  "attempt": 1,
  "duration_ms": 18234,
  "result": "completed|failed_retryable|failed_terminal",
  "failure_class": null
}
```

## Integration Points

- Queue source: `.agents/review-intake/next-work.queue.json`
- Findings stream: `.agents/review-intake/review-findings.jsonl`
- Branch locks: `.agents/review-intake/locks/`
- Resolution logs: existing review-resolution artifacts
- Optional trace backend: LangSmith or equivalent

## Acceptance Checks

1. Dispatcher never executes mutating path without lock acquisition.
2. Validation gate blocks resolution publish on failed checks.
3. Retries follow policy and stop at max attempts.
4. Every run has complete telemetry with trace_id and state_path.
5. Manual lane receives low-confidence or policy-violating items.

## Rollout Plan

1. Implement read-only simulation mode over historical queue items.
2. Enable lock + planning + telemetry with no mutation.
3. Enable scoped mutation for a narrow finding class.
4. Expand to full patch/validate/resolve loop after stability window.
