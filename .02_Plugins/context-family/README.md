# Context Family

Context, memory, decision log, source-of-truth, and session handoff controls.

## Purpose

This plugin family keeps agent work compact, durable, source-backed, and transferable across Claude Code runs, IDE sessions, subagents, reviewers, and future contributors.

## Skills

### Implemented core skills

- `session-brief` - Create compact evidence-backed status briefs.
- `decision-log` - Capture durable decisions with rationale, tradeoffs, status, and confidence.
- `handoff-pack` - Package current progress for another agent/session/human reviewer.

### Implemented support skills

- `context-map` - Map repo/project/plugin structure into navigable context.
- `source-of-truth-audit` - Identify authoritative files, conflicts, stale docs, and missing canonical sources.
- `context-prune` - Compress noisy context while preserving operational truth.
- `memory-sync` - Move stable facts and decisions into durable project files.
- `onboarding-brief` - Prepare a fast-start guide for a fresh agent or contributor.

## References

- `references/context-state-schema.md`
- `references/session-brief-template.md`
- `references/decision-log-template.md`
- `references/handoff-template.md`
- `references/source-of-truth-rules.md`

## Agents

- `context-steward` - Keeps project context compact, current, source-backed, and ready for handoff.

## Hooks

- `PreCompact` advisory hook via `scripts/context-check.sh`.

## Status

Context core implemented. Ready for trial use in Claude Code / IDE-agent workflows.
