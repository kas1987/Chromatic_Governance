# Agent Handoff: Quartermaster — Hermes Local-Worker Integration

> PDR-008 / HERMES-008. Adapted from the source packet
> `hermes_harness_pdr_package/12_HANDOFFS/agent_packets/quartermaster_hermes_packet.md`
> to this repository's actual layout. The Quartermaster **runtime** is registered by
> HERMES-008 (`config/agents.yaml`, `status: inactive`) — this document is the bounded
> *mission contract* it operates under for Hermes work.

## Agent Role

Quartermaster — resource / dependency specialty. Tracks the supplies the Hermes
integration depends on: the local `hermes3:8b` model tag, validator dependencies in
`requirements-dev.txt`, and capability-tier inventory — and keeps them reproducible.
Proposes dependency/inventory patches.

## Runtime binding

This handoff binds to the runtime registered by HERMES-008; it grants **no authority
beyond the broker profile**:

- `config/agents.yaml → quartermaster` (`status: inactive`,
  `branch_prefix: agent/quartermaster/`, `require_pull_request: true`,
  `deny_direct_main_push: true`, `require_task_id_for_write: true`).
- Allowed profiles: `read_only`, `patch_standard`
  (see [`config/permission_profiles.yaml`](../../config/permission_profiles.yaml) —
  `patch_standard` is PR-only, denies direct `Main` push, requires a task id).

The mission below must stay inside that profile envelope. Anything requiring authority
beyond `patch_standard` is out of scope and triggers a stop condition.

## Mission

Keep the Hermes integration's dependencies reproducible: confirm the `hermes3:8b` model
tag is the inventory of record, that validator deps are pinned in `requirements-dev.txt`,
and that the capability registry reflects what is actually installed — without mutating
routing behavior or touching secrets.

## Source Files (this repo)

- [`.01_PDRs/.03_In-Process/PDR-008-hermes-local-agent-harness.md`](../../../.01_PDRs/.03_In-Process/PDR-008-hermes-local-agent-harness.md)
  — the governing PDR (replaces the packet's `08_PDRS/PDR_HERMES_LOCAL_AGENT_WORKER.md`).
- [`config/hermes-model-capability.yaml`](../../config/hermes-model-capability.yaml)
  — model-capability map (replaces the packet's `*.example.yaml`).
- [`config/hermes-routing-patch.yaml`](../../config/hermes-routing-patch.yaml)
  — additive routing patch (replaces the packet's `*.example.yaml`).
- [`config/agents.yaml`](../../config/agents.yaml) and
  [`config/permission_profiles.yaml`](../../config/permission_profiles.yaml)
  — the guard policy this agent is bound by.
- [`schemas/eval_receipt.schema.json`](../../schemas/eval_receipt.schema.json) and
  [`operations/eval-receipts.md`](../../operations/eval-receipts.md)
  — the receipt this mission must emit (HERMES-005/006).

## Allowed Actions

- Read repo routing and governance files.
- Propose bounded, reversible patches (within the `patch_standard` profile envelope).
- Add tests.
- Add docs (dependency / inventory notes).
- Record validation results and emit an eval receipt.

## Blocked Actions

- Do not bypass governance gates (CI gate `hermes-gate.yml`, branch protection).
- Do not promote Hermes to C3/C4 default routing without benchmark evidence.
- Do not change git autonomy thresholds.
- Do not delete existing provider routes.
- Do not modify secrets or credentials.
- Do not push directly to `Main` (profile-enforced; PR-only).

## Acceptance Criteria

- Findings are grounded in repo files.
- Any proposed patch is scoped and reversible.
- Stop conditions are preserved.
- Output includes validation evidence or explicit blockers.
- The mission emits a valid eval receipt under
  `operations/receipts/<mission_id>.eval_receipt.json`.

## Stop Conditions

Stop and report (emit a receipt with `stop_condition_triggered: true`) if:

- The Hermes model tag is not installed.
- Existing routing tests fail before changes.
- Provider-selector behavior differs from the expected architecture.
- Any patch requires changing secrets, env files, or production autonomy policy.
- A fix requires authority beyond the `patch_standard` profile.
