# GitHub Agent Access Governance Kit

**Purpose:** A drop-in governance and implementation starter kit for letting AI agents access GitHub repositories safely through a GitHub App, short-lived installation tokens, least-privilege permission profiles, and PR-only change control.

## Executive recommendation

Use this kit when multiple agents need to inspect, patch, triage, or govern repositories. Do **not** give each agent a long-lived personal token. Put a controlled broker between agents and GitHub.

```text
Agent -> Agent Router -> Repo Access Broker -> GitHub App installation token -> GitHub API / branch / PR
```

## What this package contains

| Area | Files |
|---|---|
| Product/design record | `pdr/PDR-github-agent-access-broker.md` |
| Governance | `governance/*.md` |
| Policy config | `config/*.yaml` |
| Broker scaffold | `broker/src/*.py`, `broker/tests/*.py` |
| GitHub workflow examples | `.github/workflows/*.yml` |
| Security and operations | `security/*.md`, `operations/*.md` |
| Agent handoffs | `handoffs/*.md` |
| Registry/manifest | `artifact_manifest.json`, `registry/quilt_registry.json` |

## Intended repo location

Recommended target path inside a repo:

```text
/governance/github-agent-access/
```

Or as a standalone internal repo:

```text
github-agent-access-governance-kit/
```

## First implementation move

1. Register a private GitHub App.
2. Install it only on selected repositories.
3. Store the App ID and private key in your secure secret store or GitHub Actions secrets.
4. Configure `config/agents.yaml`, `config/repos.yaml`, and `config/permission_profiles.yaml`.
5. Run the broker locally in dry-run mode first.
6. Allow writes only through branch + pull request flow.

## Non-negotiable governance rules

- No agent gets a broad long-lived PAT by default.
- No agent pushes directly to `main`.
- Every write action must map to an agent identity, task ID, branch, and audit event.
- Tokens are generated on demand and expire quickly.
- The broker must deny by default.
- Human/admin credentials remain outside agent runtime.

## Validation

Run:

```bash
python scripts/validate_artifact.py
python broker/tests/test_policy_engine.py
```

## Status

Version: `0.1.0`

This is a starter kit, not a fully hardened production security boundary. Treat it as scaffolding for your agent governance layer.
