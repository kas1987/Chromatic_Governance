# Controls Checklist

## GitHub App registration

- [ ] App is private/internal.
- [ ] Installed only on selected repositories.
- [ ] Permissions are minimum viable.
- [ ] Webhooks disabled unless required.
- [ ] Webhook secret configured if webhooks are enabled.
- [ ] Private key stored only in approved secret store.

## Repository protections

- [ ] Branch protection enabled on `main`/default branch.
- [ ] PR review required before merge.
- [ ] Required CI checks enabled.
- [ ] Force pushes disabled.
- [ ] Deletion of protected branches disabled.
- [ ] CODEOWNERS covers high-risk files.

## Broker controls

- [ ] Deny-by-default policy engine active.
- [ ] Agent allowlist configured.
- [ ] Repo allowlist configured.
- [ ] Permission profiles configured.
- [ ] Task ID required for write access.
- [ ] Audit logs enabled.
- [ ] Tokens never written to logs.

## Agent controls

- [ ] Agents use branch prefixes.
- [ ] Agents open PRs instead of direct merge.
- [ ] High-risk files require human review.
- [ ] Destructive changes are blocked or escalated.
- [ ] Agent PR template is used.
