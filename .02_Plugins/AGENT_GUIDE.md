# Agent and Subagent Guide

**For:** Primary agents, subagents, and orchestrators using the Poly-Chromatic plugin ecosystem  
**Version:** 0.16.0

---

## Core principle: load only what you need

This ecosystem has 118 skills across 13 families. Loading all families at session start wastes context tokens that every agent shares with its work output. The system is designed for **on-demand loading** — bring in a family when you need a skill from it, and only then.

---

## How to invoke a skill

Skills are SKILL.md files inside each plugin family. They are loaded by the plugin mechanism (Claude Code plugin or MCP server) when the family is active for the session.

**To invoke a skill:** use its `/skill-name` slash command when the family is loaded.

**To load a family:** use `/plugin load <family-name>` or configure it in your `CLAUDE.md` or session settings.

**To check which families are currently loaded:** run `/status` or `/context-monitor`.

---

## Recommended startup sequence

### Step 1 — Load only the minimum

Load the single family most relevant to your first task step. Do not load multiple families upfront unless you have confirmed context budget.

```
Task type                → Start with
──────────────────────────────────────
Feature delivery         → rpi
Multi-agent coordination → agent-governance-family
PDR intake / routing     → agent-governance-family
Cross-LLM handoffs       → toolchain-family
Security review          → security-family
Architecture gate        → architecture-family
Release                  → release-family
Context budget check     → observability-family
Docs update              → docs-family
Research                 → data-research-family
Frontend work            → frontend-family
Memory / continuity      → context-family
```

### Step 2 — Add families as the task evolves

As you encounter triggers for other families, load them. Keep `/context-monitor` in mind.

### Step 3 — Check context before loading a third family

Before loading a third or subsequent family, run `/context-monitor` to verify you have budget. If you are at `orange` or `red`, do not load more — use `/context-prune` or `/handoff` instead.

---

## Subagent setup guide

When spawning a subagent, follow these rules to avoid context waste and capability gaps.

### What to include in every subagent prompt

```
1. The specific task (not the full project context).
2. The family or skill the subagent needs (by name).
3. The approximate token budget remaining in the parent session.
4. The output format and destination file.
5. A stop condition (when to stop and return, not when to keep going).
6. Whether to write output to a file or return it inline.
   Rule: if output > ~2 000 tokens, write to file.
```

### What NOT to send to subagents

- The full conversation history
- All loaded plugin manifests
- Large file reads the subagent doesn't need
- "Load all families" instructions

### Example subagent prompt structure

```markdown
## Subagent task: [name]

**Model:** claude-sonnet-4-6
**Context budget:** ~[N] tokens remaining in parent session
**Plugin to load:** [family-name] (for /skill-name)

### Task
[Specific bounded task — 2–5 sentences max]

### Input files
- [path]: [why needed]

### Output
Write result to: `.agents/[output-file].md`
Do NOT return output inline if it exceeds 2 000 tokens.

### Stop condition
Stop when: [clear stopping criterion]
Do not: [what to avoid]
```

---

## Context monitoring guidance

### When to check

| Situation | Action |
|---|---|
| About to load a 3rd or later family | Run `/context-monitor` first |
| About to read a file > 500 lines | Check context level |
| Spawning 2 or more subagents | Check context level before each |
| Receiving a tool result > 200 lines | Check context level after |
| Session expected to run > 30 min | Check at start and midpoint |
| Response feels slow or truncated | Check immediately |

### Context levels and actions

| Level | % used | Action |
|---|---|---|
| `green` | < 40% | Continue normally |
| `yellow` | 40–65% | Prefer lazy loading; avoid large file reads |
| `orange` | 65–80% | Run `/context-prune`; stop loading new families |
| `red` | 80–90% | Run `/handoff` immediately |
| `critical` | > 90% | Write handoff and stop all new work |

### Context usage log

Every `/context-monitor` invocation writes a JSONL entry to `.agents/logs/context-usage.jsonl`. Review this file across sessions to understand which tasks or models consume context most rapidly.

```jsonl
{"ts":"2026-06-04T12:00:00Z","model":"claude-sonnet-4-6","session":"abc123","used_tokens":45000,"limit_tokens":200000,"pct_used":0.225,"status":"green","loaded_families":["rpi","context-family"],"note":""}
```

---

## Model routing guidance

Use the right model for the task to conserve context and budget.

| Task type | Recommended model | Reason |
|---|---|---|
| Complex architecture, long-context review | claude-opus-4-8 | Highest reasoning, 200k context |
| Most delivery and coding tasks | claude-sonnet-4-6 | Best balance of quality and speed |
| Fast classification, triage, short tasks | claude-haiku-4-5 | Cheapest per token, lowest latency |
| Multimodal review or broad comparison | gemini-1.5-pro | 1M context, multimodal |
| Offline / private / cost-constrained | local LLM | No external calls |

When routing to a different model, always use `/llm-ide-handoff-packager` to produce a self-contained handoff. Do not assume the target model has access to the current conversation context.

---

## PDR and swarm routing

When you receive a PDR package, audit bundle, or governance artifact:

1. Load `agent-governance-family`.
2. Run `/repo-pdr-swarm-router` to decompose, classify, and route work to agents.
3. For each routed task that targets a different LLM or IDE, run `/llm-ide-handoff-packager` to convert to a self-contained handoff.
4. After routing is complete, run `/chromatic-memory-registrar` to save the decision register and project state.

---

## Durable memory after major events

After any of these events, run `/chromatic-memory-registrar`:

- A PDR completed or routed
- A significant architectural decision made
- A repo migrated or major refactor completed
- An agent dispatched with a complex task
- A governance audit completed
- A release shipped

This prevents loss of continuity when sessions end, models switch, or a new agent picks up work.

---

## Governance bridges

Two reference documents connect the skill ecosystem to the broker and to the parallel Poly-Chromatic operating stack. Consult them when your task crosses either boundary:

- **`SKILL_BRIDGE.md`** (in `.02_Plugins/`) — maps each Poly-Chromatic operating skill (`project-level-operator`, `cognitive-stack-architect`, `chromatic-systems-auditor`, `queue-dispatcher`, `fusion-computer`, etc.) to its nearest plugin-family equivalent, stating the relationship (equivalent / partial overlap / gap) and when to use each. Read this before acting on guidance from the operating stack so you don't apply two conflicting taxonomies.
- **`plugin-access-policy.md`** (in `.03_Harness Governance/governance/`) — maps each broker permission profile (`read_only`, `issue_triage`, `patch_standard`, `cleanup_limited`) to the plugin families that profile is allowed to load. Before loading a family, confirm it's permitted for your broker profile.

---

## Anti-patterns to avoid

| Anti-pattern | Correct approach |
|---|---|
| Loading all 13 families at session start | Load 1–2 families; add more as triggers appear |
| Sending full conversation history to a subagent | Send only the task, input files, and stop condition |
| Returning large output inline from a subagent | Write to `.agents/[output-file].md` and return the path |
| Creating a new skill for a minor variation | Add a reference or template to an existing skill |
| Skipping `/context-monitor` when loading families | Always check before adding the 3rd+ family |
| Relying on chat history as project memory | Use `/chromatic-memory-registrar` after major events |
| Sending a PDR to another LLM without a handoff pack | Always use `/llm-ide-handoff-packager` for cross-LLM work |
| Guessing at GitHub org settings | Use `/github-org-governance-manager` to produce a verified checklist |

---

## Family dependency map

Some skills work best in sequence. These are the key multi-family flows:

### PDR intake and dispatch
```
agent-governance-family (/repo-pdr-swarm-router)
  → toolchain-family (/llm-ide-handoff-packager)   [if cross-LLM]
  → context-family (/chromatic-memory-registrar)     [save state]
```

### Feature delivery with governance
```
rpi (/discovery → /plan → /crank → /validation)
  → security-family (/security-pr)                  [before merge]
  → release-family (/deploy-checklist)               [before ship]
  → context-family (/chromatic-memory-registrar)     [save state]
```

### Context recovery
```
observability-family (/context-monitor)
  → context-family (/context-prune)                  [if orange]
  → toolchain-family (/handoff)                       [if red]
```

### Cross-LLM handoff
```
[any family producing work]
  → toolchain-family (/llm-ide-handoff-packager)
  → context-family (/chromatic-memory-registrar)
```
