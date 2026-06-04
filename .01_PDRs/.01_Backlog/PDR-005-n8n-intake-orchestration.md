# PDR-005: n8n Intake Orchestration for ZIP-to-Pipeline Automation

## Mission
Add n8n as an orchestration layer for ZIP intake so GPT-delivered artifacts are automatically ingested, reviewed, routed into the PDR pipeline, and escalated to human/agent execution only when gates pass.

## Why now
Current flow is strong but split between local watcher scripts and GitHub Actions triggers. n8n can provide unified event orchestration (local + repo + notifications) while preserving deterministic policy checks in Python and registry-driven governance.

## Scope
- Build a phased n8n integration plan for intake and orchestration only.
- Keep existing Python scanners as policy engines.
- Keep existing PDR pipeline states authoritative in PDR_REGISTRY.json.
- Do not replace core governance scripts in this phase.
- Use `.01_PDRs/AUTOMATION_WIRING_LOG.md` as the process register for follow-on automation targets across `n8n`, `LangGraph`, `LangSmith`, and related tooling.

## Out of scope
- Full LangGraph migration.
- Replacing GitHub Actions as CI governance gate.
- Auto-merging PRs.
- Multi-repo global orchestration.

## Architecture intent
Use n8n as the event router, not the policy engine:
1. Event sources
- Local ZIP drop events (watch folder)
- GitHub push / workflow events
- Manual webhook trigger

2. Deterministic checks (existing scripts)
- pdr_zip_intake.py for ZIP integrity + implementation signal
- pdr_sync.py for pipeline status consistency

3. State + audit
- SQLite + JSONL remain source for intake events
- PDR_REGISTRY.json remains source for PDR stage state

4. Dispatch and notifications
- n8n sends notifications for failures/escalations
- n8n opens/updates issue or PR comments when policy fails

## Phased plan

### Phase 1: Intake Event Bridge (Backlog -> Pre-flight ready)
- Create n8n workflow: ZIP dropped -> call local intake script -> persist result.
- Inputs:
  - ZIP filename
  - detected_pdr_id
  - review_result
  - implementation_status
- Outputs:
  - structured intake payload to JSONL/SQLite
  - optional webhook callback for dashboard status
- Success criteria:
  - New ZIP drop is processed in under 30s
  - Intake record appears in SQLite and JSONL
  - Failure paths produce notification

### Phase 2: Registry-Aware Routing
- n8n reads PDR_REGISTRY artifact_backlog + pdrs mapping.
- Route rules:
  - Backlog + pass -> keep backlog
  - Pre-flight + extracted_ready -> signal In-Process readiness
  - fail/warn -> create task for remediation
- Success criteria:
  - No status mutation without explicit policy gate
  - Routing decisions logged with reason and timestamp

### Phase 3: Human/Agent Handoff Triggering
- n8n emits mission packet trigger only when:
  - intake passed
  - required files extracted
  - status transition allowed by workflow
- Success criteria:
  - Handoff events are idempotent
  - Duplicate ZIP events do not duplicate dispatches

### Phase 4: Governance + Metrics Layer
- Add n8n metrics nodes:
  - intake latency
  - pass/fail rates
  - stale backlog artifacts
- Publish summary to periodic report endpoint.
- Success criteria:
  - Weekly summary generated automatically
  - Alert thresholds configurable in one place

## Risks
- Event duplication from local watcher + GitHub push.
- Drift between n8n flow logic and Python policy logic.
- Silent failures if n8n credentials/webhooks expire.

## Mitigations
- Idempotency key: zip_name + sha256 + pipeline_status.
- Keep policy decisions in Python, n8n only orchestrates.
- Healthcheck workflow in n8n with daily self-test ping.

## Dependencies
- Existing intake scripts stable and versioned.
- n8n runtime available (self-hosted or managed).
- Webhook secret and service credentials managed outside repo.

## Acceptance criteria
- A documented n8n workflow exists for ZIP intake orchestration.
- Intake event processing is automated for local ZIP drops.
- Registry-aware routing decisions are logged and auditable.
- No direct transition to In-Process without Pre-flight readiness.
- Existing GitHub Actions governance remains active.

## Exit criteria for this PDR
- PDR approved and promoted from Backlog to Pre-flight.
- n8n Phase 1 design reviewed and implementation tasked.

## Implementation artifacts
- Execution board: `.01_PDRs/AUTOMATION_EXECUTION_BOARD.md`
- n8n Phase 1 spec: `.01_PDRs/N8N_PHASE1_INTAKE_WORKFLOW_SPEC.md`
- LangGraph dispatcher spec: `.01_PDRs/LANGGRAPH_DISPATCHER_SPEC.md`
