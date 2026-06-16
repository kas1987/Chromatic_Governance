# HERMES-001 — Pre-flight Schema Diff Report

**Date:** 2026-06-16
**PDR:** PDR-008 (Hermes Local-Agent Harness)
**Task:** Extract source ZIPs, diff the `mission_packet` schemas, choose canonical.
**Stop condition:** Escalate if schemas are structurally incompatible.
**Verdict:** ✅ **Proceed** — schemas are reconcilable (not incompatible). Canonical = framework version. HERMES-001 does **not** escalate.

---

## 0. Correction to PDR-008's premise

PDR-008 (Background table + Risks) assumes **three** `mission_packet` schemas. Inventory of the extracted artifacts shows **two**:

| Artifact | Schema file | Kind |
|---|---|---|
| `chromatic_mission_packet_framework_v1` | `schemas/mission-packet.schema.json` | **mission packet** (M1–M4, canonical candidate) |
| `hermes_harness_pipeline_scaffold_v1` | `03_SCHEMAS/mission_packet.schema.json` | **mission packet** (flat) |
| `hermes_harness_pdr_package` | `schemas/hermes_evaluation_result.schema.json` | **eval result** — *not* a mission packet |

The PDR package contributes the **agent roster + an eval-result schema**, not a third mission-packet copy. The "three schemas silently diverge" risk (PDR-008 Risks row 1) is therefore overstated: there are two to collapse, plus two *eval* contracts to reconcile separately (§3).

---

## 1. Mission-packet schema diff (the two that matter)

### A. Framework `mission-packet.schema.json` (canonical candidate)
- `$id` set; `schema_version` const `"1.0"`; `mission_level` M1–M4; rich nested objects: `scope`, `validation`, `rollback`, `governance`.
- Roster-aware `owner_agent` enum (sentinel, auditor, chainbreaker, quartermaster, cartographer, financier, archivist, janitor, local_worker, human).
- Conditional `allOf`: M1 constrains complexity/risk; M4 requires `pdr_ref`+`rollback`+`supporting_docs` and forces `governance.level=maximum`, `approval_required=true`.
- `additionalProperties: false`. ~30 fields.

### B. Scaffold `mission_packet.schema.json`
- No `$id`, no `schema_version`, no `mission_level`, no conditionals. Flat (no nested objects). 15 fields. `additionalProperties: false`.

### Field reconciliation map

| Scaffold field | Home in framework | Mapping |
|---|---|---|
| `mission_id` | `mission_id` | direct (framework adds a `pattern`) |
| `title` | `title` | direct |
| `objective` | `objective` | direct |
| `complexity` | `complexity` | direct (same C1–C4 enum) |
| `privacy_class` | `privacy_class` | direct (same P0–P5 enum) |
| `risk_class` | `risk_level` | **rename**, same enum (low/medium/high/critical) |
| `allowed_files` | `scope.allowed_files` | **nest** |
| `forbidden_files` | `scope.forbidden_files` | **nest** |
| `steps` | `steps` | direct |
| `acceptance_criteria` | `acceptance_criteria` | direct |
| `validation_commands` | `validation.required_checks` | **nest + rename** |
| `stop_conditions` | `stop_conditions` | direct |
| `preferred_model` | — | **no 1:1 home** (see §2) |
| `expected_output` | ≈ `validation.success_definition` | semantic, not 1:1 (see §2) |
| `escalation_target` | ≈ `governance.reviewers` / `rollback.owner` | semantic, not 1:1 (see §2) |

**Every scaffold field is reachable** by direct map, rename, or nesting, except three that need an additive home. No field *contradicts* the framework (no conflicting types/enums). → **structurally compatible.**

---

## 2. Fields with no clean home — for HERMES-002 to resolve

HERMES-002's stop condition is "Stop if a Hermes field has no home." These three trip that gate but are **additively reconcilable** (add optional field or map), not blockers:

1. **`preferred_model`** — scaffold carries an explicit routing hint; framework selects tier implicitly via `mission_level`/`complexity`. *Recommendation:* add optional `preferred_model` (or `routing_hint`) to canonical; keep tier-derivation as the default when absent. Aligns with PDR-008 Decision 2 (mission level selects tier) while preserving an override.
2. **`expected_output`** — free-text deliverable description; framework spreads this across `acceptance_criteria` + `validation.success_definition` + `validation.evidence_required`. *Recommendation:* fold into `validation.success_definition`; no new field needed.
3. **`escalation_target`** — single escalation routing target; framework has `governance.reviewers[]`, `rollback.owner`, and free-text `stop_conditions`. *Recommendation:* add optional `escalation_target` to `governance` (a routing address differs in intent from a reviewer list).

Net: canonical schema = framework version **+ optional `preferred_model`** + optional `governance.escalation_target`; `expected_output` and `validation_commands` map into `validation.*`.

---

## 3. Eval contracts — two distinct schemas, NOT duplicates (revises PDR-008 Decision 3)

PDR-008 Decision 3 treats `eval_receipt.schema.json` and `hermes_evaluation_result.schema.json` as two copies of one contract to merge. They are **complementary, not duplicate**:

| | Scaffold `eval_receipt` | PDR-pkg `hermes_evaluation_result` |
|---|---|---|
| Purpose | **Operational** per-mission completion receipt | **Model-quality** eval-harness scorecard |
| Keys | mission_id, agent_model, status, files_changed, validation_results, scope_compliance, stop_condition_triggered | run_id, model_id, task_id, task_class, complexity, passed, scores{format,accuracy,completeness,path_grounding}, governance{critical_violation,hallucinated_paths,malformed_output}, latency_ms |
| Answers | "Did this mission complete within scope?" | "How good is this model at this task class?" |

**Recommendation for HERMES-005/006:** keep **both** — `eval_receipt` is the per-mission CI gate artifact (mission lacks passing receipt → fail); `hermes_evaluation_result` is the model-benchmark artifact for routing/capability decisions. Do *not* merge them. PDR-008 Decision 3 / Risks row 3 should be amended: there is one CI-gate receipt contract (`eval_receipt`) plus one separate model-eval contract.

---

## 4. Decision

- **Canonical mission-packet schema:** `chromatic_mission_packet_framework_v1/schemas/mission-packet.schema.json` (confirms PDR-008 Decision 1).
- **Reconciliation deltas** (hand to HERMES-002): rename `risk_class`→`risk_level`; nest `allowed_files`/`forbidden_files` under `scope`; map `validation_commands`→`validation.required_checks` and `expected_output`→`validation.success_definition`; add optional `preferred_model` and `governance.escalation_target`.
- **Eval layer:** keep two contracts (operational receipt + model scorecard); amend PDR-008 Decision 3 wording.
- **Escalation:** none. Schemas compatible.

## 5. Follow-up
- HERMES-002: apply the §4 deltas to a single canonical schema; record supersession of the scaffold copy; write migration note.
- Amend PDR-008 Background ("three schemas"→"two mission-packet + two eval"), Decision 3, and Risks row 1/3 to match this report.
- Do not start HERMES-003+ runtime work until HERMES-002 lands the canonical schema.
