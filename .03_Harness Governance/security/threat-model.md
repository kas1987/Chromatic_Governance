# Threat Model: AI Agent Repo Access

## Assets

- Source code.
- Repository history.
- GitHub App private key.
- Installation access tokens.
- CI secrets.
- Protected branches.
- Release artifacts.

## Trust boundaries

```text
User/Human Admin
  -> GitHub App Settings
  -> Secret Store
  -> Broker
  -> Agent Runtime
  -> GitHub API
```

The highest-risk boundary is between the broker and agent runtime. Tokens should not be exposed to untrusted prompts, logs, or arbitrary shell output.

## Attack classes

| Class | Example | Control |
|---|---|---|
| Prompt injection | Malicious README tells agent to exfiltrate token | Keep token outside prompt context; no token logging |
| Tool misuse | Agent requests broad write permissions | Policy engine deny-by-default |
| Supply chain | Dependency update adds malicious package | Review, CI, dependency scanning |
| CI compromise | Workflow modified to expose secrets | CODEOWNERS, high-risk review |
| Repo destruction | Agent deletes files | PR review, diff threshold, blocked paths |

## Minimum security posture

- App private key never committed.
- Installation tokens expire and are never logged.
- All writes go through PRs.
- Branch protection blocks direct main push.
- Broker has a kill switch.
