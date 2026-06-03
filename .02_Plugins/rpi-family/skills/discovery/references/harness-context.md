# Harness Context — Discovery Contract

## Purpose

Every RPI invocation begins with STEP 0.5 which loads the canonical `~/.claude/AI_Harness.md` and writes a structured summary to `.agents/rpi/harness-context.json`. This gives every subsequent skill in the discovery DAG — and any sub-agent they spawn — access to the harness's global goals, topology, constraints, and best practices without re-reading the source file.

**Fail-Open Rule:** If `AI_Harness.md` does not exist or cannot be parsed, STEP 0.5 logs a warning and continues. Harness context is advisory — it enriches planning but never blocks it. A missing `AI_Harness.md` is not an error.

---

## AI_Harness.md Schema

`~/.claude/AI_Harness.md` must contain these sections (in order):

| Section | Machine-readable format | Purpose |
|---------|------------------------|---------|
| `## Global Goals` | Numbered list | Long-term objectives every plan must serve |
| `## Session Goal Template` | Markdown code block with YAML-like fields | Per-session intent declaration |
| `## Harness Topology` | Tables: agents, hooks, router tiers | Current harness components |
| `## Canonical References` | Table: system → path | Authoritative file paths |
| `## Constraints` | Numbered list, imperative sentences | Hard rules for every plan |
| `## Best Practices` | Bullet list | Distilled learnings from .agents/learnings/ |

---

## harness-context.json Shape

Written to `~/.claude/.agents/rpi/harness-context.json` by STEP 0.5:

```json
{
  "global_goals": "string — concatenated ## Global Goals items",
  "session_goal": "string — current ## Session Goal Template entry",
  "topology": "string — ## Harness Topology summary (agents + hook chain + router tiers)",
  "constraints": "string — ## Constraints list",
  "best_practices": "string — ## Best Practices summary",
  "loaded_at": "ISO8601 timestamp"
}
```

---

## How Other Skills Use It

Any skill invoked after discovery can read `harness-context.json` for context:

```bash
HARNESS_CTX="${HOME}/.claude/.agents/rpi/harness-context.json"
if [ -f "$HARNESS_CTX" ]; then
  constraints=$(jq -r '.constraints' "$HARNESS_CTX" 2>/dev/null || echo "")
  # inject into prompts, pre-mortem checks, plan boundaries, etc.
fi
```

### Per-step usage in discovery:
- **STEP 1 (brainstorm):** Check if the user's goal aligns with `global_goals`. If misaligned, surface as a brainstorm concern — not a blocker.
- **STEP 2 (ao search):** Append `topology` summary to the search query for richer context matching.
- **STEP 3 (research):** Include `constraints` in the explore agent prompt under a `## Harness Constraints` heading so the explorer knows what to watch for.
- **STEP 4 (plan):** Validate each issue's router tier assignment against the topology table. Flag T4 work that could be T2. Add `constraints` to plan's `## Boundaries → Always` section.
- **STEP 5 (pre-mortem):** Load `constraints` as `known_risks` in the council packet. Any plan that violates a constraint is an automatic FAIL finding.

---

## Example

Given `AI_Harness.md` with constraint #6: *"Route tier 0-2 work to local — do not use cloud models for mechanical work"*

A plan issue like:
> "Generate 50 fixture JSON files using Claude Orchestrator (claude-sonnet-4-6)"

Pre-mortem would flag: *"pm-YYYYMMDD-NNN: Constraint #6 violated — fixture generation is tier-0 mechanical work, must route to Ollama (tier 0) or Featherless (tier 1), not Claude Orchestrator (tier 4)."*

---

## Updating AI_Harness.md

`AI_Harness.md` should be updated when:
- New agents or squads are added to the Multica workspace
- Hook chain changes (new hooks, reordering)
- Router tier policies change (`governance/multi-router-matrix.yaml` updated)
- Global goals evolve (new product direction, completed goals)
- New best practices distilled from `.agents/learnings/`

The `/evolve` skill can auto-update `AI_Harness.md` as part of session close-out.
