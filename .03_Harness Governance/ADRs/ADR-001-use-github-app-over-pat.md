# ADR-001: Use GitHub App Over Shared PAT

## Status

Accepted

## Context

Agents need programmatic GitHub access. Shared PATs are simple but introduce broad permissions, weak attribution, difficult rotation, and high blast radius.

## Decision

Use a private GitHub App with selected repository installation and short-lived installation tokens. Put an access broker in front of token issuance.

## Consequences

### Positive

- Better least-privilege control.
- Cleaner app/bot identity.
- Short-lived token model.
- Per-repo installation control.
- Better audit and revocation path.

### Negative

- More initial setup.
- Requires broker implementation.
- Requires private key handling.

## Follow-ups

- Implement token issuer.
- Add audit log review process.
- Add branch protection and CODEOWNERS.
