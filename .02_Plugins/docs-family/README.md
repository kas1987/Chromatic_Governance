# Docs Family

Documentation operations for README, API docs, runbooks, developer guides, troubleshooting, diagrams, doc audits, and documentation synchronization.

## Purpose

Use this family when agents need to create, repair, audit, or synchronize documentation with the current implementation and operating model.

## Skills

- `readme-refresh` - Refresh README files for orientation, quick start, usage, validation, and doc navigation.
- `api-docs` - Document interfaces, commands, schemas, endpoints, examples, errors, and permissions.
- `runbook` - Create operational procedures with prechecks, verification, rollback, and escalation.
- `dev-guide` - Build setup, repo map, workflow, testing, and contribution guides.
- `troubleshooting` - Convert recurring failures into symptom-to-fix diagnosis paths.
- `diagram-plan` - Plan architecture, flow, deployment, sequence, data, and workflow diagrams.
- `doc-audit` - Find stale docs, contradictions, broken links, missing owners, and implementation drift.
- `doc-sync` - Update affected docs after code, config, API, release, or workflow changes.

## References

- `references/documentation-operating-model.md`
- `references/readme-template.md`
- `references/api-docs-template.md`
- `references/runbook-template.md`
- `references/dev-guide-template.md`
- `references/troubleshooting-template.md`
- `references/diagram-plan-template.md`
- `references/doc-audit-template.md`
- `references/doc-sync-checklist.md`
- `references/doc-quality-checklist.md`

## Agents

- `docs-maintainer` - Keeps docs aligned with implementation, operations, and user-facing behavior.

## Operating rule

Do not make documentation sound more certain than the repository proves. When code, tests, configs, and docs disagree, report the conflict and mark the required owner review.

## Status

Core skills implemented. Scripts and hooks remain lightweight advisory utilities.
