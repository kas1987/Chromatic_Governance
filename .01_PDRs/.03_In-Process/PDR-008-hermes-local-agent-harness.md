# PDR-008: Hermes Local-Agent Harness

## Status
Draft — proposed 2026-06-16. Folds three backlog artifacts into one initiative; awaiting pre-flight + scheduling.

## Date
2026-06-16

## Owner
Kris Sayresmith / Poly-Chromatic

## Reference
- `SWOT.md` (ecosystem analysis)
- Router work: Featherless T3 tiers (Kimi-K2, Hermes-3-70B) already wired in `~/.claude` (see router activation + Kimi/Hermes routing memory)
- PDR-004 (review intake), PDR-005 (n8n orchestration), PDR-006 (artifact taxonomy)

---

## Executive Summary

Three independently-dropped backlog artifacts describe one coherent system: a **local-agent worker harness** ("Hermes") that runs a fixed roster of bounded agents on local / Featherless-hosted models, governed by mission-packet schemas and verified by eval receipts. Held separately they read as three half-specs; folded together they are a single deliverable with a schema layer, a routing layer, an agent roster, and an evaluation gate. This PDR promotes all three out of the backlog, states what each contributes, and defines the work queue to stand the harness up incrementally on top of the router tiers that already exist.

---

## Background — the three source artifacts

| Artifact (backlog ID) | Role in the initiative | Key contents |
|---|---|---|
| `ART-CHROMATIC_MISSION_PACKET_FRAMEWORK_V1` | **Schema + governance layer** | M1–M4 mission-complexity schemas; `mission-packet`, `pdr`, `governance-register`, `supporting-documents` JSON schemas; templates (PDR, risk register, dispatch board, evidence map); governance gates; PDR-requirements-by-level; `validate_packet.py`; CI gate plan; worked examples; seed work items |
| `ART-HERMES_HARNESS_PIPELINE_SCAFFOLD_V1` | **Pipeline scaffold** | `PDR_HERMES_LOCAL_AGENT_PIPELINE.md`; `MODEL_AUTHORITY_POLICY.md` + governance checklist; `mission_packet` / `eval_receipt` schemas; routing patch plan + `MODEL_TIER_MAP.md`; 3 agent missions (capability registry, routing, eval receipts); eval plan + sample receipt; CI gate plan; operator guide; seed queue |
| `ART-HERMES_HARNESS_PDR_PACKAGE` | **Agent roster + deployment** | `PDR_HERMES_LOCAL_AGENT_WORKER.md`; 5 agent handoff packets — **Sentinel, Auditor, Cartographer, Archivist, Quartermaster**; implementation plan; deployment configs (`hermes-model-capability.yaml`, `hermes-routing-patch.yaml`); routing policy; evaluation protocol; smoke-test plan; `hermes_evaluation_result.schema.json` |

The three overlap deliberately along a shared seam — not a conflict. **Reconciled by HERMES-001 (2026-06-16):** there are **two** `mission_packet` schemas, not three — the framework's M1–M4 version and the pipeline scaffold's flat copy. The PDR package does **not** carry a third mission-packet schema; its only schema is `hermes_evaluation_result.schema.json`, an eval-result contract. Separately, the two *eval* schemas (`eval_receipt` and `hermes_evaluation_result`) are **distinct contracts** — an operational per-mission receipt and a model-quality scorecard — not duplicate copies. See `.01_PDRs/.03_In-Process/HERMES-001-schema-diff-report.md`.

---

## Problem Statement

- The router already exposes local (Ollama T0) and Featherless (Kimi/Hermes T1–T3) tiers, but there is **no worker harness** that turns a queued work-item into a governed mission packet, dispatches it to the right tier, and records a verifiable eval receipt.
- Three artifacts describe that harness in pieces. Left in the backlog they will drift, duplicate schemas, and never ship.
- There is no single mission-packet schema of record. The framework artifact has the most general one (M1–M4); the two Hermes artifacts each carry a narrower copy.
- The five named agents (Sentinel/Auditor/Cartographer/Archivist/Quartermaster) have handoff packets but no runtime, no capability registry, and no routing entry.

---

## Goals

1. Promote the three artifacts out of `artifact_backlog` and treat them as one initiative of record.
2. Establish **one** canonical mission-packet schema (the M1–M4 framework version) and reconcile the two Hermes copies to it.
3. Stand up the Hermes capability registry + routing patch against the existing model-tier map.
4. Define the eval-receipt contract and a CI gate that rejects a mission without a passing receipt.
5. Land the five agent missions as bounded, individually-shippable units.

---

## Non-Goals

- Does not replace the existing subagent router or the In-Review pipeline (mc-685) — Hermes is a worker tier beneath them.
- Does not commit to running all five agents at once; the roster lands incrementally.
- Does not bake any Featherless key into config (key stays in `~/.claude/secrets/`, never committed).
- Does not redefine the broker permission model (PDR-002 governance bridges remain authoritative).

---

## Design Decisions

### Decision 1 — One schema of record
Adopt `chromatic_mission_packet_framework_v1/schemas/mission-packet.schema.json` (the M1–M4 version) as canonical. The two Hermes `mission_packet.schema.json` copies are reconciled to it (or referenced, not re-declared). Rationale: a single schema is the seam the three artifacts join on; duplicate schemas are the most likely drift source.

### Decision 2 — Hermes is a worker tier, governed by mission level
Mission complexity (M1 basic → M4 atomic) selects both the required PDR rigor and the model tier. Low-complexity (M1/M2) routes to local/Featherless tiers; high-complexity (M3/M4) escalates. **Amended by HERMES-003 (2026-06-16):** the live router (`~/.claude/governance/multi-router-matrix.yaml` + `provider-tiers.json`) is **authoritative** over the scaffold `MODEL_TIER_MAP.md`, which does not match it (live T0 Ollama llama3.2:3b / T1 Featherless Hermes-3 / T2 OpenAI gpt-4o-mini / T3 Gemini / T4 Claude). For the Claude-Agent cloud plane, the "capability registry" of record remains the matrix's `when:` clauses, **not** a new file. **Option B was chosen (2026-06-16):** a separate local-worker plane (Ollama/Gen) now has its own registry of record — `.03_Harness Governance/config/hermes-model-capability.yaml` — covering the locally-pulled `hermes3:8b`. The two planes are kept distinct; this file does not redefine any cloud tier. See `.01_PDRs/.03_In-Process/HERMES-003-tier-reconciliation-finding.md`.

### Decision 3 — Eval receipts are mandatory and CI-gated
**Amended by HERMES-001:** the two eval schemas are *not* duplicates and are **both retained**. Every completed mission emits an operational **`eval_receipt`** (mission_id, status, files_changed, scope_compliance, stop_condition_triggered) — this is the CI-gate artifact: a mission lacking a passing receipt fails the gate. Separately, **`hermes_evaluation_result`** is a model-quality scorecard (scores 0–1, hallucinated-path counts) used for routing/capability decisions, not per-mission gating. The CI gate plan becomes one workflow keyed on `eval_receipt`; the scorecard feeds the capability registry (HERMES-003).

### Decision 4 — Incremental agent roster
Land the five agents in dependency order, each behind its own mission: capability registry first (no agent runs without it), then routing, then eval receipts, then the individual agent packets. Sentinel (guard/security) lands before agents with write authority.

---

## Work Queue

| ID | Pri | Status | Task | Output | Stop condition |
|---|---:|---|---|---|---|
| HERMES-001 | P0 | ✅ done | Pre-flight: extract ZIPs to `.99_Extracted/`, diff the `mission_packet` schemas | Diff report + chosen canonical (framework) — done 2026-06-16, no escalation | Stop if schemas are structurally incompatible (escalate) |
| HERMES-002 | P0 | ✅ done | Reconcile to one canonical `mission-packet.schema.json`; record supersessions | `.03_Harness Governance/schemas/mission-packet.schema.json` + `.MIGRATION.md` — done 2026-06-16 | Stop if a Hermes field has no home in the M1–M4 schema |
| HERMES-003 | P1 | ✅ done | Build Hermes capability registry (mission-001) | **Stop fired then resolved (2026-06-16):** scaffold `MODEL_TIER_MAP` ≠ live router → reconciliation finding + escalation → `.01_PDRs/.03_In-Process/HERMES-003-tier-reconciliation-finding.md`. Owner chose **Option B**: pulled local `hermes3:8b` into Ollama (4.7 GB, 8B, tools-capable, smoke-tested) + authored local-worker capability registry of record → `.03_Harness Governance/config/hermes-model-capability.yaml`. Live-matrix wiring deferred to HERMES-004 | Stop if router tier names don't match the tier map ← tripped, escalated, resolved (option B) |
| HERMES-004 | P1 | ◑ patch + proof built; live write human-gated | Apply Hermes routing patch (mission-002) against live tiers | Routing patch + dry-run proof — done 2026-06-16: additive fragment + spec + machine proof in `.03_Harness Governance/config/hermes-routing-patch.{fragment.json,yaml,proof.txt}`. Proof: 0 key collisions, 10/10 existing Gen intents byte-identical after merge → adds only `instruction-follow` + `agentic-tool-use` (hermes3:8b primary). Live write to `C:\.04_Prism\gen\src\routes\routing-matrix.json` (separate Prism repo) held at human gate | Stop if patch would alter non-Hermes routing — **did NOT fire** (proven additive) |
| HERMES-005 | P1 | ✅ done | Implement eval-receipt emission + `validate_packet.py` (mission-003) | Receipts validated against schema — done 2026-06-16: canonical `.03_Harness Governance/schemas/eval_receipt.schema.json` (7 required fields kept byte-faithful to scaffold + additive optional `pr_ref`/`created_at`), importable `scripts/validate_packet.py` (deps `jsonschema`+`pyyaml`, both pinned in `requirements-dev.txt`), valid+invalid fixtures, `scripts/tests/test_eval_receipt.py` (10 tests green: valid passes / invalid fails / CLI rc 0·1·2), and operator guide `operations/eval-receipts.md` (when to emit + how to attach to a PR). | Stop if validator has undocumented deps — **did NOT fire** (deps documented in-script + pinned) |
| HERMES-006 | P2 | ✅ done | Merge the two CI gate plans into one workflow | `.github/workflows/hermes-gate.yml` — done 2026-06-16: single gate keyed on `eval_receipt`, scoped to `.03_Harness Governance/**`. Three jobs: **schema-validate** (validates every `operations/receipts/*.eval_receipt.json` against the schema; rejects invalid; advisory-pass when none present), **yaml-parse** (all 6 `config/*.yaml` parse), **unit-tests** (eval-receipt contract suite, 10 green). Folds framework's phased plan + scaffold's job table. Also: `jsonschema>=4.18` added to `requirements-dev.txt` (validator dep now reproducible in CI); dogfood receipt at `operations/receipts/hermes-006-ci-gate.eval_receipt.json`. **Phase-3 "reject a mission PR lacking a receipt" is the documented follow-up.** | Stop if it conflicts with skill-governance CI — **did NOT fire** (skill-governance is `.02_Plugins/**`-scoped; no path/job/concurrency overlap) |
| HERMES-007 | P2 | ✅ done | Land Sentinel + Auditor agent packets (read/guard first) | Two Hermes mission-packet handoffs — done 2026-06-16: `.03_Harness Governance/handoffs/hermes/{SENTINEL,AUDITOR}_HANDOFF_HERMES_INTEGRATION.md`. Both adapted from the source packets to this repo's layout (Source Files remapped to PDR-008 + `config/hermes-*.yaml`; blocked-actions + stop-conditions carried verbatim) and **bound to the runtimes that already exist** in `config/agents.yaml` (`code_sentinel` → `read_only`/`patch_standard`, PR-only + `deny_direct_main_push`; `auditor` → `read_only`/`issue_triage`, `may_write_files:false`). Docs-only: no config-capability or authority change. Dogfood receipt at `operations/receipts/hermes-007-sentinel-auditor.eval_receipt.json`. | Stop if Sentinel guard policy is ambiguous — **did NOT fire** (guard policy fully specified in `agents.yaml` + `permission_profiles.yaml`; runtimes pre-existing) |
| HERMES-008 | P3 | ✅ done | Land Cartographer / Archivist / Quartermaster | Three Hermes mission-packet handoffs — done 2026-06-16: `.03_Harness Governance/handoffs/hermes/{CARTOGRAPHER,ARCHIVIST,QUARTERMASTER}_HANDOFF_HERMES_INTEGRATION.md`, adapted from the source packets (Source Files remapped to PDR-008 + `config/hermes-*.yaml`; blocked-actions + stop-conditions verbatim; role-specific Mission/Role per specialty). Owner chose **docs + register runtimes**: the three runtimes are now registered in `config/agents.yaml` (`status: inactive`, `read_only`/`patch_standard`, PR-only + `deny_direct_main_push`) — mirrors the existing `code_sentinel` bounded-write runtime; **no new permission profile, no authority beyond `patch_standard`**. Dogfood receipt at `operations/receipts/hermes-008-cartographer-archivist-quartermaster.eval_receipt.json`. Runtime activation + an end-to-end run remain follow-ups. | Stop if any needs write authority beyond broker policy — **did NOT fire** (all three packets fit `patch_standard`; runtimes registered inactive within broker policy) |

---

## Risks

| Risk | Severity | Mitigation |
|---|---:|---|
| ~~Three~~ Two `mission_packet` schemas silently diverge | High | ✅ Resolved: HERMES-001/002 collapsed to one canonical schema (2026-06-16) before any runtime work |
| Hermes routing patch perturbs the live subagent router | High | Dry-run + diff-only proof in HERMES-004; patch is additive |
| Two CI gate plans contradict each other or skill-governance CI | Medium | HERMES-006 merges them into one workflow |
| Featherless key handling | Medium | Key stays in `~/.claude/secrets/`; never committed; secret scans active |
| Agent with write authority exceeds broker profile | Medium | Sentinel-first ordering; agents mapped to `plugin-access-policy.md` profiles |
| Initiative stalls again in backlog | Low | This PDR + registry promotion make it tracked work, not a loose ZIP |

---

## Acceptance Criteria

This PDR is complete when:

- [ ] All three artifacts are extracted and their `artifact_backlog` status is `Promoted` (folded into PDR-008)
- [ ] One canonical `mission-packet.schema.json` exists; the two Hermes copies reference or are reconciled to it
- [ ] Hermes capability registry is wired to the live router tiers and validated
- [x] An eval receipt is emitted for a sample mission and passes `validate_packet.py` (HERMES-005: valid fixture + 10 green tests)
- [x] A single Hermes CI gate validates eval receipts and rejects invalid ones (HERMES-006: `hermes-gate.yml`, 3 jobs). _Follow-up: Phase-3 enforcement that a mission PR must include a receipt._
- [ ] Sentinel and Auditor agents run a bounded mission end-to-end _(HERMES-007 landed both mission-packet handoffs bound to the existing `code_sentinel`/`auditor` runtimes — `handoffs/hermes/`; an actual end-to-end run against the live `hermes3:8b` worker is the follow-up.)_
- [ ] PDR-008 is referenced from the PDR registry and (if it ships) `AGENT_GUIDE.md`

---

## Next action

Run HERMES-001 (pre-flight extraction + schema diff) as a single scoped session. Do not begin runtime work (HERMES-003+) until the canonical schema is chosen in HERMES-002.
