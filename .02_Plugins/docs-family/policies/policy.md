# Docs Family Policy

## Allowed

- Create, update, audit, and synchronize documentation.
- Propose docs patches from repo evidence, diffs, and current source files.
- Mark unverified claims, stale content, and owner-review items.
- Generate templates, diagrams, runbooks, guides, and troubleshooting matrices.

## Not allowed without explicit approval

- Promise production support, compatibility, security posture, or SLA guarantees not proven by source material.
- Publish secrets, credentials, private customer data, internal-only links, or sensitive operational details in public docs.
- Rewrite large documentation sets when a targeted sync was requested.
- Delete or archive docs without reporting impact and rationale.

## Escalation

- Security-sensitive documentation: use `security-family`.
- Deployment or rollback procedures: coordinate with `release-family` and `observability-family`.
- Interface changes: coordinate with `architecture-family` and `qa-eval-family`.
- Agent authority or ownership conflict: use `agent-governance-family`.
