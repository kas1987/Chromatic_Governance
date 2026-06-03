---
name: decision-log
description: Capture, update, and audit durable project decisions with rationale, tradeoffs, evidence, and status. Use when the user makes or asks to record architecture, product, security, release, agent-governance, plugin-scope, or workflow decisions; when decisions need to be preserved for later; or when existing decisions conflict or need review.
---

# Decision Log

Maintain a durable record of decisions that materially affect project direction, architecture, security, release behavior, plugin boundaries, or agent workflow.

## Core procedure

1. Determine whether the item is a real decision or routine implementation detail.
2. Record the decision, context, options considered, rationale, consequences, and follow-ups.
3. Mark status as `proposed`, `accepted`, `superseded`, or `rejected`.
4. Attach confidence: `confirmed`, `inferred`, `unknown`, `stale-risk`, or `conflict`.
5. Preserve old decisions by marking them `superseded`; do not erase project history.
6. If no durable decision-log file exists, propose a location such as `docs/decisions/DECISION_LOG.md` or `docs/adr/` before writing.

## What qualifies as a decision

Log decisions involving:

- Architecture and module boundaries.
- Plugin family scope and skill ownership.
- Agent authority, permissions, escalation rules, or tool access.
- Security posture or trust boundaries.
- Release gates, quality standards, and validation rules.
- Product scope, MVP cuts, or non-goals.
- Durable naming, folder structure, schema, or interface contracts.

Do not log:

- Temporary brainstorming unless selected for action.
- Routine file edits with no strategic consequence.
- Command output unless it changes a decision.

## Output structure

Use `references/decision-log-template.md` for durable entries. For chat summaries, provide:

```markdown
## Decision captured

**Decision:** ...
**Status:** accepted/proposed/superseded/rejected
**Rationale:** ...
**Consequences:** ...
**Follow-up:** ...
**Confidence:** confirmed/inferred/unknown/stale-risk/conflict
```

## Guardrails

- Do not silently resolve conflicts between decisions. Surface them.
- Do not rewrite history without marking supersession.
- Ask for confirmation before recording high-impact security, release, or destructive workflow decisions when user intent is unclear.

## Related references

- `references/decision-log-template.md`
- `references/source-of-truth-rules.md`
