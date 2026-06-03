# Handoff Pack Template

Use this template when transferring work to another agent, another session, or a human reviewer.

```markdown
# Handoff Pack: <mission/title>

## 1. Executive state
- **Goal:** <one sentence>
- **Current status:** not started | in progress | blocked | ready for review | complete
- **Recommended next agent/skill:** <agent or skill>
- **Risk level:** low | medium | high

## 2. What changed
- <file/path> — <change summary>
- <file/path> — <change summary>

## 3. Key decisions
- <decision> — <why it matters>

## 4. Current assumptions
- **Confirmed:** <assumption with evidence>
- **Inferred:** <assumption to verify>
- **Unknown:** <gap>

## 5. Source-of-truth files
- `<path>` — authoritative for <topic>
- `<path>` — secondary for <topic>

## 6. Validation performed
- <command/test/check> — pass/fail/not run

## 7. Remaining work
1. <next action>
2. <next action>
3. <next action>

## 8. Guardrails
- Do not <forbidden action> without human approval.
- Verify <critical source> before changing <critical file>.

## 9. Resume prompt
<Copy-paste prompt for the next agent/session.>
```

## Quality bar

A handoff is acceptable only if the receiving agent can continue without rereading the full conversation.
