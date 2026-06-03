---
name: secrets-audit
description: Audit repositories, plugin folders, generated artifacts, logs, prompts, environment examples, and configuration files for exposed secrets or credential-handling risk. Use when the user asks to check for API keys, tokens, private keys, passwords, .env leakage, unsafe examples, or secret exposure before sharing, committing, packaging, or release.
---

# Secrets Audit

Find likely credential exposure and produce safe remediation steps. Never print full secret values.

## Core procedure

1. Identify target files and likely secret locations: `.env*`, config files, CI files, logs, notebooks, generated zips, docs, examples, and plugin manifests.
2. Use available search tools or local commands when working in a repo. Prefer targeted scans over broad noisy output.
3. Detect common patterns: API keys, OAuth tokens, private keys, SSH keys, database URLs, cloud credentials, webhook URLs, session cookies, and bearer tokens.
4. Classify each finding as `confirmed-secret`, `likely-secret`, `test-placeholder`, or `benign`.
5. Report only masked values using first 4 and last 4 characters when helpful.
6. Recommend remediation: revoke/rotate, remove from history, move to secret manager, update `.gitignore`, replace examples with placeholders, and add scanning gates.
7. If packaging a plugin or artifact, inspect the package contents before sharing.

## Output format

```markdown
## Secrets audit

**Scope reviewed:** ...
**Result:** pass / needs action / blocked

### Findings
| Severity | File | Type | Evidence | Action |
|---|---|---|---|---|

### Immediate remediation
1. ...

### Prevention controls
- ...
```

## Guardrails

- Never echo complete keys, tokens, passwords, private keys, or credentials.
- Do not attempt to validate secrets by calling external services unless the user explicitly asks and it is safe.
- If a real secret appears in committed history, tell the user deletion alone is insufficient; rotation is required.
- Treat generated archives as shareable artifacts and scan them before linking.

## Related references

- `references/secrets-patterns.md`
- `references/security-review-checklist.md`
