# QA Eval Family

Testing, acceptance criteria, regression harnesses, LLM/agent evals, golden cases, failure analysis, coverage review, and controlled chaos testing.

## Purpose

This plugin family turns agent work into measurable quality gates. Use it after context and security controls are established, and before merge, release, large refactor, or agent rollout.

## Implemented skills

- `acceptance-criteria` - Convert ambiguous work into observable pass/fail criteria.
- `test-plan` - Build risk-based test plans across unit, integration, e2e, manual, and eval layers.
- `regression-harness` - Protect known-good behavior with repeatable checks.
- `eval-suite` - Evaluate LLM, prompt, plugin, and agent behavior.
- `golden-cases` - Create canonical known-good examples and fixtures.
- `failure-analysis` - Diagnose failed tests, CI, evals, and agent runs.
- `coverage-review` - Find untested behavior and shallow assertions.
- `chaos-test` - Plan safe resilience and fault-injection checks.

## References

- `references/qa-gate-model.md`
- `references/test-plan-template.md`
- `references/eval-suite-template.md`
- `references/regression-harness-template.md`
- `references/failure-analysis-template.md`
- `references/coverage-review-template.md`
- `references/golden-case-schema.md`

## Agent

- `qa-evaluator` - Defines and runs quality gates, tests, regressions, and eval plans.

## Default posture

- Do not call work complete without evidence.
- Prefer small repeatable checks over broad subjective review.
- Tie tests and evals to acceptance criteria whenever possible.
- Treat security, data loss, auth, deployment, and agent tool access as high-risk by default.
