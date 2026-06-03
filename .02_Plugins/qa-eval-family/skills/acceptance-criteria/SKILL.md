---
name: acceptance-criteria
description: convert feature requests, bug reports, product requirements, technical plans, or agent tasks into objective acceptance criteria and pass/fail checks. use when defining done, clarifying scope, creating issue-ready requirements, preparing implementation gates, or translating ambiguous goals into verifiable behavior.
---

# Acceptance Criteria

Use this skill to turn intent into measurable completion gates before implementation starts.

## Inputs

Collect or infer:

- Feature, bug, refactor, or workflow goal.
- In-scope and out-of-scope behavior.
- Users, systems, APIs, files, or interfaces affected.
- Success conditions and known failure modes.
- Non-functional expectations: performance, security, accessibility, reliability, compatibility.

If key details are missing, write assumptions explicitly instead of blocking.

## Procedure

1. **Restate the goal** in one sentence.
2. **Identify actors and surfaces**: user, agent, service, CLI, API, UI, database, file, or external system.
3. **Separate criteria by layer**:
   - Functional behavior.
   - Error and edge behavior.
   - Security and permission behavior.
   - Data/state behavior.
   - Observability/logging behavior.
   - Documentation or migration behavior.
4. **Write testable criteria** using this shape:

```markdown
AC-<n>: Given <state>, when <action>, then <observable result>.
Verification: <unit/integration/e2e/manual/eval check>.
Priority: must/should/could.
```

5. **Add rejection criteria** for what must not happen.
6. **Add open questions** only where they change implementation or testing.
7. **Produce a compact ready-to-build checklist**.

## Output standard

Use clear IDs. Make every criterion observable. Avoid vague words like "fast", "clean", "good", or "robust" unless paired with a measurable threshold.

## Example output

```markdown
AC-1: Given a valid plugin directory, when validation runs, then every plugin manifest is checked and failures list the exact file path.
Verification: CLI test with one valid and one invalid fixture.
Priority: must

Reject-1: The validator must not modify plugin files during read-only validation.
```

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
