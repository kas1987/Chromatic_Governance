# Codex / Agent Handoff

## Mission

Implement and harden the GitHub Agent Access Broker from this governance kit.

## Constraints

- Do not commit secrets.
- Do not use a shared PAT.
- Preserve PR-only write workflow.
- Keep policy deny-by-default.
- Add tests before enabling live write mode.

## Tasks

1. Replace example repo names in config.
2. Implement `broker/src/token_issuer.py` using PyJWT + requests or preferred SDK.
3. Add real token permission narrowing.
4. Add CLI command for access requests.
5. Add structured JSON logs.
6. Add path-risk checks before write operations.
7. Add tests for blocked paths and high-risk paths.
8. Add docs for local and GitHub Actions operation.

## Acceptance

- `python scripts/validate_artifact.py` passes.
- `python broker/tests/test_policy_engine.py` passes.
- Read-only access works.
- Unauthorized write access is denied.
- Patch agent can create branch + PR only.
