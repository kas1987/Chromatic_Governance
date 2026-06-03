---
name: source-of-truth-audit
description: Audit project files, docs, plugin manifests, decisions, and generated summaries for contradictions, stale guidance, duplicate authority, or missing canonical sources. Use when the user asks what is authoritative, whether docs conflict, why agents are confused, which files should govern behavior, or how to clean up project truth before implementation.
---

# Source-of-Truth Audit

Find conflicts, stale files, duplicate authority, and missing canonical sources.

## Core procedure

1. List candidate authoritative files for the topic.
2. Rank them using `references/source-of-truth-rules.md`.
3. Compare claims across docs, manifests, configs, tests, and user instructions.
4. Classify findings as `confirmed`, `conflict`, `stale-risk`, `missing-source`, or `duplicate-authority`.
5. Recommend one canonical source per topic.
6. Propose edits, but do not delete or overwrite without approval.

## Output format

```markdown
## Source-of-truth audit

### Verdict
<brief conclusion>

### Authority ranking
| Topic | Canonical source | Secondary source | Issue |
|---|---|---|---|

### Conflicts found
- <conflict> — sources: `path`, `path`

### Stale or suspect files
- `path` — reason

### Recommended cleanup
1. ...
2. ...
3. ...
```

## Guardrails

- Never hide contradictions.
- Never delete stale docs automatically.
- Prefer marking a source as superseded before removal.
- If user instruction conflicts with repo docs, treat current explicit user instruction as highest authority and recommend updating docs.

## Related references

- `references/source-of-truth-rules.md`
- `references/decision-log-template.md`
