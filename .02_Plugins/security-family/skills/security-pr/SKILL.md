---
name: security-pr
description: Perform security-focused pull request, diff, or code review for repositories, plugin changes, hooks, scripts, permissions, dependencies, tests, and configuration. Use when the user asks for a security review, pre-merge review, PR hardening pass, risky diff analysis, or approval recommendation before merging or releasing changes.
---

# Security PR Review

Review changes for concrete security regressions and missing controls. Focus on actionable findings.

## Core procedure

1. Identify the diff scope: changed files, new permissions, dependencies, scripts, hooks, configs, auth logic, data handling, and deployment changes.
2. Prioritize high-risk areas: secrets, auth, authorization, input validation, command execution, file writes, deserialization, network calls, dependency installs, logging, and prompt/tool boundaries.
3. For each issue, provide evidence, impact, exploit path, and fix.
4. Separate blocking issues from non-blocking hardening suggestions.
5. End with a merge recommendation.

## Output format

```markdown
## Security PR review

**Scope reviewed:** ...
**Recommendation:** approve / approve with follow-ups / request changes / block

### Blocking findings
| Severity | File | Issue | Evidence | Required fix |
|---|---|---|---|---|

### Non-blocking hardening
- ...

### Positive controls observed
- ...

### Follow-up tests
- ...
```

## Guardrails

- Do not approve changes you did not inspect.
- If tests or scans were not run, say `not run`.
- Avoid vague advice like “improve security”; name the exact control or code path.
- Require human approval for production credential, deployment, auth, or data-access changes.

## Related references

- `references/security-review-checklist.md`
- `references/security-risk-register-template.md`
