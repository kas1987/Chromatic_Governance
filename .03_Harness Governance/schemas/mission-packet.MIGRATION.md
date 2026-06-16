# Mission-Packet Schema — Canonicalization & Migration Note

**PDR:** PDR-008 · **Task:** HERMES-002 · **Date:** 2026-06-16
**Canonical:** `.03_Harness Governance/schemas/mission-packet.schema.json`
**Source diff:** `.01_PDRs/.03_In-Process/HERMES-001-schema-diff-report.md`

## Supersession

| Schema | Disposition |
|---|---|
| `chromatic_mission_packet_framework_v1/schemas/mission-packet.schema.json` | **Adopted as base** (M1–M4 framework). |
| `hermes_harness_pipeline_scaffold_v1/03_SCHEMAS/mission_packet.schema.json` | **Superseded.** Its fields are reconciled into the canonical schema (below). The extracted copy stays in `.99_Extracted/` as historical source only — do not author against it. |

There were only **two** mission-packet schemas, not three (PDR-008's premise corrected in HERMES-001). The PDR package's `hermes_evaluation_result.schema.json` is an eval-result contract, not a mission packet — out of scope here, handled in HERMES-005/006.

## Reconciliation deltas applied (scaffold → canonical)

| Scaffold field | Canonical home | Change |
|---|---|---|
| `mission_id`, `title`, `objective`, `complexity`, `privacy_class`, `steps`, `acceptance_criteria`, `stop_conditions` | same names | direct (no change) |
| `risk_class` | `risk_level` | rename (same enum: low/medium/high/critical) |
| `allowed_files`, `forbidden_files` | `scope.allowed_files`, `scope.forbidden_files` | nested under `scope` |
| `validation_commands` | `validation.required_checks` | nested + renamed |
| `expected_output` | `validation.success_definition` | mapped (free-text deliverable → success definition) |
| `preferred_model` | `preferred_model` (top-level, **added**) | new optional routing-hint field |
| `escalation_target` | `governance.escalation_target` (**added**) | new optional field, distinct from `reviewers[]` |

All scaffold fields have a home; none conflict in type/enum. The two additions (`preferred_model`, `governance.escalation_target`) are **optional** → backward-compatible, so `schema_version` stays `"1.0"`.

## Author migration checklist

When migrating a scaffold-format packet to canonical:
1. Add `schema_version: "1.0"`, `mission_level` (M1–M4), `owner_agent`, `status`, `allowed_actions`, `blocked_actions`, `governance` — these are required by canonical and absent from the flat scaffold.
2. Rename `risk_class` → `risk_level`.
3. Move `allowed_files`/`forbidden_files` into a `scope` object (also add `in_scope`/`out_of_scope`).
4. Move `validation_commands` → `validation.required_checks`; put `expected_output` text into `validation.success_definition`.
5. Keep `preferred_model` / `escalation_target` if present (now first-class).
6. Validate with `validate_packet.py` (from the framework artifact) against the canonical `$id`.
