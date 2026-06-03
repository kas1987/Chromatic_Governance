# Governance Best Practices

## Core principles

1. **Deny by default.** Access must be explicitly granted by agent, repo, action, and permission profile.
2. **Separate read from write.** Read access should be easy to grant; write access should require a task ID and branch/PR constraints.
3. **Use short-lived tokens.** Do not store installation tokens in local agent config.
4. **Use PR-only changes.** No direct pushes to protected branches.
5. **Log decisions, not secrets.** Audit who requested what, why, and whether it was allowed.
6. **Keep admin human-only.** Repo settings, secrets, billing, and app configuration are not agent-owned.
7. **Review destructive work.** Deletes, migrations, dependency changes, auth changes, and workflow changes are high-risk.

## Preferred access sequence

```text
read -> plan -> approval/policy check -> write branch -> open PR -> CI -> review -> merge
```

## Recommended branch prefixes

| Agent | Branch prefix |
|---|---|
| CodeSentinel | `agent/codesentinel/` |
| RepoScout | `agent/reposcout/` |
| Auditor | `agent/auditor/` |
| Janitor | `agent/janitor/` |
| Human supervised | `human-supervised/` |

## Commit message convention

```text
<agent-name>: <imperative summary>

Task-ID: <task-id>
Agent: <agent-id>
Policy: <permission-profile>
Risk: low|medium|high
```

Example:

```text
CodeSentinel: add access broker policy validation

Task-ID: GOV-001
Agent: codesentinel
Policy: patch_standard
Risk: medium
```

## Required PR metadata

Every agent PR should include:

- Purpose.
- Files changed.
- Risk level.
- Validation performed.
- Rollback plan.
- Agent identity.
- Linked issue/task.

## High-risk files

Require human review for changes to:

```text
.github/workflows/**
Dockerfile
docker-compose*.yml
package-lock.json
requirements*.txt
pyproject.toml
infra/**
security/**
config/**/secrets*
*.pem
*.key
.env*
```

## Merge rule

Agents may open PRs. Humans or specifically approved automation may merge after all controls pass.
