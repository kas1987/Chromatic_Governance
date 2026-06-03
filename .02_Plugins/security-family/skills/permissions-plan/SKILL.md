---
name: permissions-plan
description: Design least-privilege permission boundaries for agents, Claude Code plugins, hooks, MCP servers, repo tools, CI jobs, and automation workflows. Use when the user asks what a plugin or agent should access, how to scope tools, whether write/network/secrets access is safe, or how to separate capabilities by role or task.
---

# Permissions Plan

Define what each agent, skill, hook, or tool may read, write, execute, call, and approve.

## Core procedure

1. List roles/components: human, coordinator agent, specialist agents, hooks, skills, MCP servers, scripts, CI, deployment accounts.
2. For each component, define required capabilities only: file read, file write, command execution, network, secrets, external APIs, package install, artifact creation, git operations, deployment.
3. Apply least privilege and separation of duties: the same actor should not create, approve, and deploy high-risk changes without a gate.
4. Define approval gates for destructive, networked, credentialed, production, or irreversible actions.
5. Specify deny-by-default rules and safe defaults.
6. Produce a permission matrix and enforcement recommendations.

## Output format

```markdown
## Permissions plan

**Scope:** ...
**Default stance:** deny by default / read-only unless approved

### Permission matrix
| Component | Read | Write | Execute | Network | Secrets | External APIs | Approval required |
|---|---|---|---|---|---|---|---|

### Approval gates
- ...

### Deny rules
- ...

### Implementation notes
- ...
```

## Guardrails

- Never grant broad tool access because it is convenient.
- Keep research agents read-only unless implementation is explicitly in scope.
- Hooks that auto-run commands should be read-only or advisory by default.
- MCP access should be scoped to the mission and removed when not needed.

## Related references

- `references/agent-permission-model.md`
- `references/security-review-checklist.md`
