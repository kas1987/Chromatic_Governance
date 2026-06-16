# Agent Handoff: Sentinel — Hermes Local-Worker Integration

> PDR-008 / HERMES-007. Adapted from the source packet
> `hermes_harness_pdr_package/12_HANDOFFS/agent_packets/sentinel_hermes_packet.md`
> to this repository's actual layout. The Sentinel **runtime** already exists — this
> document is the bounded *mission contract* it operates under for Hermes work.

## Agent Role

Sentinel — guard / security specialty. Reviews and patches the Hermes local-worker
integration from a guard perspective: scope, reversibility, and gate-compliance.

## Runtime binding

This handoff binds to the existing runtime, it does **not** create new authority:

- `config/agents.yaml → code_sentinel` (`status: active`,
  `branch_prefix: agent/codesentinel/`, `require_pull_request: true`,
  `deny_direct_main_push: true`, `require_task_id_for_write: true`).
- Allowed profiles: `read_only`, `patch_standard`
  (see [`config/permission_profiles.yaml`](../../config/permission_profiles.yaml) —
  `patch_standard` is PR-only, denies direct `Main` push, requires a task id).

The mission below must stay inside that profile envelope. Anything requiring authority
beyond `patch_standard` is out of scope and triggers a stop condition.

## Mission

Implement or review the Hermes local-worker integration from the Sentinel (guard)
perspective: confirm routing/governance changes are scoped, reversible, and do not
weaken any governance gate.

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
- Add docs.
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
