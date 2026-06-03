---
name: logs-triage
description: Triage logs, error output, stack traces, deployment logs, CI logs, application logs, and agent/tool execution output to identify failures, likely causes, affected scope, severity, and next diagnostic actions. Use when reviewing log snippets, debugging incidents, summarizing noisy output, or preparing concise evidence for Claude Code, IDE agents, SREs, or human reviewers.
---

# Logs Triage

Turn noisy logs into a ranked diagnosis and next actions.

## Core procedure

1. Preserve the raw signal: note time range, environment, service, command, commit, deployment, and source.
2. Separate symptoms from causes. Treat first failure, repeated failure, and final fatal error as separate evidence.
3. Cluster log lines by failure family: auth, network, dependency, config, data/schema, resource, timeout, permission, test assertion, tool misuse, or unknown.
4. Rank likely causes with confidence: `high`, `medium`, or `low`.
5. Identify blast radius: affected service, user path, job, branch, agent, environment, or release.
6. Recommend the smallest safe diagnostic step before recommending broad rewrites or rollback.

## Output structure

Use `references/log-triage-template.md` for formal triage notes. Otherwise provide:

```markdown
## Log triage

**Severity:** low / medium / high / critical
**Primary failure:** ...
**Likely cause:** ...
**Confidence:** high / medium / low

### Evidence
| Signal | Meaning | Confidence |
|---|---|---|

### Failure clusters
- ...

### Next checks
1. ...

### Suggested fix path
- Immediate containment: ...
- Root fix: ...
- Verification: ...
```

## Guardrails

- Do not infer production impact unless logs, metrics, or user reports support it.
- Do not delete, redact, or rewrite logs except to remove secrets before sharing.
- Flag possible secrets, tokens, credentials, or personal data immediately.
- Prefer targeted checks over speculative code changes.
- If the log sample is incomplete, say what evidence is missing.

## Related references

- `references/log-triage-template.md`
- `references/incident-severity-model.md`
- `references/root-cause-template.md`
