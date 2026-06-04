---
name: harvest
description: 'Cross-rig knowledge consolidation. One-time sweep + ongoing tiered promotion. Walks all .agents/ directories, extracts learnings, deduplicates, and promotes to knowledge base. Triggers: harvest, consolidate knowledge, extract learnings, knowledge sweep.'
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

# Harvest Skill

> **Quick Ref:** Consolidate session knowledge into `~/.agents/learnings/`. Uses `ao forge transcript` + `ao extract` — NOT `ao harvest` (does not exist).

**YOU MUST EXECUTE THIS WORKFLOW. Do not just describe it.**

## Execution Steps

### Step 1: Find the Current Session Transcript

```bash
TRANSCRIPT=$(ls -t ~/.claude/projects/C--Users-kas41/*.jsonl 2>/dev/null | head -1)
echo "Transcript: $TRANSCRIPT"
```

If no transcript found, skip to Step 3.

### Step 2: Extract Learnings from Transcript

```bash
ao forge transcript --last-session --queue --quiet 2>/dev/null || echo "[harvest] ao forge transcript not available — writing learnings manually"
```

Then process the extraction queue:

```bash
ao extract --all 2>/dev/null || echo "[harvest] ao extract not available"
```

### Step 3: Extract from Any Research Docs Produced This Session

```bash
# Find markdown files created/modified in the last 4 hours
find ~/.agents/research ~/.agents/plans ~/.agents/audits -name "*.md" -newer ~/.agents/learnings/.last-harvest 2>/dev/null | head -10 | while read f; do
  ao forge markdown "$f" 2>/dev/null && echo "Forged: $f"
done
```

### Step 4: Write Manual Learning if ao Commands Unavailable

When `ao` commands fail, write learnings directly. Use this frontmatter:

```markdown
---
id: learning-YYYY-MM-DD-<slug>
type: learning
date: YYYY-MM-DD
tags: [<relevant-tags>]
confidence: 0.8
utility: medium
anti-pattern: false
---

# <Title>

## What I Learned
<concise statement of the insight>

## How to Apply
<when and how to use this going forward>
```

Save to: `~/.agents/learnings/YYYY-MM-DD-<slug>.md`

### Step 5: Update Last-Harvest Timestamp

```bash
touch ~/.agents/learnings/.last-harvest
```

### Step 6: Report

List new learnings written:

```bash
ls -lt ~/.agents/learnings/*.md | head -10
```

## Examples

```
/harvest
→ Finds latest transcript, runs ao forge + ao extract, reports new learnings

/harvest research
→ Same, plus forges any .agents/research/*.md files from today
```

## Troubleshooting

- **`ao harvest` not found** — Expected. `ao harvest` does not exist. This skill uses `ao forge transcript` + `ao extract` instead.
- **`ao forge` not found** — Write learnings manually (Step 4). The goal is the `.md` files, not the tool.
- **No transcript found** — Skip Step 2; proceed from Step 3 with any research docs.

## Guardrails

- Extract only factual learnings from the session transcript; no speculation
- Do not fabricate entries if no transcript is found; skip and report instead
- Harvesting is idempotent; re-running must not create duplicate entries
