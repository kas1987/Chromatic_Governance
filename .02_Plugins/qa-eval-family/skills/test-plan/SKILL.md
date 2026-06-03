---
name: test-plan
description: design practical test plans for code changes, plugins, agents, workflows, CLIs, APIs, UIs, data migrations, or release candidates. use when the user needs a structured unit/integration/e2e/manual test plan, risk-based testing scope, or implementation-ready QA checklist.
---

# Test Plan

Use this skill to build a risk-based test plan that a developer or agent can execute.

## Inputs

- Change summary or requirements.
- Files, modules, commands, routes, UI flows, or agents affected.
- Acceptance criteria if available.
- Known risks, dependencies, and constraints.
- Test framework or environment if known.

## Procedure

1. **Define test objective**: what confidence the plan must produce.
2. **Map affected surfaces**:
   - Code units.
   - Integration boundaries.
   - UI/CLI/API surfaces.
   - Data/storage surfaces.
   - Agent/tool permission surfaces.
3. **Choose test depth by risk**:
   - Low risk: smoke + targeted unit tests.
   - Medium risk: unit + integration + regression checks.
   - High risk: unit + integration + e2e + negative tests + rollback verification.
4. **Write test cases** with setup, action, expected result, and owner.
5. **Include negative and edge cases** before happy-path repetition.
6. **Define exit criteria**: what must pass before merge/release.
7. **List fixtures and mocks** needed.
8. **Mark manual checks** only when automation is unreasonable.

## Output format

```markdown
# Test Plan
## Objective
## Scope
## Risk rating
## Test matrix
| ID | Layer | Scenario | Setup | Expected result | Priority | Automated? |
## Fixtures / data
## Exit criteria
## Known gaps
```

## Quality bar

A good test plan lets another agent start implementing tests without re-asking what to test.

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
