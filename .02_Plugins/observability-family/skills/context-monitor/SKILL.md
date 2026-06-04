---
name: context-monitor
description: Track, report, and manage context window and token usage across models and agent sessions. Use when diagnosing slow responses, planning context-heavy tasks, monitoring subagent token budgets, logging usage across sessions, or deciding when to invoke context-prune, handoff, or model switching.
skill_api_version: 1
---

# Context Monitor

Make context usage visible, logged, and actionable so agents and subagents can make informed decisions about loading, pruning, handoffs, and model selection before the context window becomes a silent constraint.

## Core procedure

1. **Establish the context budget.** Identify the model in use and its context limit:

   | Model | Context limit |
   |---|---:|
   | claude-opus-4-8 | ~200 000 tokens |
   | claude-sonnet-4-6 | ~200 000 tokens |
   | claude-haiku-4-5 | ~200 000 tokens |
   | gpt-4o | ~128 000 tokens |
   | gemini-1.5-pro | ~1 000 000 tokens |
   | local / unknown | Assume 8 000 tokens unless stated |

2. **Estimate current usage.** Inventory what is loaded: system prompt, plugin manifests, skill files, conversation history, file reads, tool results, and in-progress output. Use the `/status` command in Claude Code to read live token counts when available.

3. **Classify usage level and recommend action:**

   | Used | Status | Recommended action |
   |---|---|---|
   | < 40% | `green` | Continue; load additional families if needed |
   | 40–65% | `yellow` | Prefer lazy skill loading; avoid reading large files |
   | 65–80% | `orange` | Run `/context-prune`; stop loading new plugin families |
   | 80–90% | `red` | Create a `/handoff` immediately; do not start new sub-tasks |
   | > 90% | `critical` | Write handoff and stop; further work risks truncation |

4. **Log the snapshot.** Write a JSONL entry to `.agents/logs/context-usage.jsonl`:

   ```jsonl
   {"ts":"<ISO-8601>","model":"<model-id>","session":"<session-id>","used_tokens":<n>,"limit_tokens":<n>,"pct_used":<0.0–1.0>,"status":"green|yellow|orange|red|critical","loaded_families":["rpi","context-family"],"note":"<optional>"}
   ```

5. **Report the snapshot** in a concise inline summary.

6. **Advise on next steps** based on status: which families to unload, whether to invoke `context-prune`, whether to begin a `handoff`, or whether to switch to a cheaper or higher-capacity model.

## Output format

```markdown
## Context monitor snapshot

**Model:** [model-id]
**Limit:** [N] tokens
**Estimated used:** [N] tokens ([X]%)
**Status:** green / yellow / orange / red / critical

### Loaded contributing to usage
- System prompt + plugin manifests: ~[N] tokens
- Skill files loaded: [list] (~[N] tokens)
- Conversation history: ~[N] tokens
- Tool results / file reads: ~[N] tokens

### Recommendation
[Specific action: continue / prune / handoff / switch model]

### Logged to
`.agents/logs/context-usage.jsonl`
```

## Subagent guidance

When spawning a subagent, include a context budget note in the prompt:
- State the model the subagent will run on.
- State the approximate tokens already consumed in the parent session.
- Tell the subagent to invoke `/context-monitor` if it needs to load more than two plugin families.
- Tell the subagent to write its output to a file rather than return it inline if the output will exceed ~2 000 tokens.

## When to invoke automatically

Agents should invoke `context-monitor` proactively when:
- About to load a third or subsequent plugin family in one session
- About to read a file larger than 500 lines
- Starting a task that requires spawning 2 or more subagents
- After receiving a large tool result (>200 lines)
- At the start of any session expected to last more than 30 minutes

## Guardrails

- Do not block progress solely because of yellow status; proceed with reduced loading.
- Do not guess token counts from output length alone; use `/status` counts when available and add a 20% buffer when estimating.
- If the model is unknown, use the most conservative limit (8 000 tokens) until confirmed.
- Log every snapshot; do not skip logging to save tokens — the log entry is small.

## Related references

- `references/health-report-template.md`
- `references/metrics-review-template.md`
