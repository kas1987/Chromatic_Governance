# Architecture Family

Design governance for architecture review, technical design docs, ADRs, interface contracts, module boundaries, migrations, scalability, and technical debt.

## Purpose

Use this plugin family when agents need to decide whether a system should be built, changed, split, migrated, or constrained before implementation. This family keeps fast implementation from turning into brittle structure.

## Skills

- `architecture-review` - Evaluate system design, risks, boundaries, and maintainability.
- `design-doc` - Produce build-ready technical design documents.
- `adr-create` - Capture durable architecture decisions.
- `interface-contracts` - Define stable boundaries between systems, modules, agents, tools, or files.
- `module-boundaries` - Map and enforce dependency direction and safe edit zones.
- `migration-plan` - Stage risky changes with validation, rollback, and stop conditions.
- `scalability-review` - Find growth, performance, concurrency, and reliability risks.
- `technical-debt-map` - Rank debt and convert it into actionable remediation work.

## References

- `references/architecture-review-checklist.md`
- `references/design-doc-template.md`
- `references/adr-template.md`
- `references/interface-contract-template.md`
- `references/module-boundary-rules.md`
- `references/migration-plan-template.md`
- `references/technical-debt-scoring.md`

## Agents

- `architect` - Evaluates system design, boundaries, scalability, and long-term maintainability.

## Operating rule

Prefer the smallest architecture that preserves clear ownership, testability, migration safety, and future change. Escalate security-sensitive findings to `security-family` and measurable pass/fail checks to `qa-eval-family`.

## Status

Core skill implementation complete. Skills are ready for use and should be refined after real project runs.
