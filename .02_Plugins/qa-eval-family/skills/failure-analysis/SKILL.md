---
name: failure-analysis
description: analyze failing tests, eval failures, broken agent runs, flaky behavior, regressions, CI failures, bug reports, or validation gaps. use when diagnosing why a workflow failed and deciding whether to fix code, tests, prompts, data, tools, or expectations.
---

# Failure Analysis

Use this skill to convert failure noise into a clear diagnosis and repair path.

## Inputs

- Failure output, logs, screenshots, traces, test results, or transcript.
- Expected behavior.
- Recent changes.
- Environment details.
- Reproduction steps if available.

## Procedure

1. **Classify failure type**:
   - Product/requirement mismatch.
   - Code defect.
   - Test defect.
   - Fixture/data issue.
   - Environment/config issue.
   - Flaky timing/concurrency issue.
   - Agent/prompt/tool-use issue.
   - Security/permission boundary issue.
2. **Extract evidence** from logs or output before hypothesizing.
3. **Build a likely-cause ranking** with confidence levels.
4. **Define the smallest reproduction**.
5. **Separate immediate fix from prevention**.
6. **Recommend validation checks** to prove the fix.
7. **Record any new regression or golden case needed.**

## Output format

```markdown
# Failure Analysis
## Symptom
## Expected vs actual
## Evidence
## Likely causes
| Rank | Cause | Confidence | Evidence | How to verify |
## Immediate fix
## Prevention / regression checks
## Escalations
```

## Confidence labels

Use:

- High: directly supported by logs or deterministic repro.
- Medium: plausible with partial evidence.
- Low: hypothesis needing investigation.

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
