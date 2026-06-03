# Secrets Patterns

Do not print full values. Mask evidence.

## Common secret locations

- `.env`, `.env.local`, `.env.production`
- CI configs and workflow files
- Docker compose files
- shell scripts
- app config files
- notebooks
- logs
- generated archives
- README examples copied from real environments

## Common secret types

- API keys and bearer tokens
- OAuth client secrets and refresh tokens
- private keys and SSH keys
- cloud provider credentials
- database URLs with usernames/passwords
- webhook URLs
- signing keys and JWT secrets
- session cookies

## Classification

- `confirmed-secret`: real credential format with plausible value or label.
- `likely-secret`: suspicious high-entropy value or credential-like config.
- `test-placeholder`: fake value such as `sk-REPLACE_ME`, `example`, `dummy`, or documented mock.
- `benign`: not a secret after inspection.

## Masking standard

Use `abcd...wxyz` or `[redacted type]`. Never show complete values.
