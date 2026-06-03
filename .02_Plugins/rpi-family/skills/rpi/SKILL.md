---
name: rpi
description: 'Full RPI lifecycle orchestrator. Delegates to /discovery, /crank, /validation phase skills. One command, full lifecycle with complexity classification, --from routing, and optional loop. Triggers: "rpi", "full lifecycle", "research plan implement", "end to end".'
skill_api_version: 1
user-invocable: true
context:
  window: fork
  intent:
    mode: task
  sections:
    exclude: [HISTORY]
  intel_scope: full
metadata:
  tier: meta
  dependencies:
    - discovery   # phase 1 orchestrator
    - crank       # phase 2 orchestrator
    - validation  # phase 3 orchestrator
    - ratchet     # checkpoint tracking
  internal: false
permissions:
  allowed: [Read, Glob, Grep, Bash, Write, Skill, Agent]
  forbidden: [Edit, WebFetch, WebSearch, NotebookEdit, LSP, TaskCreate, TaskUpdate, TaskList, TaskGet]
  bash_scope: "git log/branch/diff/status, ao ratchet, jq, date, mkdir, rm, printf"
  write_scope: ".agents/rpi/, .agents/chronicle/ — no source code"
  model_tier: large
---

## Tool Governance

> Full registry: `skills/shared/references/skill-tool-registry.md`. Violations tracked in mc-6a5.

| Allowed | Forbidden |
|---------|-----------|
| Read, Glob, Grep, Bash, Write, Skill, Agent | Edit, WebFetch, WebSearch, NotebookEdit, LSP, TaskCreate, TaskUpdate, TaskList, TaskGet |

**Bash:** git log/branch/diff/status, ao ratchet, jq, date, mkdir, rm, printf — no curl, wget, ssh
**Write:** .agents/rpi/, .agents/chronicle/ — no source code, no skill files


# /rpi — Full RPI Lifecycle Orchestrator

> **Quick Ref:** One command, full lifecycle. `/discovery` → `/crank` → `/validation`. Thin wrapper that delegates to phase orchestrators.


> **Brownfield safety:** Before Phase 1 (discovery), always check the current git branch
> and read `.agents/rpi/execution-packet.json` if it exists. Do not start a new RPI on top of
> an in-flight epic. See the `brownfield-discovery-must-check-feature-branches` learning.

**YOU MUST EXECUTE THIS WORKFLOW. Do not just describe it.**

**THREE-PHASE RULE + FULLY AUTONOMOUS.** Read `references/autonomous-execution.md` — it defines the mandatory 3-phase lifecycle, autonomous execution rules, anti-patterns, and phase completion logging. Unless `--interactive` is set, RPI runs hands-free. Do NOT stop after Phase 2. Do NOT ask the user anything between phases.

## Quick Start

```bash
/rpi "add user authentication"                        # full lifecycle
/rpi --interactive "add user authentication"          # human gates in discovery only
/rpi --from=discovery "add auth"                      # resume discovery
/rpi --from=implementation ag-23k                      # skip to crank with existing epic
/rpi --from=validation                                 # run validation only
/rpi --loop --max-cycles=3 "add auth"                 # iterate-on-fail loop
/rpi --deep "refactor payment module"                  # force full council ceremony
/rpi --fast-path "fix typo in readme"                  # force lightweight ceremony
/rpi --no-test-first "add auth"                       # opt out of strict-quality
```

## Lifecycle Ownership

Phase orchestrators own all sub-skill sequencing, retry gates, and phase budgets:
- Phase 1: `/discovery` handles brainstorm → design (when PRODUCT.md exists) → search → research → plan → pre-mortem and writes the execution packet.
- Phase 2: `/crank` handles wave-based implementation plus implementation retries.
- Phase 3: `/validation` handles vibe → post-mortem → retro → forge plus validation retries.

`/rpi` stays thin: it owns setup, complexity classification, phase routing, the implementation gate, the validation-fail-to-crank loop, and the final report.

## Execution Steps

### Step 0: Setup + Classify

```bash
mkdir -p .agents/rpi .agents/chronicle

# Report prior Chronicle results before clearing state (skip when --no-chronicle)
if [ "${NO_CHRONICLE:-false}" != "true" ] && [ -f .agents/chronicle/complete.json ]; then
  PRIOR_EPIC=$(jq -r '.epic_id // "unknown"' .agents/chronicle/complete.json 2>/dev/null)
  PRIOR_N=$(jq -r '.items_created // 0' .agents/chronicle/complete.json 2>/dev/null)
  PRIOR_BEADS=$(jq -r '.beads_created // [] | join(", ")' .agents/chronicle/complete.json 2>/dev/null)
  PRIOR_STATUS=$(jq -r '.status // "unknown"' .agents/chronicle/complete.json 2>/dev/null)
  echo "Prior Chronicle ($PRIOR_EPIC, status=$PRIOR_STATUS): $PRIOR_N beads created [$PRIOR_BEADS]"
fi

# Reset stale chronicle state from prior run
rm -f .agents/chronicle/complete.json
> .agents/chronicle/events.jsonl
```

**Determine starting phase:**
- default: `discovery`
- `--from=implementation` (aliases: `crank`) → skip to Phase 2
- `--from=validation` (aliases: `vibe`, `post-mortem`) → skip to Phase 3
- aliases `research`, `plan`, `pre-mortem`, `brainstorm` map to `discovery`
- If input looks like an epic ID (`ag-*`) and `--from` is not set, start at implementation.

**Classify complexity:**

| Level | Criteria | Behavior |
|-------|----------|----------|
| `fast` | Goal <=30 chars, no complex/scope keywords | Discovery → crank only. Skip validation. |
| `standard` | Goal 31-120 chars, or 1 scope keyword | Full 3-phase. Gates use `--quick`. |
| `full` | Complex-operation keyword, 2+ scope keywords, or >120 chars | Full 3-phase. Gates use full council. |

**Complex-operation keywords:** `refactor`, `migrate`, `migration`, `rewrite`, `redesign`, `rearchitect`, `overhaul`, `restructure`, `reorganize`, `decouple`, `deprecate`, `split`, `extract module`, `port`

**Scope keywords:** `all`, `entire`, `across`, `everywhere`, `every file`, `every module`, `system-wide`, `global`, `throughout`, `codebase`

**Overrides:** `--deep` forces `full`. `--fast-path` forces `fast`.

Log:
```
RPI mode: rpi-phased (complexity: <level>)
```

Initialize state:
```
rpi_state = {
  goal: "<goal string>",
  epic_id: null,
  phase: "<discovery|implementation|validation>",
  complexity: "<fast|standard|full>",
  test_first: <true by default; false only when --no-test-first>,
  chronicle: <true by default; false only when --no-chronicle>,
  cycle: 1,
  max_cycles: <3 when --loop; overridden by --max-cycles>,
  verdicts: {}
}
```

Write first chronicle event:
```bash
printf '%s\n' "$(jq -cn \
  --arg goal "$RPI_GOAL" \
  --arg complexity "$COMPLEXITY" \
  '{event:"rpi_start",goal:$goal,epic_id:null,complexity:$complexity,timestamp:(now|todate)}')" \
  >> .agents/chronicle/events.jsonl
```

### Phase 1: Discovery

Delegate to `/discovery`:

```
Skill(skill="discovery", args="<goal> [--interactive] --complexity=<level>")
```

After `/discovery` completes:
1. Check completion marker: `<promise>DONE</promise>` or `<promise>BLOCKED</promise>`
2. If BLOCKED: stop. Discovery handles its own retries (max 3 pre-mortem attempts). Manual intervention needed.
3. If DONE: extract epic-id from `.agents/rpi/execution-packet.json`
4. Store `rpi_state.epic_id` and `rpi_state.verdicts.pre_mortem`
5. Write chronicle event:
   ```bash
   PLAN_PATH=$(ls -t .agents/plans/*.md 2>/dev/null | head -1)
   printf '%s\n' "$(jq -cn \
     --arg epic "$EPIC_ID" \
     --arg plan "${PLAN_PATH:-}" \
     --arg verdict "${PRE_MORTEM_VERDICT:-unknown}" \
     '{event:"discovery_complete",epic_id:$epic,plan_path:$plan,pre_mortem_verdict:$verdict,timestamp:(now|todate)}')" \
     >> .agents/chronicle/events.jsonl
   ```
6. Log: `PHASE 1 COMPLETE ✓ (discovery) — proceeding to Phase 2`

### Phase 2: Implementation

Requires `rpi_state.epic_id`.

```
Skill(skill="crank", args="<epic-id> [--test-first] [--no-test-first]")
```

**Implementation gate (max 3 attempts):**
- `<promise>DONE</promise>`: proceed to validation
- `<promise>BLOCKED</promise>`: retry with block context (max 2 retries)
  - Re-invoke `/crank` with epic-id + block reason
  - If still BLOCKED after 3 total: stop, manual intervention needed
- `<promise>PARTIAL</promise>`: retry remaining (max 2 retries)
  - Re-invoke `/crank` with epic-id (picks up unclosed issues)
  - If still PARTIAL after 3 total: stop, manual intervention needed

Record:
```bash
ao ratchet record implement 2>/dev/null || true
```

Write chronicle event:
```bash
printf '%s\n' "$(jq -cn \
  --arg epic "$EPIC_ID" \
  '{event:"phase2_complete",epic_id:$epic,timestamp:(now|todate)}')" \
  >> .agents/chronicle/events.jsonl
```

Log: `PHASE 2 COMPLETE ✓ (implementation) — proceeding to Phase 3`

**DO NOT STOP HERE.** Do not ask the user to commit. Do not summarize and wait. Proceed IMMEDIATELY to Phase 3.

### Phase 3: Validation Gate + Chronicle Spawn

**Skip if:** complexity == `fast` (fast-path runs discovery + crank only).

**Default (Chronicle active):** Run `/vibe` as the quality gate only, then spawn Chronicle in background to handle post-mortem + retro + forge + beads feeding. Do NOT call `/validation` when Chronicle is active — that would double-run post-mortem.

**When `--no-chronicle`:** Call `/validation` as before (full blocking pipeline).

#### Phase 3a: Vibe Gate

```
Skill(skill="vibe", args="recent [--quick for standard; full for full complexity]")
```

**Vibe-to-crank loop (max 3 total attempts):**
- `PASS` or `WARN`: write event, spawn Chronicle, finish
- `FAIL`: vibe found defects
  1. Extract findings from vibe output
  2. Re-invoke `/crank` with epic-id + findings context
  3. Re-run vibe
  4. If still FAIL after 3 total: spawn Chronicle (FAIL recorded), stop implementation retries

Record:
```bash
ao ratchet record vibe 2>/dev/null || true
```

Write chronicle event:
```bash
printf '%s\n' "$(jq -cn \
  --arg verdict "$VIBE_VERDICT" \
  '{event:"vibe_complete",verdict:$verdict,timestamp:(now|todate)}')" \
  >> .agents/chronicle/events.jsonl
```

#### Phase 3b: Spawn Chronicle (skip if `--no-chronicle`)

Read `references/chronicle-agent.md` for the full prompt template and spawn instructions.

Assemble context from `events.jsonl` (inline into Chronicle prompt — truncate to last 20 lines if > 2000 chars):

```bash
EVENTS=$(tail -20 .agents/chronicle/events.jsonl | head -c 2000)
export RPI_CHRONICLE_ACTIVE=true
```

Spawn:
```python
Agent(
  description="chronicle-<epic-id>: post-mortem + retro + flywheel + beads feeding",
  subagent_type="general-purpose",
  model="sonnet",
  run_in_background=True,
  prompt=<chronicle prompt template from references/chronicle-agent.md,
          with epic_id, goal, vibe_verdict, events_content substituted>
)
```

Log: `PHASE 3 COMPLETE ✓ — vibe gate done, Chronicle running in background`

### Step Final: Report + Loop

**Report:** Summarize all phase verdicts and epic status. When Chronicle is active, report:
```
Implementation: DONE ✓
Vibe: <verdict>
Post-mortem: running in background (Chronicle agent)
Next-work → beads: Chronicle will feed results into backlog on completion
Check .agents/chronicle/complete.json for Chronicle status
```

**Optional loop (`--loop`):** If vibe verdict is FAIL (Chronicle active) or validation verdict is FAIL (`--no-chronicle`) and `cycle < max_cycles`:
1. Extract 3 concrete fixes from the post-mortem report
2. Increment `rpi_state.cycle`
3. Re-invoke `/rpi` from discovery with a tightened goal
4. PASS/WARN stops the loop

**Optional spawn-next (`--spawn-next`):** After PASS/WARN finish:
1. Read `.agents/rpi/next-work.jsonl` for harvested follow-up items
2. Report with suggested next `/rpi` command
3. Do NOT auto-invoke

Read `references/report-template.md` for full output format.
Read `references/error-handling.md` for failure semantics.

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--from=<phase>` | `discovery` | Start from `discovery`, `implementation`, or `validation` |
| `--interactive` | off | Human gates in discovery |
| `--auto` | on | Fully autonomous (no human gates). Inverse of `--interactive`. Passed through to `/discovery` and `/plan`. |
| `--loop` | off | Post-mortem FAIL triggers new cycle |
| `--max-cycles=<n>` | `3` | Max cycles when `--loop` enabled (default 3) |
| `--spawn-next` | off | Surface follow-up work after completion |
| `--test-first` | on | Strict-quality (passed to `/crank`) |
| `--no-test-first` | off | Opt out of strict-quality |
| `--fast-path` | auto | Force fast complexity |
| `--deep` | auto | Force full complexity |
| `--quality` | off | Pass `--strict-surfaces` to `/validation`, making all 4 surface failures blocking |
| `--no-chronicle` | off | Disable Chronicle; run full `/validation` synchronously (blocking post-mortem) |
| `--dry-run` | off | Report without mutating queue |
| `--no-budget` | off | Disable phase time budgets (passed to phase skills) |

## Phase Data Contracts
All transitions use filesystem artifacts (no in-memory coupling). The execution packet (`.agents/rpi/execution-packet.json`) carries `contract_surfaces` (repo execution profile), `done_criteria`, and queue claim/finalize metadata between phases. Sub-skills include /plan, /vibe, /post-mortem, and /pre-mortem. For detailed contract schemas, read `references/phase-data-contracts.md`.

## Complexity-Scaled Council Gates

### Phase 3: Pre-mortem
- `complexity == "low"` or `complexity == "fast"`: inline review, no spawning (`--quick`)
- `complexity == "medium"` or `complexity == "standard"`: inline fast default (`--quick`)
- `complexity == "high"` or `complexity == "full"`: full council, 2-judge minimum; retry gate: max 3 total attempts

### Phase 5: Final Vibe
- `complexity == "low"` or `complexity == "fast"`: inline review, no spawning (`--quick`)
- `complexity == "medium"` or `complexity == "standard"`: inline fast default (`--quick`)
- `complexity == "high"` or `complexity == "full"`: full council, 2-judge minimum; retry gate: max 3 total attempts

### Phase 6: Post-mortem (STEP 2)
- `complexity == "low"` or `complexity == "fast"`: inline review, no spawning (`--quick`)
- `complexity == "medium"` or `complexity == "standard"`: inline fast default (`--quick`)
- `complexity == "high"` or `complexity == "full"`: full council, 2-judge minimum; retry gate: max 3 total attempts

## Examples
Read `references/examples.md` for full lifecycle, resume, and interactive examples.

## Troubleshooting
Read `references/troubleshooting.md` for common problems and solutions.

**See also:** [discovery](../discovery/SKILL.md), [crank](../crank/SKILL.md), [validation](../validation/SKILL.md)

## Reference Documents

- [references/chronicle-agent.md](references/chronicle-agent.md) — Chronicle Observer spec, prompt template, beads feeder
- [references/complexity-scaling.md](references/complexity-scaling.md)
- [references/context-windowing.md](references/context-windowing.md)
- [references/gate-retry-logic.md](references/gate-retry-logic.md)
- [references/gate4-loop-and-spawn.md](references/gate4-loop-and-spawn.md)
- [references/phase-budgets.md](references/phase-budgets.md)
- [references/phase-data-contracts.md](references/phase-data-contracts.md)
- [references/report-template.md](references/report-template.md)
- [references/error-handling.md](references/error-handling.md)
- [references/examples.md](references/examples.md)
- [references/autonomous-execution.md](references/autonomous-execution.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [../shared/references/orchestration-as-prompt.md](../shared/references/orchestration-as-prompt.md)
