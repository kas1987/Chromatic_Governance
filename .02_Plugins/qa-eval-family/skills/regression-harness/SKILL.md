---
name: regression-harness
description: design or update repeatable regression harnesses that detect behavior drift across code, plugins, prompts, agents, workflows, APIs, or CLIs. use when preserving known-good behavior, preventing bug recurrence, building smoke checks, or creating repeatable validation commands.
---

# Regression Harness

Use this skill to convert known-good behavior into repeatable checks.

## Inputs

- Behavior that must not regress.
- Recent bug, feature, or failure mode.
- Existing test commands and fixtures.
- Expected outputs, snapshots, logs, or golden files.
- Runtime constraints and CI requirements.

## Procedure

1. **Identify invariants**: behavior that must remain stable.
2. **Convert each invariant into a check**:
   - Input fixture.
   - Execution command or workflow.
   - Expected output/state.
   - Tolerance for acceptable variation.
3. **Prefer deterministic fixtures** over live services.
4. **Separate harness levels**:
   - Smoke harness: fast, broad, runs often.
   - Regression harness: targeted, runs on PR/merge.
   - Full validation harness: slower, runs before release.
5. **Define failure messages** that explain likely causes.
6. **Document how to run locally and in CI**.
7. **Add maintenance rules** for updating golden outputs.

## Output format

```markdown
# Regression Harness Plan
## Protected behaviors
## Fixture set
## Commands
## Expected outputs
## CI placement
## Golden update rule
## Failure triage
```

## Golden update rule

Golden files may only be updated when:

1. The behavior change is intentional.
2. A human or designated reviewer approves the changed expectation.
3. The decision is recorded in the decision log.

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
