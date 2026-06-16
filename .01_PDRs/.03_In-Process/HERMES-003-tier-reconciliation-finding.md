# HERMES-003 — Capability-Registry Pre-Wire Finding (STOP / escalate)

**Date:** 2026-06-16
**PDR:** PDR-008 (Hermes Local-Agent Harness)
**Task:** Build the Hermes capability registry (`hermes-model-capability.yaml`) and wire it to the live router.
**Stop condition (from PDR-008 work queue):** *Stop if router tier names don't match the tier map.*
**Verdict:** ⏸ **STOP — escalate for a routing-plane decision.** The scaffold tier map and the capability example **contradict the live router**. Wiring `hermes3:8b` as written would inject a model the live system runs nowhere. No live router config was modified. This finding is read-only.

---

## 0. What HERMES-003 was supposed to do

Source artifacts (extracted, historical):
- `hermes_harness_pipeline_scaffold_v1/05_AGENT_MISSIONS/mission-001-add-hermes-capability-registry.md` — add `hermes3:8b` to `model-capabilities.yaml`.
- `hermes_harness_pipeline_scaffold_v1/04_ROUTING/MODEL_TIER_MAP.md` — the tier map the registry is supposed to agree with.
- `hermes_harness_pdr_package/09_DEPLOYMENT/config/routing/hermes-model-capability.example.yaml` — the registry entry shape.

The PDR-008 stop condition requires that, before authoring, the **scaffold tier map agree with the live router tiers**. It does not.

---

## 1. Live router (authoritative) vs scaffold tier map

**Live sources (read-only):**
`~/.claude/governance/multi-router-matrix.yaml` (`claude_agent_tiers`) and `~/.claude/config/provider-tiers.json`.

| Tier | LIVE Claude-Code Agent router | SCAFFOLD `MODEL_TIER_MAP.md` | Match? |
|---|---|---|---|
| T0 | `ollama` **llama3.2:3b** — nano; zero-judgment formatting | "CI / tests / schemas — validation authority" | ❌ different *kind* (a model vs a concept) |
| T1 | `featherless` **NousResearch/Hermes-3-Llama-3.1-8B** — micro; scaffold/boilerplate | **Hermes** (local agentic) + **Llama/Gemma** (local support) | ⚠️ Hermes present but **cloud-hosted, not local** |
| T2 | `openai` **gpt-4o-mini** — small; review | **Qwen Coder** (local coder) | ❌ entirely different model/provider |
| T3 | `gemini` **gemini-2.5-flash** — medium; debug/integration | *(absent)* | ❌ no scaffold equivalent |
| T4 | `claude` **claude-sonnet-4-6** — large; architect | **Claude/GPT/Gemini Pro** — architect | ✅ aligns on Claude |

Only T4 aligns. T0–T3 diverge in provider, model, or kind.

## 2. The deeper conflict — two routing planes, and `hermes3:8b` is in neither

The estate actually runs **two** routing planes (both in `multi-router-matrix.yaml`):

1. **Claude-Code Agent router** (`claude_agent_tiers`): T0 Ollama llama3.2 → T1 **Featherless Hermes-3** → T2 OpenAI → T3 Gemini → T4 Claude. Tiers 1–3 are **cloud-hosted**.
2. **Gen `/api/delegate`** (`gen_task_intents`): local-first probe chains using **qwen2.5-coder:14b/7b, gemma3:4b, qwen3:4b/8b, deepseek-r1:8b** → claude. These are the **actually-local** models.

The scaffold `MODEL_TIER_MAP` (local Hermes, local Qwen Coder) reads like the **Gen plane**, not the Claude Code Agent router. But the specific model it wants to register — **`hermes3:8b` as a local Ollama worker** — appears in **neither** plane:
- Claude Agent T1 runs **Hermes-3 via Featherless** (cloud), not a local `hermes3:8b`.
- Gen local chains run **qwen/gemma/deepseek**, not `hermes3:8b`.

So `mission-001` would register a local model that nothing currently dispatches to.

## 3. Decision required before HERMES-003 can proceed (escalation)

Pick the routing plane and the Hermes identity. Options:

- **(A) Map "Hermes" to the existing Featherless T1.** No new local model; the capability registry describes the *live* Claude-Code Agent tiers (Ollama-T0, Featherless-Hermes-T1, OpenAI-T2, Gemini-T3, Claude-T4). The scaffold `MODEL_TIER_MAP` is superseded by `multi-router-matrix.yaml`. Lowest risk; no Ollama change. **Recommended** unless a genuinely local Hermes worker is wanted.
- **(B) Stand up a real local `hermes3:8b` in Ollama** and add it as a *new* T0/T1 local worker in the Gen plane (alongside qwen/gemma). Requires pulling the model and a Gen-plane change — bigger scope, real benefit only if local agentic throughput is the goal.
- **(C) Drop `hermes3:8b`; use the already-local `qwen2.5-coder` workers** for the "local agentic worker" role the scaffold envisioned. The capability registry then documents the Gen local chains as-is.

Any option also requires deciding **which file is the registry of record** — the live router has no `model-capabilities.yaml`; capability lives implicitly in `multi-router-matrix.yaml` (`when:` clauses) and `gen_task_intents`. Inventing a parallel `hermes-model-capability.yaml` risks a third drift source (the very thing PDR-008 exists to prevent).

## 4. What this finding did / did not do

- ✅ Read-only comparison of live router vs scaffold tier map. **No live router file modified** (`multi-router-matrix.yaml`, `provider-tiers.json`, `router-patterns.json`, `model-router.sh` all untouched).
- ⛔ Did **not** author `hermes-model-capability.yaml` or wire anything to the router — the stop condition fired.
- ⛔ Did **not** alter the Gen routing matrix.

## 4a. Resolution (2026-06-16)

**Decision: Option B — stand up a real local `hermes3:8b` in Ollama** as a new local agentic worker on the Gen / local plane. Chosen by the decision owner.

Consequences:
- `hermes3:8b` is pulled into local Ollama (`ollama pull hermes3:8b`) and verified to run.
- The **registry of record** for local-worker capabilities is `.03_Harness Governance/config/hermes-model-capability.yaml` (this file is authored by HERMES-003).
- The Claude-Agent cloud tiers remain owned by the live matrix and are **not** edited by HERMES-003; the local Ollama `hermes3:8b` is the local counterpart of the Featherless-hosted `NousResearch/Hermes-3-Llama-3.1-8B` (same family, two planes).
- **Wiring** `hermes3:8b` into the live Gen routing matrix is deferred to **HERMES-004** (additive, dry-run + diff; stop if it alters non-Hermes routing).
- `hermes3:8b` stays C1/C2 until a `hermes_evaluation_result` scorecard (HERMES-005) earns it C3+.

## 5. Follow-up

- ✅ **Decision made:** Option B (see §4a). Registry of record = `config/hermes-model-capability.yaml`.
- Once decided, **re-scope HERMES-003** as: "Document Hermes capability against the *live* router plane chosen in §3" — likely a small edit to `multi-router-matrix.yaml`'s `when:` clauses (option A) rather than a new YAML file.
- **HERMES-004** (routing patch) stays blocked until §3 is resolved — its dry-run target depends on which plane HERMES-003 lands in.
- Amend PDR-008 Decision 2 to state the live router (`multi-router-matrix.yaml`) is authoritative over the scaffold `MODEL_TIER_MAP.md`, and that the capability "registry" is the matrix's `when:` clauses, not a new file (unless option B is chosen).
