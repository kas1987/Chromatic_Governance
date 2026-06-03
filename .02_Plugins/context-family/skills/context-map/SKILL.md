---
name: context-map
description: Map a repository, project folder, plugin scaffold, documentation set, or workspace into a concise source-of-truth and navigation model. Use when the user asks to understand project structure, identify important files, onboard an agent, locate authoritative docs, map plugin families, or create a compact repo/project overview before implementation.
---

# Context Map

Create a navigable map of the project context so agents know where truth lives and where to work.

## Core procedure

1. Inspect the file tree before summarizing when filesystem access is available.
2. Identify primary domains: code, docs, tests, configuration, scripts, policies, agents, skills, hooks, assets.
3. Mark authoritative files, secondary files, stale/suspect files, and missing files.
4. Connect each area to its likely owner or plugin family when applicable.
5. Recommend the next files to inspect for the user's current mission.

## Output format

```markdown
## Context map

### Top-level structure
| Path | Purpose | Authority |
|---|---|---|
| `path` | ... | primary/secondary/stale/unknown |

### Source-of-truth map
- <topic>: `path`

### Work zones
- Safe to edit now: ...
- Inspect before editing: ...
- Avoid unless approved: ...

### Gaps / conflicts
- ...

### Recommended next reads
1. `path` — why
```

## Guardrails

- Do not infer file purpose from name alone when contents are available to inspect.
- Do not label a file authoritative if another newer or higher-priority source conflicts.
- Keep generated maps compact; link to deeper docs rather than copying them.

## Related references

- `references/source-of-truth-rules.md`
- `references/context-state-schema.md`
