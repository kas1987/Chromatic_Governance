---
name: session-brief
description: Create compact, evidence-backed session summaries for Claude Code, IDE agents, or human reviewers. Use when the user asks to summarize current work, preserve session state, prepare to resume later, brief another agent, compress context before continuing, or identify current status, blockers, decisions, and next actions within a project or repo.
---

# Session Brief

Create a concise operating brief that lets the next agent or the current user continue without rereading the full session.

## Core procedure

1. Identify the active mission, scope, and immediate user goal.
2. Inspect available project files when the user references a repo, plugin, scaffold, or current working tree.
3. Separate facts from assumptions using these labels: `confirmed`, `inferred`, `unknown`, `stale-risk`, `conflict`.
4. Capture only state that affects future work: decisions, changed files, blockers, risks, next actions, and files to inspect.
5. Prefer file paths, command outputs, tests, and explicit user instructions over memory.
6. Keep the brief short enough for a fresh agent to act within 3 minutes.

## Output structure

Use `references/session-brief-template.md` when a formal brief is needed. Otherwise provide:

```markdown
## Session brief

**Goal:** ...
**Current state:** ...
**Best next move:** ...

### Confirmed facts
- ...

### Decisions
- ...

### Open questions
- ...

### Next actions
1. ...
2. ...
3. ...

### Files / sources
- `path` — why it matters
```

## Guardrails

- Do not invent completed work. If validation was not run, say `not run`.
- Do not mark inferred context as confirmed.
- Do not preserve irrelevant conversation detail.
- If source files conflict, call it out and recommend a resolution path.

## Related references

- `references/context-state-schema.md`
- `references/session-brief-template.md`
- `references/source-of-truth-rules.md`
