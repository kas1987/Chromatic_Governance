# Security Family

Security, trust-boundary, secrets, dependency, prompt-injection, sandbox, and permission controls for agentic development and Claude Code plugin workflows.

## Implemented skills

- `threat-model` — map assets, boundaries, abuse cases, and mitigations.
- `secrets-audit` — inspect repos/artifacts for exposed credentials without printing secrets.
- `dependency-risk` — review package, lockfile, license, and supply-chain risk.
- `permissions-plan` — design least-privilege access for agents, hooks, MCPs, and scripts.
- `sandbox-check` — decide whether commands or code are safe to run and under what constraints.
- `prompt-injection-review` — separate untrusted content from authoritative instructions.
- `security-pr` — perform security-focused PR/diff review.
- `hardening-pass` — convert risks into practical controls and verification steps.

## Default posture

Deny by default. Prefer read-only inspection first. Require explicit human approval for credential access, destructive changes, dependency installs, network calls involving sensitive data, CI/CD changes, and deployment.

## References

- `references/security-review-checklist.md`
- `references/agent-permission-model.md`
- `references/secrets-patterns.md`
- `references/prompt-injection-patterns.md`
- `references/security-risk-register-template.md`
