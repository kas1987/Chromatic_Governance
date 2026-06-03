# Toolchain Operating Model

Use the toolchain family as the workspace operations layer. It should not own product decisions, architecture decisions, security approval, or final release approval. It should gather evidence, maintain workspace hygiene, prepare handoffs, support worktree isolation, and help author/review skill files.

## Operating principles

1. Prefer evidence over memory: files, diffs, manifests, validation output, and logs.
2. Separate collection from interpretation: use `harvest` before `harvest-insights` when the workspace is unknown.
3. Keep operational reports short and action-oriented.
4. Bound every agent task by branch/worktree/scope.
5. Preserve human decision points instead of silently choosing risky defaults.
6. Never hide unrun validation.

## Common flow

```text
harvest -> harvest-insights -> status -> handoff/system-audit
```

For parallel work:

```text
status -> using-git-worktrees -> handoff -> status -> system-audit
```

For skill creation:

```text
writing-skills -> system-audit -> package/zip validation -> handoff
```

## Escalation triggers

Escalate to the security family when secrets, permissions, prompt injection, dependency risk, or production access appear. Escalate to the architecture family when boundaries, APIs, migrations, or cross-module design are affected. Escalate to the QA/eval family when acceptance criteria, tests, regression, or coverage are material.
