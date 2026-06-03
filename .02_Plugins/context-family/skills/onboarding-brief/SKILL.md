---
name: onboarding-brief
description: Create a fast-start onboarding brief for a fresh agent, developer, reviewer, or project contributor. Use when the user asks to onboard someone, explain a repo or plugin family, prepare a new Claude Code session, summarize how to work in the project, or give a new agent enough context to become productive quickly.
---

# Onboarding Brief

Create a fast-start guide for a fresh agent or contributor.

## Core procedure

1. Identify audience: agent, developer, reviewer, product partner, security reviewer, or human stakeholder.
2. Explain mission, architecture, key folders, important files, operating rules, and common workflows.
3. Include what not to touch without approval.
4. Include the first 3-5 actions the new contributor should take.
5. Include current risks and where to find source-of-truth docs.

## Output format

```markdown
# Onboarding Brief: <project>

## What this is
<plain description>

## How the project is organized
- `path` — purpose

## How to work safely
- ...

## First actions
1. ...
2. ...
3. ...

## Source-of-truth files
- `path` — topic

## Do not do without approval
- ...
```

## Guardrails

- Do not overwhelm with full file listings.
- Do not present outdated docs as current.
- Do not skip safety boundaries when onboarding agents with tool access.

## Related references

- `references/context-state-schema.md`
- `references/source-of-truth-rules.md`
