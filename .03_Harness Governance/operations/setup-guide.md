# Setup Guide

## 1. Register GitHub App

Recommended app name:

```text
chromatic-agent-access
```

Initial settings:

- Private/internal visibility.
- Selected repositories only.
- Webhooks disabled at first.
- Minimum permissions.

## 2. Configure secrets

GitHub Actions variables/secrets:

```text
vars.CHROMATIC_AGENT_APP_ID
secrets.CHROMATIC_AGENT_PRIVATE_KEY
```

Local broker `.env`:

```text
GITHUB_APP_ID=...
GITHUB_APP_PRIVATE_KEY_PATH=...
GITHUB_API_VERSION=2026-03-10
BROKER_DRY_RUN=true
```

## 3. Configure policy

Update:

```text
config/agents.yaml
config/repos.yaml
config/permission_profiles.yaml
```

Replace:

```text
example-org/example-repo
REPLACE_WITH_INSTALLATION_ID
@REPLACE_WITH_OWNER
```

## 4. Validate

```bash
python scripts/validate_artifact.py
python broker/tests/test_policy_engine.py
```

## 5. First live test

Use a read-only agent profile first. Confirm it can read repo metadata and list issues, but cannot write files.

## 6. First write test

Use a low-risk docs-only patch. Confirm the agent creates a branch and PR. Do not allow direct merge until controls are proven.
