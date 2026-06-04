---
name: harvest-insights
description: 'Parses the latest /insights report and autonomously generates PDRs, queues items into next-session-queue, writes an audit file. Triggers: harvest insights, process insights, queue insights, insights to pdr.'
skill_api_version: 1
context:
  window: inherit
  intent:
    mode: none
  intel_scope: none
metadata:
  tier: session
  dependencies: []
---

# Harvest-Insights Skill

> **Quick Ref:** Parses `/insights` output → generates PDRs → updates `~/.agents/evolve/next-session-queue.md` → writes audit to `~/.agents/audits/YYYY-MM-DD-insights-harvest-audit.md`.

**YOU MUST EXECUTE THIS WORKFLOW. Do not just describe it.**

## Execution Steps

### Step 1: Run /insights (if not already done)

If the user has not yet run `/insights`, invoke it now:

```
Use the Skill tool with skill: "insights" (if available), or ask the user to run /insights first.
```

If `/insights` output is already in context, proceed to Step 2.

### Step 2: Parse the Insights Output

Extract all items from the `/insights` report. Categorize by:
- **Priority:** P1 / P2 / P3
- **Type:** bug, feature, process, horizon
- **Status:** Ready / Blocked / Done

### Step 3: Generate PDRs for Ready Items

For each **Ready** item (P1 or P2), create a PDR (Proposed Decision Record) file:

```bash
mkdir -p ~/.agents/evolve/pdrs
```

PDR filename: `~/.agents/evolve/pdrs/YYYY-MM-DD-<slug>.md`

PDR template:
```markdown
---
id: pdr-YYYY-MM-DD-<slug>
type: pdr
date: YYYY-MM-DD
priority: P1|P2|P3
status: proposed
---

# PDR: <Title>

## Proposed Action
<What should be done>

## Why
<Motivation from /insights>

## Definition of Done
<How to know it's complete>

## Blocked On
<If blocked: what's needed. Otherwise: "Nothing — ready to pick up.">
```

### Step 4: Update next-session-queue.md

Read current queue:

```bash
cat ~/.agents/evolve/next-session-queue.md 2>/dev/null
```

Add new items at the top under their priority heading. Mark each with `**Status:** Ready` or `**Status:** Blocked on <reason>`.

Do NOT overwrite existing DONE items — only append new ones.

### Step 5: Write Audit File

```bash
AUDIT_FILE="$HOME/.agents/audits/$(date +%Y-%m-%d)-insights-harvest-audit.md"
```

Audit template:
```markdown
# Insights Harvest Audit — YYYY-MM-DD

## Summary
- Items parsed: N
- PDRs generated: N
- Items queued: N
- Items blocked: N

## PDRs Generated
- [ ] pdr-YYYY-MM-DD-<slug> — <title>
...

## Blocked Items
- <item> — blocked on: <reason>

## Notes
<anything notable about this harvest>
```

### Step 6: Report

Tell the user:
- How many PDRs were generated
- How many items queued
- Path to the audit file

## Examples

```
/harvest-insights
→ Processes /insights output already in context, generates PDRs, updates queue

Run /insights first, then /harvest-insights
→ Full end-to-end insights → action pipeline
```

## Troubleshooting

- **No /insights output in context** — Ask user to run `/insights` first, then re-invoke this skill.
- **next-session-queue.md missing** — Create it with `mkdir -p ~/.agents/evolve && touch ~/.agents/evolve/next-session-queue.md`.
- **Duplicate PDRs** — Check existing PDRs before creating; if a matching slug exists, update status instead of creating a new file.

## Guardrails

- Only generate PDRs for items explicitly marked ready in the insights output
- Do not modify or overwrite existing PDR files; create new ones only
- If insights output is absent or empty, report and stop without creating files
