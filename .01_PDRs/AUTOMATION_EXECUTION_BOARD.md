# Automation Execution Board

Last updated: 2026-06-04

## Objective

Translate automation planning into executable phases with ownership, priorities, dependencies, and verifiable acceptance checks.

## Status Legend

- `not_started`: Work has not started
- `in_progress`: Actively being implemented
- `blocked`: Waiting on dependency or decision
- `done`: Acceptance checks passed

## Phase Board

| Work ID | Process ID | Work item | Owner | Priority | Status | Depends on | Acceptance checks |
|---|---|---|---|---|---|---|---|
| `AUTO-EXE-001` | `PDR-AUTO-001` | Implement n8n trigger for local ZIP intake events | Kas/Claude | P0 | in_progress | none | ZIP event reaches orchestration within 30s; failed trigger emits alert |
| `AUTO-EXE-002` | `PDR-AUTO-002` | Add n8n-assisted import flow from Downloads to Backlog | Kas/Claude | P1 | not_started | `AUTO-EXE-001` | Import supports copy/move; idempotency key prevents duplicate enqueue |
| `AUTO-EXE-003` | `PDR-AUTO-003` | Wrap `pdr_zip_intake.py` in n8n execution node | Kas/Claude | P0 | in_progress | `AUTO-EXE-001` | Intake run result is persisted in SQLite and JSONL; run metadata includes duration and outcome |
| `AUTO-EXE-004` | `PDR-AUTO-004` | Publish duplicate/redundancy outcomes to operator channel | Kas/Claude | P1 | not_started | `AUTO-EXE-003` | `duplicate_status`, confidence, and evidence sent in notification payload |
| `AUTO-EXE-005` | `PDR-AUTO-005` | Trigger `pdr_sync.py sync` after successful intake/import | Kas/Claude | P0 | in_progress | `AUTO-EXE-003` | Registry contains all current backlog ZIP artifacts after each run |
| `AUTO-EXE-006` | `PDR-AUTO-006` | Orchestrate Backlog -> Pre-flight extraction step | Kas/Claude | P1 | not_started | `AUTO-EXE-005` | Extraction success/failure captured; retry is safe and does not corrupt extracted bundle |
| `AUTO-EXE-007` | `PDR-AUTO-007` | Add readiness guard before In-Process transitions | Kas/Claude | P0 | not_started | `AUTO-EXE-006` | Transition blocked when extracted_path missing/empty; block reason visible in status output |
| `AUTO-EXE-008` | `PDR-AUTO-008` | Define approval checkpoint for stage mutations | Kas/Claude | P1 | not_started | `AUTO-EXE-007` | Stage mutation requires explicit approved event; mutation log includes actor/reason/timestamp |
| `AUTO-EXE-009` | `PDR-AUTO-009` | Build scheduled pipeline digest job | Kas/Claude | P2 | not_started | `AUTO-EXE-005` | Daily or weekly digest published with counts by state and blocked items |
| `AUTO-EXE-010` | `PDR-AUTO-010` | Aggregate repo-side intake signals in central flow | Kas/Claude | P1 | not_started | `AUTO-EXE-003` | GitHub Action outcomes are ingested into centralized event stream |
| `AUTO-EXE-011` | `PDR-AUTO-011` | Centralize review-intake normalization stream | Kas/Claude | P1 | not_started | `AUTO-EXE-010` | PR review events normalized with stable schema and replay-safe ids |
| `AUTO-EXE-012` | `PDR-AUTO-012` | Build queue upsert and confidence re-score node | Kas/Claude | P1 | not_started | `AUTO-EXE-011` | Queue updates are atomic; low-confidence findings route to manual review lane |
| `AUTO-EXE-013` | `PDR-AUTO-013` | Surface branch lock state in dispatcher control plane | Kas/Claude | P0 | in_progress | `AUTO-EXE-012` | No concurrent mutating agent writes on same PR branch |
| `AUTO-EXE-014` | `PDR-AUTO-014` | Implement mission packet generation from ready queue | Kas/Claude | P1 | in_progress | `AUTO-EXE-013` | Mission packet includes scope, constraints, validation targets, rollback policy |
| `AUTO-EXE-015` | `PDR-AUTO-015` | Implement patch/validate/resolve graph loop | Kas/Claude | P0 | not_started | `AUTO-EXE-014` | Validation fan-out executes; resolution comment created only after checks pass |
| `AUTO-EXE-016` | `PDR-AUTO-016` | Add weekly learning and trend evaluation pipeline | Kas/Claude | P2 | not_started | `AUTO-EXE-015` | Repeated-failure clusters emitted; weekly trend report persisted |
| `AUTO-EXE-017` | `PDR-AUTO-017` | Build centralized escalation routing | Kas/Claude | P1 | in_progress | `AUTO-EXE-011` | Failures, blocked states, and manual gates route to designated channel with SLA label |
| `AUTO-EXE-018` | `PDR-AUTO-018` | Stand up end-to-end intake-to-execution control graph | Kas/Claude | P0 | not_started | `AUTO-EXE-013`, `AUTO-EXE-015` | Intake-to-resolution trace is end-to-end observable and replay-safe |

## Current Sprint Slice (Recommended)

| Sprint focus | Included work IDs | Target outcome |
|---|---|---|
| `Sprint-A` Event bridge baseline | `AUTO-EXE-001`, `AUTO-EXE-003`, `AUTO-EXE-005`, `AUTO-EXE-017` | Reliable intake execution with notifications and fresh registry state |
| `Sprint-B` Stage-safe routing | `AUTO-EXE-006`, `AUTO-EXE-007`, `AUTO-EXE-008` | Governed transition flow with explicit guardrails |
| `Sprint-C` Review-intake dispatch | `AUTO-EXE-010`, `AUTO-EXE-011`, `AUTO-EXE-012`, `AUTO-EXE-013` | Stable queueing and lock-safe multi-agent readiness |

## Governance Gates

- `Gate-1`: No orchestration step mutates PDR stage without allowed transition in `PDR_REGISTRY.json`.
- `Gate-2`: Duplicate/redundancy decisions remain evidence-backed and human-overrideable.
- `Gate-3`: Any mutating agent path must acquire branch lock before write operations.
- `Gate-4`: Every orchestration run emits structured telemetry suitable for audit and replay.

## Traceability

- Planning source: `AUTOMATION_WIRING_LOG.md`
- n8n implementation spec: `N8N_PHASE1_INTAKE_WORKFLOW_SPEC.md`
- Dispatcher architecture spec: `LANGGRAPH_DISPATCHER_SPEC.md`
- n8n workflow asset: `.03_Harness Governance/orchestration/n8n/pdr-zip-intake-phase1.workflow.json`
- LangGraph scaffold asset: `.03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py`
