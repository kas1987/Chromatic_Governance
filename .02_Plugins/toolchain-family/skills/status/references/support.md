# Status Skill — Extended Reference

Supplementary content for the `status` skill. Use for output format reference, state inspection, and tool installation.

---

## Dashboard Output Format

Full dashboard structure (all sections present):

```
## Current Work
  Phase: implement | Epic: EPIC-42 | Task: [BD-007] Add endpoint
  In progress: 1 | Blocked: 0

## Recent Validations
  [PASS] 2026-04-26 — vibe check on internal/api/
  [PASS] 2026-04-25 — test coverage at 78%

## Knowledge Flywheel
  Learnings: 14 | Patterns: 7 | Last sync: 2 days ago

## Goals
  ✅ Go coverage > 75%  (current: 78%)
  ❌ PR response < 24h  (current: 38h)

## Suggested Action
  → /implement BD-007 — in-progress task needs attention
```

---

## State File Reference

| File | Purpose | Location |
|------|---------|---------|
| `.agents/rpi/phased-state.json` | RPI phase | Current project dir |
| `.agents/evolve/cycle-history.jsonl` | Evolve cycles | Current project dir |
| `.agents/ao/chain.jsonl` | Flywheel chain | Current project dir |
| `.agents/beads/issues/` | Open beads issues | Current project dir |

---

## Tool Install Reference (Windows)

| Tool | Install |
|------|---------|
| `bd` (beads CLI) | Download from AgentOps releases |
| `ao` (AgentOps CLI) | Download from AgentOps releases |
| `jq` | `winget install jqlang.jq` |

---

## JSON Mode

Use `--json` flag to get machine-readable output:

```bash
/status --json
```

Returns structured JSON with all state sections. Useful for scripting or piping into other tools.

Example output:
```json
{
  "phase": "implement",
  "epic": "EPIC-42",
  "open_tasks": 3,
  "blocked_tasks": 0,
  "flywheel_velocity": "normal",
  "suggested_action": "/implement BD-007"
}
```
