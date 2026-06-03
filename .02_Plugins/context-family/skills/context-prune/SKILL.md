---
name: context-prune
description: Compress, clean, and de-noise project or session context while preserving decisions, constraints, risks, source-of-truth files, and next actions. Use when the user asks to reduce context bloat, prepare for compaction, remove stale planning noise, clean agent handoff material, or keep only durable information needed for continuation.
---

# Context Prune

Compress context without losing operational truth.

## Core procedure

1. Preserve goals, constraints, accepted decisions, active files, risks, blockers, and next actions.
2. Remove repeated explanations, superseded plans, low-value brainstorms, routine command output, and irrelevant chatter.
3. Replace long details with file paths, decision IDs, or short summaries.
4. Mark discarded-but-risky items as `pruned: stale`, `pruned: duplicate`, or `pruned: superseded` when useful.
5. Produce a compact continuation summary.

## Output format

```markdown
## Pruned context

### Keep
- ...

### Compress
- <long item> -> <short retained form>

### Drop
- <item> — reason

### Resulting continuation state
- Goal:
- Current status:
- Next actions:
```

## Guardrails

- Do not remove unresolved blockers.
- Do not drop security, release, or destructive-action warnings.
- Do not flatten confirmed facts and assumptions into the same confidence level.

## Related references

- `references/source-of-truth-rules.md`
- `references/context-state-schema.md`
