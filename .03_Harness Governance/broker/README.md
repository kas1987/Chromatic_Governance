# Repo Access Broker Scaffold

This is a minimal Python scaffold for a GitHub App token broker. It intentionally focuses on policy decisions and audit structure. The actual token issuance function is stubbed so you can wire it to PyJWT/requests or Octokit depending on your runtime preference.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install pyyaml
```

## Validate policy engine

```bash
python broker/tests/test_policy_engine.py
```

## Integration notes

- Keep private keys outside the repo.
- Never log installation tokens.
- Return tokens only to trusted agent runtimes.
- Prefer running this broker in a controlled local service or GitHub Actions job.
