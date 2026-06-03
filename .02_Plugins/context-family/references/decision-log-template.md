# Decision Log Template

Use this template for durable project decisions. Keep entries short, traceable, and reversible.

```markdown
# Decision Log

## YYYY-MM-DD - <decision title>

**Status:** proposed | accepted | superseded | rejected  
**Owner:** <user/agent/person>  
**Scope:** <repo/module/plugin/project area>  
**Confidence:** confirmed | inferred | unknown | stale-risk | conflict

### Decision
<What was decided.>

### Context
<Why this came up. Reference files, user instructions, command outputs, or known constraints.>

### Options considered
1. <Option A> — <why accepted/rejected>
2. <Option B> — <why accepted/rejected>

### Rationale
<Why this choice is better now. Include tradeoffs.>

### Consequences
- Positive: <expected benefit>
- Negative: <cost/risk>
- Follow-up: <what must happen next>

### Source links
- `<file path>`
- `<command or issue reference>`
```

## Rules

- One decision per entry.
- Never hide unresolved objections; record them as pending questions.
- Mark old decisions as `superseded` instead of deleting them.
- Prefer dated entries over rewriting history.
- Do not log routine implementation details unless they change direction, authority, architecture, security, release scope, or operating procedure.
