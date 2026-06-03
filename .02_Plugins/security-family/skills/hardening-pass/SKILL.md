---
name: hardening-pass
description: Apply or recommend practical hardening controls for code, plugins, agents, hooks, scripts, APIs, configs, and release artifacts. Use after implementation or review when the user asks to make the system safer, production-ready, less fragile, least-privilege, more auditable, or ready for packaging/release.
---

# Hardening Pass

Turn identified risks into concrete controls and safe defaults.

## Core procedure

1. Establish scope and risk posture: prototype, internal tool, production, public release, or sensitive-data system.
2. Review existing controls: validation, auth, permissions, secrets handling, logs, dependency pins, error handling, tests, hooks, and rollback.
3. Add or recommend controls in priority order: input validation, output encoding, least privilege, safe file paths, dry-runs, confirmation gates, redaction, allowlists, timeouts, dependency pins, and audit logs.
4. Verify changes with tests or manual checks where possible.
5. Provide residual risks and next hardening round.

## Output format

```markdown
## Hardening pass

**Scope:** ...
**Risk posture:** prototype / internal / production / public

### Applied / recommended controls
| Priority | Area | Control | Status | Verification |
|---|---|---|---|---|

### Residual risks
- ...

### Next pass
1. ...
```

## Guardrails

- Do not make broad rewrites when small controls solve the risk.
- Keep developer ergonomics in mind; security that breaks workflows gets bypassed.
- Do not claim production readiness without tests, deployment context, and operational checks.
- Redact sensitive values in logs, examples, and output.

## Related references

- `references/security-review-checklist.md`
- `references/agent-permission-model.md`
