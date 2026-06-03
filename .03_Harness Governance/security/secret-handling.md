# Secret Handling Policy

## Allowed

- GitHub Actions secrets for private key storage.
- Local OS secret manager.
- Vault/1Password/Bitwarden/Keychain-style storage.
- Environment variables injected at runtime.

## Not allowed

- Committing `.pem`, `.key`, `.env`, or token files.
- Printing tokens in logs.
- Passing tokens into LLM prompt context.
- Storing installation tokens in agent memory files.
- Sharing one PAT across agents.

## Rotation triggers

Rotate GitHub App private keys when:

- A key may have been exposed.
- An agent runtime is compromised.
- Logs accidentally contain secret material.
- An operator leaves the project.
- Scheduled rotation cadence is reached.

## Emergency shutoff

1. Suspend or uninstall the GitHub App installation.
2. Revoke/rotate private keys.
3. Disable broker runtime.
4. Review audit logs.
5. Re-enable with narrowed permissions.
