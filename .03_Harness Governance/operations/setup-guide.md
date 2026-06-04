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

Optional external provider keys (set only if you want cloud-provider routing):

```text
secrets.OPENAI_API_KEY
secrets.ANTHROPIC_API_KEY
secrets.GEMINI_API_KEY
```

Local broker `.env`:

```text
GITHUB_APP_ID=...
GITHUB_APP_PRIVATE_KEY_PATH=...
GITHUB_API_VERSION=2026-03-10
BROKER_DRY_RUN=true
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
OLLAMA_LOCAL_BASE_URL=http://127.0.0.1:11434
OLLAMA_REMOTE_BASE_URL=http://desktop.local:11434
OLLAMA_MODEL_C1=llama3.2:3b
OLLAMA_MODEL_C2=qwen2.5-coder:14b
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
kas1987/Chromatic_Governance
REPLACE_WITH_INSTALLATION_ID
@REPLACE_WITH_OWNER
```

Provider config template:

```text
config/providers.example.yaml
```

Copy and adjust for your runtime if needed.

## 4. Validate

```bash
python scripts/validate_artifact.py
python broker/tests/test_policy_engine.py
```

GitHub secret/variable checks:

```bash
gh secret list --repo kas1987/Chromatic_Governance
gh variable list --repo kas1987/Chromatic_Governance
```

Ollama checks:

```bash
curl http://127.0.0.1:11434/api/tags
curl http://desktop.local:11434/api/tags
```

## 5. First live test

Use a read-only agent profile first. Confirm it can read repo metadata and list issues, but cannot write files.

## 6. First write test

Use a low-risk docs-only patch. Confirm the agent creates a branch and PR. Do not allow direct merge until controls are proven.
