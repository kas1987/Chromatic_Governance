---
name: coverage-review
description: review test, eval, requirement, or workflow coverage to identify untested behaviors, missing edge cases, shallow assertions, and risk gaps. use before merge, release, refactor, agent rollout, or when judging whether existing tests are enough.
---

# Coverage Review

Use this skill to identify what is not protected yet.

## Inputs

- Requirements or acceptance criteria.
- Existing tests/evals if available.
- Changed files or affected modules.
- Known risks or previous bugs.
- Coverage reports if available.

## Procedure

1. **Map requirements to checks**.
2. **Group coverage by layer**:
   - Unit.
   - Integration.
   - End-to-end.
   - Manual.
   - Eval/rubric.
   - Security/permission.
   - Observability.
3. **Identify shallow checks**: tests that execute code but do not assert meaningful behavior.
4. **Find missing negative cases**.
5. **Rank gaps by risk**, not by count.
6. **Recommend the smallest set of new checks that materially improves confidence.**

## Output format

```markdown
# Coverage Review
## Coverage map
| Requirement / behavior | Existing check | Gap | Risk | Recommended check |
## Highest-risk gaps
## Low-value or redundant checks
## Minimum additional tests before merge
```

## Rule of thumb

Coverage percentage is supporting evidence, not the conclusion. A low-risk module with 70% meaningful coverage may be safer than a critical module with 95% shallow coverage.

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
