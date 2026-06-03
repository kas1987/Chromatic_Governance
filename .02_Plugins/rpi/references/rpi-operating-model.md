# RPI Operating Model

RPI is the delivery lifecycle family. It handles scoped work from ambiguity through planning, implementation, validation, review, and handoff.

## Default flow

1. `discovery` - clarify the mission and boundaries.
2. `plan` - sequence work and define gates.
3. `pre-mortem` - identify likely failure modes for risky work.
4. `implement` or `quick-execute` - make changes.
5. `test` and `validation` - gather evidence.
6. `review` - judge readiness.
7. `handoff-ready` - package continuation state.
8. `post-mortem` - capture lessons when needed.

## Escalation rules

- Use `security-family` for secrets, permissions, auth, supply-chain, or prompt-injection concerns.
- Use `architecture-family` for boundary, API, migration, or structural design questions.
- Use `qa-eval-family` for durable test/eval harnesses and golden cases.
- Use `release-family` for deployment, changelog, rollback, and post-release gates.
- Use `context-family` for session memory, source-of-truth updates, and continuity.
- Use `frontend-family` for UI systems, assets, dashboards, CSS/Tailwind, local apps, and 3D asset workflows.
