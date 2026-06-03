---
name: sandbox-check
description: Check whether commands, scripts, generated code, tests, package installs, file operations, or agent workflows are safe to run in the current environment. Use before executing unknown code, running build scripts, processing untrusted files, invoking hooks, installing dependencies, or allowing an agent to perform write or network actions.
---

# Sandbox Check

Decide whether a proposed operation is safe to run, where it should run, and what constraints are required.

## Core procedure

1. Identify the operation: command, script, dependency install, file transform, hook, MCP call, test suite, or generated executable.
2. Determine inputs and trust level: local trusted repo, generated code, third-party package, user-uploaded file, internet content, or unknown source.
3. Identify potential harm: file deletion, credential access, network exfiltration, resource exhaustion, persistence, package execution, or system modification.
4. Recommend execution mode: do not run, read-only inspect, container/sandbox, dry-run, limited path, no-network, no-secrets, or approved local run.
5. Provide a safe command plan where applicable.

## Output format

```markdown
## Sandbox check

**Operation:** ...
**Trust level:** trusted / mixed / untrusted
**Risk:** low / medium / high
**Recommended mode:** ...

### Risks
- ...

### Safe run plan
1. ...

### Do-not-run conditions
- ...
```

## Guardrails

- Do not run unknown install scripts, curl-pipe-shell commands, or generated destructive commands without explicit approval.
- Prefer dry-runs and read-only inspection first.
- Keep secrets out of the environment unless absolutely required.
- Treat user-provided archives and repo hooks as untrusted until inspected.

## Related references

- `references/agent-permission-model.md`
