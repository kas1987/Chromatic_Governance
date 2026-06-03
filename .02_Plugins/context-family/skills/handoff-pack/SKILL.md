---
name: handoff-pack
description: Produce complete handoff packages for another agent, IDE session, Claude Code run, or human reviewer. Use when the user asks to hand off work, package current progress, prepare another agent, resume later, create a transfer brief, or bundle scope, changed files, validation, decisions, risks, and next actions into a reusable continuation document.
---

# Handoff Pack

Create a transfer-ready package that lets another agent or human continue the work safely and efficiently.

## Core procedure

1. Identify the receiving audience: same agent later, specialist agent, reviewer, implementer, or human stakeholder.
2. Summarize the mission, current state, changed files, validation performed, and best next action.
3. Include accepted decisions, unresolved questions, assumptions, risks, and guardrails.
4. Include exact files to inspect, modify, avoid, or treat as authoritative.
5. Provide a copy-paste resume prompt for the next agent/session.
6. Keep the handoff operational; avoid storytelling or excess background.

## Handoff depth levels

Use the smallest sufficient level:

- **Level 1: Quick handoff** — 5-10 bullets for simple continuation.
- **Level 2: Standard handoff** — structured sections with files, validation, and next actions.
- **Level 3: Full handoff pack** — complete template with risks, source-of-truth map, resume prompt, and review gate.

Default to Level 2 unless the user requests a full package or the task is complex.

## Output structure

Use `references/handoff-template.md` for full packages. Standard handoff format:

```markdown
# Handoff: <mission>

## State
- Goal:
- Status:
- Best next move:

## Changed files
- `path` — change summary

## Decisions / assumptions
- ...

## Validation
- ... — pass/fail/not run

## Risks / guardrails
- ...

## Next actions
1. ...
2. ...
3. ...

## Resume prompt
<copy-paste prompt>
```

## Guardrails

- Do not claim tests or validation passed unless actually run or explicitly provided.
- Do not omit known blockers to make the handoff look cleaner.
- Do not transfer broad permissions; name the exact scope the next agent should operate within.

## Related references

- `references/handoff-template.md`
- `references/context-state-schema.md`
- `references/source-of-truth-rules.md`
