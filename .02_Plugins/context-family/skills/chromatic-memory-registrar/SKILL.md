---
name: chromatic-memory-registrar
description: Capture durable project memory after significant decisions, repo changes, PDR completions, migrations, agent dispatches, audits, or implementation cycles. Use when updating project state, decision registers, changelogs, memory logs, source-of-truth maps, or next actions across Claude, Codex, Cursor, Gemini, GitHub, and local repositories.
skill_api_version: 1
---

# Chromatic Memory Registrar

Prevent loss of continuity across fast-moving, multi-system work by writing durable memory to the correct files rather than relying on chat history.

## Source-of-truth hierarchy

When new information conflicts with existing records, resolve by priority:

1. Explicit user instruction in current task
2. Current repo source-of-truth docs (`CLAUDE.md`, `AGENTS.md`, `CHROMATIC_TREES.md`)
3. PDR decisions
4. Project state files
5. Agent logs and handoffs
6. Chat summaries and inferred memory

Do not overwrite higher-priority sources silently. Create a contradiction entry and surface it.

## Core procedure

1. **Identify the triggering event.** What changed: a decision made, a repo migrated, a PDR completed, an agent dispatched, an audit finished?
2. **Classify the memory type.** Match each piece of information to its correct output file:
   - Architecture or workflow decisions → `DECISIONS.md`
   - Repo or system state → `PROJECT_STATE.md`
   - Completed work log → `CHANGELOG.md`
   - What to do next → `NEXT_ACTIONS.md`
   - Cross-agent continuity and source-of-truth pointers → `MEMORY_REGISTER.md`
3. **Check for contradictions.** Before writing, verify the new information is consistent with existing source-of-truth docs. If not, create a contradiction note and surface it to the user before proceeding.
4. **Write concisely and actionably.** Each entry should enable a fresh agent to act correctly without needing the originating conversation.
5. **Label assumptions.** Distinguish confirmed facts from inferred conclusions.
6. **Link sources.** Include repo paths, PDR references, or file paths where evidence lives.

## Output format

```markdown
## Memory registration — [Event name]

### Decisions
- [Decision]: [Rationale] — Source: [file or PDR ref]

### Project state
- ...

### Changelog entry
- [date] [version] [change summary]

### Next actions
1. ...

### Contradictions (if any)
- New: ... conflicts with: [source] — Recommendation: [human decision needed / override with justification]
```

## Guardrails

- Do not record uncertain inferences as durable facts; label them as assumptions.
- Do not overwrite human-authored policy without showing the change and getting confirmation.
- Do not store credentials, secrets, or tokens in memory files.
- Keep entries concise — future agents read these under context pressure; long entries reduce utility.
- Use `source-of-truth-audit` first when multiple memory files appear inconsistent.

## Related references

- `references/source-of-truth-rules.md`
- `references/decision-log-template.md`
