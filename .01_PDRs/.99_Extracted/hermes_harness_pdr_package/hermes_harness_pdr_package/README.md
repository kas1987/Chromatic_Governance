# Hermes Local Agent Worker Integration Kit

## Purpose

This package gives local agents enough context to implement Hermes as a governed local worker model inside `kas1987/chromatic-harness-v2`.

Hermes should not become a new top-level agent. It should become a router-selectable local model for C1/C2 operational work.

## Intended Repo

```text
kas1987/chromatic-harness-v2
```

## Integration Summary

Add Hermes as a T0 local/Ollama worker model for:

- bead triage
- mission packet generation
- handoff summarization
- governance checklist validation
- documentation cleanup
- lightweight classification
- local agent operations

Keep Qwen as the preferred local coding model. Keep Claude/GPT/Gemini/Kimi for C3/C4 reasoning, architecture, and high-risk governance work.

## Source Observations From Harness Review

The harness already supports the required integration seams:

- canonical execution flow: `Pre-session -> Beads -> Mission Packet -> Governance Gates -> Routing -> Execution -> Magnets -> Beads Update -> Validation -> Push -> Handoff`
- provider routing based on runtime context, C-level, privacy class, budget, and model registry
- local-first provider order with Ollama/LM Studio before broker/API fallback
- capability registry in `09_DEPLOYMENT/config/routing/model-capabilities.yaml`
- route table in `09_DEPLOYMENT/config/routing/routing-table.yaml`

## File Map

| File | Purpose |
|---|---|
| `08_PDRS/PDR_HERMES_LOCAL_AGENT_WORKER.md` | Main project design record |
| `12_HANDOFFS/HERMES_IMPLEMENTATION_PLAN.md` | Implementation sequence and control gates |
| `12_HANDOFFS/agent_packets/*.md` | Agent-specific mission packets |
| `09_DEPLOYMENT/config/routing/hermes-routing-patch.example.yaml` | Example routing patch |
| `09_DEPLOYMENT/config/routing/hermes-model-capability.example.yaml` | Example capability registry patch |
| `docs/governance/HERMES_ROUTING_POLICY.md` | Governance policy for Hermes routing |
| `docs/validation/HERMES_EVALUATION_PROTOCOL.md` | Benchmark and validation plan |
| `scripts/hermes_smoke_test_plan.md` | Manual smoke test plan |
| `schemas/hermes_evaluation_result.schema.json` | Result schema for local benchmark runs |

## Recommended First Bead

```text
chromatic-harness-v2-hermes-evaluation
```

## Recommended Acceptance Criteria

- Hermes profile exists in model capability registry.
- Routing table includes Hermes for local C1/C2 operations.
- Hermes is not routed to C3/C4 by default.
- Provider selector tests prove Hermes is selected when Ollama is reachable.
- Validation report compares Hermes against Llama 3.1 8B and Qwen 2.5 Coder 14B for C1/C2 tasks.
- No P3+ privacy work routes to cloud/broker without explicit policy approval.
