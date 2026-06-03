# RPI Examples

## Full Lifecycle

**User says:** `/rpi "add user authentication"`

1. `/discovery "add user authentication"` — brainstorm, research, plan, pre-mortem -> epic `ag-5k2`
2. `/crank ag-5k2` — implement all issues
3. `/validation ag-5k2` — vibe, post-mortem, retro, forge

## Resume from Implementation

**User says:** `/rpi --from=implementation ag-5k2`

1. Skips discovery
2. `/crank ag-5k2`
3. `/validation ag-5k2`

## Interactive Discovery

**User says:** `/rpi --interactive "refactor payment module"`

1. `/discovery "refactor payment module" --interactive --complexity=full` — human gates in research + plan
2. `/crank <epic-id>` — autonomous
3. `/validation <epic-id>` — autonomous

## Chronicle-Enabled Lifecycle (default since chronicle-agent.md)

**User says:** `/rpi "add rate limiting to API"`

RPI runs fully autonomously; Chronicle handles post-mortem asynchronously in background.

```
Step 0  mkdir -p .agents/chronicle; clear stale complete.json + events.jsonl
        ↳ Check prior complete.json (see "Prior Chronicle Context" below)

Phase 1  /discovery → epic ag-7q3
         RPI writes: {"event":"discovery_complete","epic_id":"ag-7q3",...} → events.jsonl

Phase 2  /crank ag-7q3 (waves)
         RPI writes: wave_complete × N, phase2_complete → events.jsonl

Phase 3  /vibe only (RPI runs vibe, NOT full /validation)
         RPI writes: {"event":"vibe_complete","verdict":"PASS",...} → events.jsonl
         RPI assembles events context → spawns Chronicle (run_in_background=True)
         RPI reports: "Done ✓  Chronicle handling post-mortem in background." → exits

Chronicle (background, model=sonnet)
  Phase A  /post-mortem ag-7q3
  Phase B  /retro
  Phase C  ao forge transcript (flywheel)
  Phase D  beads feeding → bd create × 3  (ag-8a1, ag-8a2, ag-8a3)
  Phase E  write complete.json:
           {
             "status": "done",
             "epic_id": "ag-7q3",
             "post_mortem_verdict": "PASS",
             "vibe_verdict": "PASS",
             "items_created": 3,
             "beads_created": ["ag-8a1","ag-8a2","ag-8a3"],
             "flywheel_fired": true,
             "timestamp": "2026-05-27T14:22:00Z",
             "error": null
           }
```

**Async report format** (what the user sees at the end of the main RPI run):

```
=== RPI Complete ===
Goal:     add rate limiting to API
Epic:     ag-7q3
Phases:   discovery ✓  crank ✓  vibe ✓
Vibe:     PASS

Chronicle spawned in background — post-mortem, retro, forge, beads feeding.
Next /rpi run will report bead count from complete.json.
```

### Prior Chronicle Context

When Step 0 detects a `complete.json` from a prior run **before** clearing it, RPI prepends:

```
Prior Chronicle (ag-7q3): 3 beads created [ag-8a1, ag-8a2, ag-8a3] — now in backlog.
```

This surfaces prior Chronicle output as context for the new run without blocking execution.
