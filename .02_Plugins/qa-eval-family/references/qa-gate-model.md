# QA Gate Model

Use this model to decide how strict the quality gate should be.

## Gate levels

| Level | Use when | Required checks |
|---|---|---|
| Q0 smoke | Tiny low-risk edits, docs, formatting | Basic run/validation, no obvious regressions |
| Q1 standard | Normal feature or bug fix | Acceptance criteria, targeted tests, regression check |
| Q2 high risk | Auth, payments, data writes, migrations, agent tools, security-sensitive code | Unit + integration + negative tests + rollback or recovery check |
| Q3 release | Pre-release or broad refactor | Full regression, coverage review, docs/runbook, known gaps approved |

## Default rule

If the change affects secrets, auth, permissions, money, user data, data deletion, deployment, or agent tool access, default to Q2 or Q3.

## Exit language

Use one of:

- **Pass**: required checks pass and no blocking gaps remain.
- **Conditional pass**: acceptable only if listed follow-ups are completed before merge/release.
- **Fail**: blocking gaps remain.
- **Blocked**: required evidence is unavailable.
