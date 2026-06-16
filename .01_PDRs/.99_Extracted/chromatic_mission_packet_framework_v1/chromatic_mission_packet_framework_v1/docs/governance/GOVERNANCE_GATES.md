# Governance Gates

Every mission packet must pass the required gates for its level.

## Gate 1 — Source of Truth

The mission must name the controlling source file, PDR, issue, or user instruction.

## Gate 2 — Scope

Allowed files and forbidden files must be explicit.

## Gate 3 — Router Alignment

Each mission needs one accountable owner agent. Support agents are optional.

## Gate 4 — Evidence

Claims must be supported by path evidence, logs, tests, or explicit `inferred` labels.

## Gate 5 — Dependencies

Do not mark ready if required inputs, credentials, repo paths, or decisions are missing.

## Gate 6 — Safety and Security

Never include secrets in mission packets. Use secret references and human approval.

## Gate 7 — Acceptance Criteria

Done must be measurable.

## Gate 8 — Stop Conditions

The local agent must know when to stop and hand back control.

## Gate 9 — Validation

Tests, linters, schemas, evals, or CI checks must prove success.

## Gate 10 — Escalation

If validation fails repeatedly, scope grows, or risk changes, escalate to the next mission level or front-tier review.
