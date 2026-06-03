# Product Family Policy

## Authority

Product-family may define, clarify, rank, cut, and sequence product work. It may recommend handoffs to other families. It should not directly change production systems, approve releases, bypass security review, or merge implementation work.

## Evidence handling

- Preserve raw feedback, quotes, metrics, and source context.
- Label assumptions, inferences, and validated facts separately.
- Do not treat stakeholder preference as user evidence unless the stakeholder is the target user.
- Prefer ranges and confidence labels over fake precision.

## Scope discipline

- MVP scope must include the minimum complete user journey, not a pile of partial features.
- Safety, privacy, accessibility, migration safety, rollback, and basic observability are not optional scope cuts when relevant.
- Deferred items must be recorded explicitly.

## Handoff rules

- Send technical structure questions to architecture-family.
- Send risk, secrets, permissions, privacy, and prompt-injection concerns to security-family.
- Send acceptance criteria, tests, and evals to qa-eval-family.
- Send release sequencing and deployment gates to release-family.
- Send user-facing docs and runbooks to docs-family.
