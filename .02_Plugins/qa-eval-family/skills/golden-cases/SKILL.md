---
name: golden-cases
description: create and maintain known-good examples for tests, evals, prompts, CLIs, APIs, plugin workflows, and agent outputs. use when the user needs canonical fixtures, expected outputs, regression examples, or high-quality reference cases.
---

# Golden Cases

Use this skill to define canonical examples that future agents and tests can reuse.

## Inputs

- Workflow, skill, feature, or agent being protected.
- Real or synthetic examples.
- Expected output format.
- Known edge cases or previous failures.
- Whether examples may include sensitive data.

## Procedure

1. **Select cases by coverage value**, not volume.
2. **Create categories**:
   - Minimal valid case.
   - Typical case.
   - Complex case.
   - Edge case.
   - Failure/invalid case.
   - Adversarial case if relevant.
3. **Write each golden case with stable fields**:

```markdown
case_id:
category:
input:
expected_output:
must_include:
must_not_include:
notes:
```

4. **Sanitize sensitive data**. Use fake tokens, fake emails, and fake customer data.
5. **Define update policy** so golden cases do not drift silently.
6. **Link each golden case to acceptance criteria or regression checks when possible.**

## Output format

```markdown
# Golden Cases
## Coverage goals
## Cases
## Update policy
## Sensitive-data notes
## Mapping to tests/evals
```

## Quality bar

A golden case should be boring, explicit, and hard to misinterpret. Fancy examples are less valuable than stable examples.

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
