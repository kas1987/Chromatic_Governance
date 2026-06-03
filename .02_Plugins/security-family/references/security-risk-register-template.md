# Security Risk Register Template

```markdown
| ID | Risk | Asset | Entry point | Trust boundary | Likelihood | Impact | Priority | Mitigation | Status | Owner |
|---|---|---|---|---|---|---|---|---|---|---|
| SEC-001 | ... | ... | ... | ... | low/medium/high | low/medium/high | low/medium/high | ... | open/mitigated/accepted | ... |
```

## Priority guide

- High: credential exposure, data exfiltration, production impact, auth bypass, destructive write, supply-chain compromise.
- Medium: unsafe defaults, missing validation, excessive permissions, incomplete logging, missing review gate.
- Low: minor hardening, documentation cleanup, non-sensitive warning.
