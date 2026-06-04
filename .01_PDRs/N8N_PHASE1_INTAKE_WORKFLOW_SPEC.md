# n8n Phase 1 Intake Workflow Spec

Last updated: 2026-06-04

## Goal

Define a concrete n8n workflow for ZIP intake orchestration that calls existing Python policy scripts and records auditable outcomes.

## Scope

- Phase 1 only: event bridge and intake execution
- No direct stage mutation beyond existing policy scripts
- No replacement of GitHub Actions governance checks

## Workflow Name

`pdr-zip-intake-phase1`

## Implementation Asset

- Workflow JSON: `.03_Harness Governance/orchestration/n8n/pdr-zip-intake-phase1.workflow.json`
- Local bridge emitter: `.01_PDRs/pdr_zip_ingest.py` with `--webhook-url` and `--webhook-secret`

Example bridge command:

```powershell
python .01_PDRs/pdr_zip_ingest.py watch --webhook-url "http://localhost:5678/webhook/pdr-zip-intake-phase1" --webhook-secret "<shared-secret>"
```

## Trigger Paths

1. Local watcher webhook
- Source: `pdr_zip_ingest.py` (watch/import mode) sends webhook when ZIP is detected or imported.

2. Manual trigger
- Source: n8n webhook endpoint for operator test/replay.

3. Optional scheduler fallback
- Source: cron node every N minutes to detect missed events and re-run intake.

## Inputs

### Event payload

```json
{
  "event_id": "uuid",
  "event_type": "zip_detected|zip_imported|manual_replay",
  "zip_name": "repo-pdr-swarm-router.zip",
  "zip_rel_path": ".01_PDRs/.01_Backlog/repo-pdr-swarm-router.zip",
  "source": "local_watcher|manual|scheduler",
  "occurred_at": "2026-06-04T20:00:00Z"
}
```

### Idempotency key

`idempotency_key = zip_name + ":" + zip_rel_path`

Optional stronger key after intake result:

`idempotency_key_v2 = zip_name + ":" + sha256 + ":" + pipeline_status`

## Node Graph

1. `Webhook / Trigger`
- Validates required fields.

2. `Normalize Event`
- Normalizes path separators and ensures relative path rooted under `.01_PDRs`.

3. `Deduplicate Event`
- Checks idempotency store.
- If already processed recently, route to `No-op Result`.

4. `Execute Intake`
- Command:

```powershell
python .01_PDRs/pdr_zip_intake.py --zip-name "{{$json.zip_name}}"
```

- Working dir: repo root.
- Timeout: 120s.

5. `Parse Intake Output`
- Reads JSON result from stdout.
- Extracts counters and per-zip outcome if present.

6. `Refresh Registry`
- Command:

```powershell
python .01_PDRs/pdr_sync.py sync
```

- Ensures `artifact_backlog` is current after intake.

7. `Classify Outcome`
- Branches to:
  - `success_unique`
  - `success_duplicate_or_redundant`
  - `warning_possible_redundant`
  - `failure`

8. `Emit Notification`
- Sends structured status payload to configured channel.
- Minimal payload:

```json
{
  "workflow": "pdr-zip-intake-phase1",
  "event_id": "uuid",
  "zip_name": "repo-pdr-swarm-router.zip",
  "result": "success|warning|failure",
  "duplicate_status": "unique|duplicate|redundant|possible_redundant|unknown",
  "confidence": 0.1,
  "next_action": "none|review|manual_fix"
}
```

9. `Persist Run Telemetry`
- Persist run metadata in n8n execution data and optional external trace sink.

## Failure Handling

- Intake command non-zero exit:
  - mark event as `failure`
  - emit notification with stderr summary
  - do not attempt stage mutation

- Registry sync non-zero exit:
  - mark event as `warning`
  - include remediation action: rerun `pdr_sync.py sync`

- Parse error / invalid JSON:
  - capture raw stdout/stderr
  - mark as `failure_parse`
  - route to manual triage

## Security and Safety

- Webhook endpoint protected by shared secret header.
- Only relative paths under `.01_PDRs` accepted.
- No shell interpolation from untrusted input beyond escaped zip name.
- Workflow credentials stored in n8n credential vault, never in repo.

## SLO Targets

- Event-to-intake completion: <= 30s median
- Error notification latency: <= 10s after failure
- Duplicate processing rate: 0 duplicate dispatches per idempotency key window

## Acceptance Checks

1. New ZIP in backlog triggers workflow and successful intake run.
2. Intake writes auditable state (SQLite/JSONL via existing script behavior).
3. Registry sync refreshes artifact backlog without manual intervention.
4. Duplicate/redundant outcomes emit differentiated notifications.
5. Replay of same event does not re-run mutating path within idempotency window.

## Implementation Notes

- Keep policy authority in Python scripts (`pdr_zip_intake.py`, `pdr_sync.py`).
- n8n orchestrates event routing, retries, and notifications only.
- Phase 2 can add status-routing logic once this baseline is stable.
