# PDR: GitHub Agent Access Broker

## 1. Decision summary

Build a GitHub App-backed access broker that grants AI agents scoped, short-lived repository access based on identity, task, repository, and permission profile. The broker is the only component that may mint or expose GitHub installation tokens to agents.

## 2. Problem statement

AI agents need repository access for inspection, triage, patching, PR creation, and governance work. Directly giving agents personal access tokens or broad secrets creates unacceptable risk:

- Weak attribution.
- Excessive permissions.
- Difficult revocation.
- Secret sprawl.
- Poor auditability.
- Direct-write risk to protected branches.

## 3. Goals

| Goal | Description |
|---|---|
| Least privilege | Agents receive only the minimum permissions required for a task. |
| Short-lived access | Tokens are generated on demand and expire. |
| PR-only writes | Agent patches flow through branches and pull requests. |
| Auditability | Every token request and write path is logged. |
| Repo selectivity | Access is limited to approved repositories. |
| Agent identity | Actions map back to named agents and task IDs. |
| Human override | Admin/repo setting changes remain human-controlled. |

## 4. Non-goals

- Replacing GitHub branch protection.
- Replacing CI/security scanning.
- Giving agents unrestricted org administration.
- Running arbitrary untrusted code without sandboxing.
- Eliminating human review for high-impact changes.

## 5. Recommended architecture

```text
[Agent]
  -> [Agent Router]
    -> [Repo Access Broker]
      -> [Policy Engine]
      -> [GitHub App Token Issuer]
      -> [Audit Log]
        -> [GitHub API]
```

## 6. Access model

### Agent classes

| Class | Example | Default access |
|---|---|---|
| Scout | Repo discovery / read-only auditor | Read contents, PRs, issues |
| Triage | Issue organizer | Read contents, write issues/labels |
| Patch | CodeSentinel / repair agent | Read/write contents through branch + PR |
| Maintainer | CI/check/status agent | Checks/statuses/actions as needed |
| Admin | Human only | Settings, secrets, app permissions |

### Write policy

All agent writes must satisfy:

```text
allowed_agent == true
allowed_repo == true
requested_permission <= profile_permission
task_id present
branch_prefix matches policy
base_branch protected from direct push
pull_request_required == true
```

## 7. Permission baseline

Start with the following GitHub App repository permissions:

| Permission | Baseline | Notes |
|---|---|---|
| Metadata | Read | Required by GitHub. |
| Contents | Read | Upgrade to write only for patch agents. |
| Pull requests | Read/write | Needed to open PRs. |
| Issues | Read/write | Needed for triage and agent reports. |
| Checks | Read/write optional | For validation agents. |
| Commit statuses | Read/write optional | For status reporting. |
| Actions | Read optional | For workflow monitoring. |
| Administration | No access | Human-only. |
| Secrets | No access | Human-only. |

## 8. Threat model

| Threat | Risk | Control |
|---|---|---|
| Agent prompt injection causes malicious commit | High | PR-only writes, diff review, deny direct main push. |
| Token leakage | High | Short-lived tokens, broker-only minting, no token persistence. |
| Overbroad app permissions | High | Selected repositories, minimum app permissions, token-level permission narrowing. |
| Rogue agent requests write access | Medium/high | Policy engine deny-by-default, task ID requirement. |
| Secret exposure through logs | High | Redaction, no token logging, audit metadata only. |
| Supply chain poisoning | High | CI checks, dependency review, signed/attributed commits where possible. |
| Repo-wide destructive edits | High | branch restrictions, file allow/deny lists, PR review. |

## 9. Operational controls

- Rotate GitHub App private key on incident or scheduled cadence.
- Revoke/suspend app installation if broker is compromised.
- Require branch protection and at least one review before merging.
- Enable required CI checks for agent PRs.
- Log all token requests to JSONL or SIEM.
- Maintain agent allowlist and repo allowlist.

## 10. Acceptance criteria

A deployment is acceptable when:

- GitHub App is installed only on selected repos.
- Broker can issue read-only tokens for scout agents.
- Broker can deny unauthorized write requests.
- Patch agent can create a branch and PR without pushing to main.
- Audit logs capture agent ID, repo, permission profile, task ID, and decision.
- Validation workflow runs on agent PRs.
- Human-only permissions are not granted to agents.

## 11. Open questions

- Which repos are first-class targets?
- Which agents need write access immediately?
- Should broker run locally, in GitHub Actions, or as an internal service?
- Should commits use verified signatures or app attribution only?
- Should PR merges remain 100% human-triggered?

## 12. Decision

Proceed with GitHub App + broker architecture. Avoid shared PATs except as temporary emergency fallback.
