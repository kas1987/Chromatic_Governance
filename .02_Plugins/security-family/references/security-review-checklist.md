# Security Review Checklist

Use this checklist for security-family skills. Keep findings evidence-backed and actionable.

## Universal checks

- Secrets are not committed, logged, packaged, or printed.
- Permissions are least-privilege and scoped to the mission.
- Dangerous actions require human approval.
- External content is treated as data, not instruction.
- Dependencies are necessary, pinned where practical, and reviewed.
- File writes are constrained to expected paths.
- Commands avoid destructive flags unless explicitly approved.
- Network access is justified and bounded.
- Logs redact tokens, keys, credentials, personal data, and internal-only context.
- Tests or manual checks verify the claimed control.

## Agentic coding checks

- Agents cannot silently alter governance files, plugin manifests, hooks, or CI without review.
- Hooks are advisory by default unless intentionally enforced.
- MCP access is scoped by task and not granted globally.
- Research agents stay read-only unless promoted by the user.
- Builder agents do not approve their own high-risk changes.
- Handoffs preserve assumptions, risks, and unverified claims.

## Release artifact checks

- Archives exclude `.env`, credentials, caches, logs, node_modules, venvs, build secrets, and local settings.
- README or docs do not include real endpoints, tokens, usernames, or internal private paths unless intended.
- Validation scripts pass or failures are disclosed.
