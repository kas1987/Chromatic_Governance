# Agent Handoff: Auditor — Hermes Local-Worker Integration

> PDR-008 / HERMES-007. Adapted from the source packet
> `hermes_harness_pdr_package/12_HANDOFFS/agent_packets/auditor_hermes_packet.md`
> to this repository's actual layout. The Auditor **runtime** already exists — this
> document is the bounded *mission contract* it operates under for Hermes work.

## Agent Role

Auditor — governance-audit specialty. Reviews the Hermes local-worker integration for
governance compliance and evidence quality. Read-and-triage oriented; does **not** write
repository files.

## Runtime binding

This handoff binds to the existing runtime, it does **not** create new authority:

- `config/agents.yaml → auditor` (`status: active`,
  `branch_prefix: agent/auditor/`, `require_task_id_for_write: true`).
- Allowed profiles: `read_only`, `issue_triage`
  (see [`config/permission_profiles.yaml`](../../config/permission_profiles.yaml) —
  both profiles have `may_write_files: false`; `issue_triage` may comment / triage
  issues+PRs but writes no files and opens no PR).

The mission below must stay inside that profile envelope. The Auditor records findings
and triages; it does not patch.

## Mission

Review the Hermes local-worker integration from the Auditor (governance) perspective:
verify routing/governance changes are evidence-backed, in-scope, and that every mission
emits a valid eval receipt. Report findings; do not patch.

## Source Files (this repo)

- [`.01_PDRs/.03_In-Process/PDR-008-hermes-local-agent-harness.md`](../../../.01_PDRs/.03_In-Process/PDR-008-hermes-local-agent-harness.md)
  — the governing PDR (replaces the packet's `08_PDRS/PDR_HERMES_LOCAL_AGENT_WORKER.md`).
- [`config/hermes-model-capability.yaml`](../../config/hermes-model-capability.yaml)
  — model-capability map (replaces the packet's `*.example.yaml`).
- [`config/hermes-routing-patch.yaml`](../../config/hermes-routing-patch.yaml)
  — additive routing patch (replaces the packet's `*.example.yaml`).
- [`config/agents.yaml`](../../config/agents.yaml) and
  [`config/permission_profiles.yaml`](../../config/permission_profiles.yaml)
  — the governance policy this agent audits against.
- [`schemas/eval_receipt.schema.json`](../../schemas/eval_receipt.schema.json) and
  [`operations/eval-receipts.md`](../../operations/eval-receipts.md)
  — the receipt contract the Auditor checks each mission against (HERMES-005/006).

## Allowed Actions

- Read repo routing and governance files.
- Triage / comment on issues and PRs (`issue_triage` profile).
- Add tests (proposed via a patch agent — Auditor records the need; it does not write files).
- Add docs (same — recorded, not written, under this profile).
- Record validation results and emit an eval receipt.

## Blocked Actions

- Do not bypass governance gates (CI gate `hermes-gate.yml`, branch protection).
- Do not promote Hermes to C3/C4 default routing without benchmark evidence.
- Do not change git autonomy thresholds.
- Do not delete existing provider routes.
- Do not modify secrets or credentials.
- Do not write repository files or open PRs (profile-enforced: `may_write_files: false`).

## Acceptance Criteria

- Findings are grounded in repo files.
- Any recommended patch is described as scoped and reversible (for a patch agent to apply).
- Stop conditions are preserved.
- Output includes validation evidence or explicit blockers.
- The mission emits a valid eval receipt under
  `operations/receipts/<mission_id>.eval_receipt.json`.

## Stop Conditions

Stop and report (emit a receipt with `stop_condition_triggered: true`) if:

- The Hermes model tag is not installed.
- Existing routing tests fail before review.
- Provider-selector behavior differs from the expected architecture.
- A finding would require changing secrets, env files, or production autonomy policy
  (escalate to human; do not act).
- A finding requires file writes (hand to a patch agent; Auditor does not write).
