# Chronicle Agent — Short-Lived Post-Mortem Executor

> **Purpose:** Offload the full post-mortem lifecycle (post-mortem + retro + flywheel + beads feeding) from the main RPI agent. Chronicle is spawned *after* vibe with all needed context already assembled on disk — no polling, no long-running observation. It runs focused, exits, and writes a closed-loop signal.

---

## Architecture

```
/rpi Phase 0
  └── mkdir .agents/chronicle, write rpi_start event to events.jsonl

Phase 1: /discovery completes
  └── RPI writes discovery_complete event to events.jsonl

Phase 2: /crank completes (each wave)
  └── RPI writes wave_complete event per wave + phase2_complete at end

Phase 3: /vibe only (RPI)
  └── RPI writes vibe_complete event to events.jsonl
      RPI assembles context summary from events.jsonl
      RPI spawns Chronicle (run_in_background=True) with full context in prompt
      RPI reports "Done — Chronicle handling post-mortem in background" → exits

Chronicle (background, short-lived)
  ├── Phase A: Run /post-mortem with chronicle context
  ├── Phase B: Run /retro
  ├── Phase C: Run /forge (flywheel)
  ├── Phase D: Beads feeding (next-work.jsonl → bd create)
  └── Phase E: Write complete.json → done
```

**Main agent is freed immediately after spawning Chronicle.** No polling. Chronicle has everything it needs from `events.jsonl` — it does not wait or observe.

---

## events.jsonl — The Context Feed

RPI writes one JSON line per significant lifecycle event to `.agents/chronicle/events.jsonl`. Chronicle reads this file at spawn time — it is the primary context source.

### Event Schema

```jsonl
{"event":"rpi_start","goal":"<goal>","epic_id":null,"complexity":"standard","timestamp":"..."}
{"event":"discovery_complete","epic_id":"ag-xxx","plan_path":".agents/plans/...","pre_mortem_verdict":"PASS","timestamp":"..."}
{"event":"wave_complete","wave":1,"epic_id":"ag-xxx","tasks_done":["ag-1","ag-2"],"commits":["abc123"],"status":"done","timestamp":"..."}
{"event":"wave_complete","wave":2,"epic_id":"ag-xxx","tasks_done":["ag-3"],"commits":["def456"],"status":"done","timestamp":"..."}
{"event":"phase2_complete","epic_id":"ag-xxx","waves_total":2,"files_changed":["src/auth.go","tests/auth_test.go"],"timestamp":"..."}
{"event":"vibe_complete","verdict":"PASS|WARN|FAIL","timestamp":"..."}
```

**Who writes what:**

| Event | Written by | When |
|-------|-----------|------|
| `rpi_start` | `/rpi` Step 0 | Before Phase 1 |
| `discovery_complete` | `/rpi` after Phase 1 | After `/discovery` returns DONE |
| `wave_complete` | `/rpi` after each crank wave (or `/crank` directly) | Per wave completion |
| `phase2_complete` | `/rpi` after Phase 2 | After `/crank` returns DONE |
| `vibe_complete` | `/rpi` after vibe | After `/vibe` verdict is known |

---

## Governance

```
## GOVERNANCE CONSTRAINTS
Role: CHRONICLE
Worker ID: chronicle-<epic-id>
Wave: post-execution (single run, no loops)

FILE SCOPE (writes permitted):
.agents/chronicle/chronicle.md
.agents/chronicle/status.json
.agents/chronicle/complete.json
.agents/learnings/
.agents/findings/
.agents/rpi/next-work.jsonl

PERMITTED ACTIONS:
- Read, Glob, Grep any file for context
- Bash: git log, git show, git diff (read-only), jq, grep, ls, date
- Bash: bd create — beads feeding phase only
- Skill invocations: post-mortem, retro, forge

FORBIDDEN:
- Agent (spawn subagents)
- Read credential/secret files: settings.json, .env, *.pem, *.key
- git commit, push, reset, add
- Modify source code, test files, plan files, or skill files
- Any Skill other than post-mortem, retro, forge
```

---

## Disk Contract

| Path | Written by | Purpose |
|------|-----------|---------|
| `.agents/chronicle/events.jsonl` | RPI | Context feed for Chronicle spawn |
| `.agents/chronicle/chronicle.md` | Chronicle | Running execution log |
| `.agents/chronicle/status.json` | Chronicle | Progress signal (optional poll by main) |
| `.agents/chronicle/complete.json` | Chronicle | Closed-loop signal for next dispatch |
| `.agents/rpi/next-work.jsonl` | Post-mortem | Items Chronicle converts to beads |

### complete.json schema

```json
{
  "status": "done|partial|failed",
  "epic_id": "ag-xxxx",
  "post_mortem_verdict": "PASS|WARN|FAIL",
  "items_created": 3,
  "beads_created": ["ag-yyyy", "ag-zzzz"],
  "flywheel_fired": true,
  "timestamp": "2026-05-27T13:00:00Z",
  "error": null
}
```

---

## Chronicle Prompt Template

Populated by RPI at spawn time. Pass `events.jsonl` content inline — Chronicle does not need to re-read it from disk to start (reduces cold-start latency).

```
## GOVERNANCE CONSTRAINTS
Role: CHRONICLE
Worker ID: chronicle-<epic-id>
Wave: post-execution

FILE SCOPE:
.agents/chronicle/chronicle.md
.agents/chronicle/status.json
.agents/chronicle/complete.json
.agents/learnings/
.agents/findings/
.agents/rpi/next-work.jsonl

PERMITTED ACTIONS:
- Read, Glob, Grep any file for context
- Bash: git log, git show, git diff (read-only), jq, grep, ls, date
- Bash: bd create — beads feeding phase only
- Skill: post-mortem, retro, forge only

FORBIDDEN: Agent (spawn), git commit/push, source code edits, other skills

---

You are the Chronicle for RPI epic <epic-id>.
Goal: <original goal>
Vibe verdict: <PASS|WARN|FAIL>

## Assembled Context (from events.jsonl)

<inline content of .agents/chronicle/events.jsonl — all events>

## Your Execution Steps

### Step 1: Initialize

```bash
echo '{"phase":"starting","epic_id":"<epic-id>","timestamp":"'$(date -Iseconds)'"}' \
  > .agents/chronicle/status.json
echo "# Chronicle: <epic-id>" > .agents/chronicle/chronicle.md
echo "Goal: <goal>" >> .agents/chronicle/chronicle.md
echo "Vibe: <vibe-verdict>" >> .agents/chronicle/chronicle.md
```

### Step 2: Run Post-Mortem

Run with `--process-only` if vibe is FAIL (skip council — implementation is already flagged):

```
# PASS or WARN: full post-mortem
Skill(skill="post-mortem", args="<epic-id>")

# FAIL: skip council (it already failed vibe), extract learnings from the failure
Skill(skill="post-mortem", args="<epic-id> --process-only")
```

Append result to chronicle:
```bash
echo "Post-mortem: done" >> .agents/chronicle/chronicle.md
```

### Step 3: Run Retro

```
Skill(skill="retro")
```

```bash
echo "Retro: done" >> .agents/chronicle/chronicle.md
```

### Step 4: Run Forge (flywheel)

```bash
if command -v ao &>/dev/null; then
  ao forge transcript --last-session --queue --quiet 2>/dev/null || true
  echo "Forge: fired" >> .agents/chronicle/chronicle.md
else
  echo "Forge: skipped (ao unavailable)" >> .agents/chronicle/chronicle.md
fi
```

### Step 5: Beads Feeding

Read unclaimed next-work items and create bd issues:

```bash
BEADS_CREATED=()
NEXT_WORK=".agents/rpi/next-work.jsonl"
EPIC_ID="<epic-id>"

if [ -f "$NEXT_WORK" ]; then
  # Extract unclaimed items from the most recent entry for this epic
  while IFS= read -r item_b64; do
    [ -z "$item_b64" ] && continue
    item=$(echo "$item_b64" | base64 --decode 2>/dev/null) || continue

    title=$(echo "$item" | jq -r '.title // empty')
    type=$(echo "$item" | jq -r '.type // "task"')
    severity=$(echo "$item" | jq -r '.severity // "medium"')
    desc=$(echo "$item" | jq -r '.description // empty')
    source=$(echo "$item" | jq -r '.source // "council-finding"')

    [ -z "$title" ] || [ -z "$desc" ] && continue

    # Map type → bd type
    case "$type" in
      tech-debt|improvement) bd_type="chore" ;;
      feature)               bd_type="feature" ;;
      bug|pattern-fix)       bd_type="bug" ;;
      *)                     bd_type="task" ;;
    esac

    # Map severity → bd priority
    case "$severity" in
      high)   bd_priority="P1" ;;
      medium) bd_priority="P2" ;;
      low)    bd_priority="P3" ;;
      *)      bd_priority="P2" ;;
    esac

    new_id=$(bd create "$title" \
      --type "$bd_type" \
      --priority "$bd_priority" \
      --description "$desc. Harvested from $source (epic $EPIC_ID)." \
      --deps "discovered-from:$EPIC_ID" \
      2>/dev/null | grep -oE '[a-z]+-[0-9a-z]+' | head -1)

    if [ -n "$new_id" ]; then
      BEADS_CREATED+=("$new_id")
      echo "Created bead: $new_id — $title" >> .agents/chronicle/chronicle.md
    fi
  done < <(jq -r --arg epic "$EPIC_ID" '
    select(.source_epic == $epic and (.consumed != true))
    | .items[]
    | select(.consumed != true and .claim_status != "in_progress")
    | @base64
  ' "$NEXT_WORK" 2>/dev/null)

  # Mark consumed
  if [ ${#BEADS_CREATED[@]} -gt 0 ]; then
    CONSUMED_AT=$(date -Iseconds)
    CONSUMER="chronicle-$EPIC_ID"
    python3 -c "
import json, sys, os
f = sys.argv[1]; epic = sys.argv[2]; consumer = sys.argv[3]; ts = sys.argv[4]
lines = open(f).readlines() if os.path.exists(f) else []
out = []
for line in lines:
    line = line.strip()
    if not line: continue
    try:
        e = json.loads(line)
        if e.get('source_epic') == epic and not e.get('consumed'):
            for item in e.get('items', []):
                if not item.get('consumed'):
                    item.update({'consumed':True,'claim_status':'consumed',
                                 'consumed_by':consumer,'consumed_at':ts})
            e['consumed'] = all(i.get('consumed') for i in e.get('items',[]))
        out.append(json.dumps(e))
    except Exception:
        out.append(line)
open(f,'w').write('\n'.join(out)+'\n')
" "$NEXT_WORK" "$EPIC_ID" "$CONSUMER" "$CONSUMED_AT" 2>/dev/null || true
  fi
else
  echo "No next-work.jsonl — skipping beads feeding" >> .agents/chronicle/chronicle.md
fi
```

### Step 6: Write complete.json

```bash
ITEMS_N=${#BEADS_CREATED[@]}
BEADS_JSON=$(printf '%s\n' "${BEADS_CREATED[@]}" | jq -R . | jq -s . 2>/dev/null || echo "[]")
PM_VERDICT=$(jq -r '.verdict // "unknown"' \
  "$(ls -t .agents/council/*post-mortem*.md 2>/dev/null | head -1)" 2>/dev/null || echo "unknown")

jq -n \
  --arg status "done" \
  --arg epic_id "$EPIC_ID" \
  --arg pm_verdict "$PM_VERDICT" \
  --arg vibe_verdict "<vibe-verdict>" \
  --arg timestamp "$(date -Iseconds)" \
  --argjson items_created "$ITEMS_N" \
  --argjson beads_created "${BEADS_JSON}" \
  '{
    status: $status,
    epic_id: $epic_id,
    post_mortem_verdict: $pm_verdict,
    vibe_verdict: $vibe_verdict,
    items_created: $items_created,
    beads_created: $beads_created,
    flywheel_fired: true,
    timestamp: $timestamp,
    error: null
  }' > .agents/chronicle/complete.json

echo "Chronicle complete. $ITEMS_N beads created."
```
```

---

## Spawning the Chronicle (called from `/rpi` Phase 3)

After vibe verdict is known, RPI assembles the inline events context and spawns:

```python
import json

events_content = open(".agents/chronicle/events.jsonl").read()
# truncate if > 2000 chars to avoid context bloat
if len(events_content) > 2000:
    lines = events_content.strip().split("\n")
    events_content = "\n".join(lines[-20:])  # keep last 20 events

chronicle_prompt = CHRONICLE_PROMPT_TEMPLATE.format(
    epic_id=epic_id,
    goal=rpi_state["goal"],
    vibe_verdict=vibe_verdict,
    events_content=events_content,
)

Agent(
    description=f"chronicle-{epic_id}: post-mortem + retro + flywheel + beads feeding",
    subagent_type="general-purpose",
    model="sonnet",
    run_in_background=True,
    prompt=chronicle_prompt,
)
```

Or via Task tool in native teams context:

```
Task(
  subagent_type="general-purpose",
  model="sonnet",
  run_in_background=True,
  description="chronicle-<epic-id>: post-mortem executor",
  prompt=<populated chronicle prompt>
)
```

---

## Event Writing Helpers

Add these bash snippets to the relevant RPI steps:

```bash
# Phase 0 — rpi_start
CHRONICLE_DIR=".agents/chronicle"
mkdir -p "$CHRONICLE_DIR"
rm -f "$CHRONICLE_DIR/trigger.json" "$CHRONICLE_DIR/complete.json"
printf '%s\n' "$(jq -cn --arg goal "$RPI_GOAL" --arg complexity "$COMPLEXITY" \
  '{event:"rpi_start",goal:$goal,epic_id:null,complexity:$complexity,timestamp:(now|todate)}')" \
  >> "$CHRONICLE_DIR/events.jsonl"

# Phase 1 complete — discovery_complete
printf '%s\n' "$(jq -cn --arg epic "$EPIC_ID" --arg plan "$PLAN_PATH" --arg verdict "$PRE_MORTEM_VERDICT" \
  '{event:"discovery_complete",epic_id:$epic,plan_path:$plan,pre_mortem_verdict:$verdict,timestamp:(now|todate)}')" \
  >> "$CHRONICLE_DIR/events.jsonl"

# Phase 2 — wave_complete (call after each crank wave, if available)
printf '%s\n' "$(jq -cn --arg epic "$EPIC_ID" --argjson wave "$WAVE_NUM" --argjson tasks "$TASKS_JSON" \
  '{event:"wave_complete",epic_id:$epic,wave:$wave,tasks_done:$tasks,status:"done",timestamp:(now|todate)}')" \
  >> "$CHRONICLE_DIR/events.jsonl"

# Phase 2 complete — phase2_complete
printf '%s\n' "$(jq -cn --arg epic "$EPIC_ID" \
  '{event:"phase2_complete",epic_id:$epic,timestamp:(now|todate)}')" \
  >> "$CHRONICLE_DIR/events.jsonl"

# After vibe — vibe_complete (triggers spawn)
printf '%s\n' "$(jq -cn --arg verdict "$VIBE_VERDICT" \
  '{event:"vibe_complete",verdict:$verdict,timestamp:(now|todate)}')" \
  >> "$CHRONICLE_DIR/events.jsonl"
```

---

## Failure Handling

Chronicle never blocks the closed loop. Each phase is best-effort:

| Failure | Behavior |
|---------|----------|
| Post-mortem FAIL verdict | Continue to retro + forge + beads — FAIL is recorded in complete.json |
| retro skill unavailable | Log warning, skip, continue |
| ao / forge unavailable | Skip forge, continue to beads |
| bd CLI unavailable | Write items to `.agents/chronicle/pending-beads.md` for manual pickup |
| Any step throws | Log error to chronicle.md, write `complete.json` with `status:"partial"` |

---

## Stop Hook Fallback (optional hardening)

If the RPI session ends before Chronicle finishes, a `Stop` hook can detect incomplete chronicles and re-queue:

```bash
# ~/.claude/hooks/chronicle-requeue.sh
# Called by Stop hook if .agents/chronicle/trigger exists but complete does not
CHRON=".agents/chronicle"
if ls "$CHRON"/events.jsonl 2>/dev/null | head -1 | grep -q . \
   && [ ! -f "$CHRON/complete.json" ]; then
  EPIC_ID=$(jq -r 'select(.event=="discovery_complete") | .epic_id' \
    "$CHRON/events.jsonl" 2>/dev/null | tail -1)
  [ -n "$EPIC_ID" ] && echo "WARN: Chronicle for $EPIC_ID incomplete — re-queue via CronCreate or manual /post-mortem $EPIC_ID"
fi
```

This is advisory only — it warns the user so they can re-run `/post-mortem <epic-id>` manually if needed.

---

## Closed Loop

```
/rpi "<goal>"
  │
  ├── events.jsonl populated throughout execution
  │
Phase 2 done + vibe gate
  │
  ├── Chronicle spawned (background, events.jsonl in prompt)
  │   └── /post-mortem → /retro → /forge → beads feed → complete.json
  │
  └── Main agent: "Done ✓ Chronicle running in background."
        │
        └── (user can start new work immediately)

Chronicle writes complete.json:
  beads_created: [ag-yyy, ag-zzz]   ← new issues in backlog

Next /crank or /rpi dispatch:
  └── Picks up ag-yyy, ag-zzz from bd ready
        │
        └── Implements them → repeats cycle
```
