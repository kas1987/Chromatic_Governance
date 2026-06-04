# Contributing

Thanks for contributing to Chromatic Governance.

## Before You Start

- Open an issue for significant changes.
- Keep changes scoped and auditable.
- Avoid mixing unrelated refactors with behavior changes.

## Development Flow

1. Create or use a feature branch.
2. Implement changes with tests or validation updates.
3. Run local checks before pushing.
4. Open or update the pull request with a clear summary.

## Validation Expectations

At minimum, run checks relevant to files you changed. For orchestration dispatch updates:

```powershell
python -m pytest ".03_Harness Governance/scripts/tests/test_dispatch.py" -q
```

## Commit Guidance

- Use descriptive commit messages.
- Do not include generated artifacts unless intentionally versioned.
- Do not commit credentials or secrets.

## Pull Requests

PRs should include:
- what changed
- why it changed
- risk and rollback notes
- links to related issues or PDR entries

## Community

By participating, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
