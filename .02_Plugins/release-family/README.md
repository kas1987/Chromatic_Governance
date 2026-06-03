# Release Family

Release planning, changelogs, versioning, rollout, deployment checks, rollback, and post-release monitoring.

## Purpose

Use this family when finished work needs to become a safe release. It should turn implementation output into release decisions, version updates, deployment checklists, rollback plans, and post-release monitoring summaries.

## Skills

- `release-plan` - Build a scoped go/no-go plan with readiness gates and sequence.
- `changelog` - Generate developer-facing change history.
- `version-bump` - Recommend or prepare semantic version updates.
- `release-notes` - Draft user-facing or stakeholder-facing release notes.
- `migration-check` - Review database, config, schema, API, and dependency migrations.
- `rollback-plan` - Create executable rollback and recovery plans.
- `deploy-checklist` - Build pre-deploy, deploy, post-deploy, and rollback readiness checklists.
- `post-release-monitor` - Define and summarize release health signals after deployment.

## Agents

- `release-manager` - Controls release gates, versioning, rollback plans, and post-release monitoring.

## References

- `references/release-gate-model.md`
- `references/release-plan-template.md`
- `references/changelog-format.md`
- `references/versioning-policy.md`
- `references/release-notes-template.md`
- `references/migration-check-template.md`
- `references/rollback-plan-template.md`
- `references/deploy-checklist-template.md`
- `references/post-release-monitor-template.md`

## Operating rule

Do not mark a release ready merely because implementation is complete. Require evidence for scope, build, tests/evals, security, migrations, observability, rollback, and communication. If evidence is missing, mark the release `conditional`, `no-go`, or `blocked`.

## Status

Core skill procedures implemented. Scripts remain advisory and should be reviewed before enablement in production workflows.
