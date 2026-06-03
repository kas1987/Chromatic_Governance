---
name: threat-model
description: Build lightweight or deep threat models for agentic development, Claude Code plugins, IDE workflows, APIs, services, repositories, and automation systems. Use when the user asks to identify attack surfaces, trust boundaries, abuse cases, data exposure, security assumptions, or risk mitigations before implementation, release, or plugin/tool access expansion.
---

# Threat Model

Produce a practical threat model that directly informs engineering decisions. Favor clear risk controls over abstract security theory.

## Core procedure

1. Define the protected assets: source code, secrets, customer data, internal docs, credentials, model prompts, agent permissions, deployment targets, and logs.
2. Map actors and trust boundaries: user, local agent, subagents, hooks, MCP servers, network services, CI, package registries, and external content.
3. Identify entry points: prompts, files, dependency installs, generated code, CLI commands, web/API calls, env vars, artifacts, and plugin manifests.
4. List abuse cases before mitigations. Include prompt injection, data exfiltration, command injection, malicious dependency, unsafe file overwrite, privilege creep, and credential leakage where relevant.
5. Rate each risk with `likelihood`, `impact`, and `priority` using low/medium/high.
6. Recommend specific controls: least privilege, confirmation gates, sandboxing, allowlists, validation, secrets scanning, read-only modes, test gates, and human approval.
7. End with a go/no-go recommendation and unresolved questions.

## Output format

```markdown
## Threat model

**Scope:** ...
**Assets protected:** ...
**Trust boundaries:** ...
**Assumptions:** ...

### Risk register
| ID | Risk | Boundary / entry point | Likelihood | Impact | Priority | Mitigation | Owner |
|---|---|---|---|---|---|---|---|

### Required controls
1. ...

### Human approval gates
- ...

### Go / no-go
...
```

## Guardrails

- Do not claim a system is secure. Say what was reviewed and what remains unverified.
- Treat unknown tool permissions as high-risk until inspected.
- Flag any workflow where an agent can both read secrets and exfiltrate data.
- If the task involves regulated data, production credentials, payments, health, legal, or employment data, require explicit human review before write actions.

## Related references

- `references/security-risk-register-template.md`
- `references/agent-permission-model.md`
- `references/security-review-checklist.md`
