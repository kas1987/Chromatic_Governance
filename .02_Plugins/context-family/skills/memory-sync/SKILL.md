---
name: memory-sync
description: Update durable project memory files such as CLAUDE.md, AGENTS.md, README.md, docs/decisions, or plugin policy files with stable facts, decisions, workflows, and source-of-truth pointers. Use when the user asks to save project memory, sync context into repo docs, preserve decisions, or make future agents remember important operating rules.
---

# Memory Sync

Move durable context into the correct project files.

## Core procedure

1. Identify which facts are durable beyond the current task.
2. Choose the correct destination file: `CLAUDE.md`, `AGENTS.md`, `README.md`, `docs/decisions/*`, `docs/runbooks/*`, or plugin-local policy/reference files.
3. Avoid saving temporary guesses, personal chatter, transient debugging output, or stale plans.
4. Preserve source links and dates when the information may later need review.
5. If editing files, show the intended changes or patch summary unless the user has already authorized direct edits.

## Durable memory criteria

Save information that affects future:

- agent behavior
- project architecture
- security or permissions
- release or validation gates
- source-of-truth routing
- recurring workflow procedure
- user-approved conventions

Do not save:

- unverified assumptions
- one-off implementation notes
- speculative options that were not selected
- sensitive secrets or credentials

## Output format

```markdown
## Memory sync plan

### Save
- ... -> `path`

### Do not save
- ... — reason

### Proposed update
<patch or concise summary>
```

## Guardrails

- Do not store credentials, personal secrets, or sensitive tokens.
- Do not overwrite human-authored policy without showing the change.
- If multiple memory files overlap, use `source-of-truth-audit` first.

## Related references

- `references/source-of-truth-rules.md`
- `references/decision-log-template.md`
