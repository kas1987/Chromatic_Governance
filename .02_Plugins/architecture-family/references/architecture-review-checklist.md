# Architecture Review Checklist

Use this checklist for system-level reviews. Not every item applies; focus on the items that materially affect the requested scope.

## 1. Purpose and fit

- The design has a clear user or system outcome.
- The chosen architecture is no more complex than the problem requires.
- Non-goals are explicit enough to stop scope creep.
- The design aligns with current constraints instead of imagined future scale.

## 2. Boundaries and ownership

- Components have clear responsibilities.
- State has a single owner or an explicit synchronization rule.
- Data, API, file, plugin, and agent boundaries are visible.
- Consumers do not rely on producer internals.
- Shared utilities do not become unowned dumping grounds.

## 3. Interfaces and contracts

- Inputs, outputs, errors, side effects, and versioning are specified.
- Contract changes include migration or compatibility plans.
- Idempotency is defined for retryable actions.
- External dependency failures are handled.

## 4. Security and permissions

- Trust boundaries are explicit.
- Secrets are not stored in code, docs, prompts, logs, or generated artifacts.
- Agent/tool permissions are least-privilege.
- Prompt-injection and untrusted-content paths are considered.

## 5. Reliability and operations

- Failure modes are named.
- Rollback or recovery is possible for risky changes.
- Observability exists for critical flows.
- Work can be tested locally or in a safe environment.

## 6. Maintainability

- The design is easy to explain to a new contributor or fresh agent.
- Module dependencies are directional and enforceable.
- Documentation and ADRs capture durable decisions.
- Technical debt created by the design is named and accepted.

## Severity guidance

| Severity | Meaning | Action |
|---|---|---|
| Blocker | unsafe to build or release | stop and redesign |
| High | likely major rework or operational risk | fix before implementation |
| Medium | manageable debt or ambiguity | track with owner |
| Low | polish or future improvement | defer if needed |
