# PDR: Hermes Local Agent Worker for Chromatic Harness v2

## Status

Proposed for local-agent implementation.

## Decision Summary

Integrate Hermes as a governed local/Ollama model option for operational C1/C2 work inside `chromatic-harness-v2`.

Hermes is not a new agent identity. It is a router-selectable model used by existing harness agents.

## Problem

The harness has many repetitive operational tasks that do not require premium frontier models:

- bead triage
- handoff summarization
- mission packet generation
- validation checklist drafting
- documentation cleanup
- context compaction summaries
- simple structured classification

Current local routing already uses models such as Llama and Qwen. Hermes may provide better agentic instruction-following for operations work while preserving local-first cost and privacy advantages.

## Goals

1. Add Hermes to the model capability registry.
2. Route Hermes for C1/C2 local operational work.
3. Keep Qwen as the preferred local coding worker.
4. Keep C3/C4 reasoning on stronger models unless validation proves Hermes can safely handle selected subcases.
5. Add a validation protocol before promotion to default operational worker.
6. Preserve existing privacy, cost, confidence, and governance gates.

## Non-Goals

- Do not replace Claude/GPT/Gemini/Kimi for deep reasoning.
- Do not make Hermes a top-level agent role.
- Do not bypass beads, mission packets, or governance gates.
- Do not route secrets or high-sensitivity data differently because Hermes is local.
- Do not add OpenRouter Hermes routes until local evaluation passes.

## Architecture

Current mental model:

```text
Agent Role -> Router -> Provider -> Model -> Bounded Task -> Validation -> Bead Update
```

Hermes should enter at the model level:

```text
Agent Role -> Router -> ollama_local:hermes3:8b -> C1/C2 operational task
```

## Recommended Model ID

Use the actual local Ollama tag installed on the machine. Initial candidate:

```text
hermes3:8b
```

If the installed tag differs, update the routing patch to match `ollama list`.

## Complexity Placement

| Complexity | Hermes Default | Reason |
|---|---:|---|
| C1 | Yes | Mechanical transformation and summaries |
| C2 | Yes | Structured operations and bounded checklists |
| C3 | No by default | Needs benchmark evidence first |
| C4 | No | Keep on frontier/deep reasoning models |

## Privacy Placement

Hermes via local Ollama may handle local privacy classes permitted by the existing provider policy. However, evaluation tasks should start at P0/P1/P2 only until the workflow is validated.

## Routing Rules

Recommended first routing changes:

- Add Hermes before Llama for C1 local operational work.
- Add Hermes before Qwen only for C2 operations work.
- Keep Qwen before Hermes for C2 coding work if routing becomes task-type aware.
- Do not route Hermes to C3/C4 without explicit benchmark promotion.

## Implementation Files

Likely target files:

```text
09_DEPLOYMENT/config/routing/model-capabilities.yaml
09_DEPLOYMENT/config/routing/routing-table.yaml
tests/test_hermes_routing_policy.py
docs/governance/HERMES_ROUTING_POLICY.md
docs/validation/HERMES_EVALUATION_PROTOCOL.md
```

## Testing Strategy

### Unit Tests

- Provider selector returns Hermes for local desktop C1 balance mode when Ollama is reachable.
- Provider selector returns Hermes for local desktop C2 balance mode for non-code operational tasks, if task-type support exists.
- Provider selector does not return Hermes for C3/C4 default routes.
- Hermes model ID is present in capability registry.

### Smoke Tests

Run 10 examples each:

1. bead triage summary
2. mission packet generation
3. handoff compression
4. governance checklist validation
5. documentation cleanup

### Benchmark Comparison

Compare Hermes against:

- `llama3.1:8b`
- `qwen2.5-coder:14b`

Metrics:

- task success rate
- malformed JSON rate
- acceptance criteria coverage
- average latency
- retry rate
- hallucinated file/path rate
- governance violation rate

## Promotion Criteria

Hermes may become default local operational worker if:

- success rate >= 90% on C1 tasks
- success rate >= 80% on C2 operational tasks
- malformed output rate <= 5%
- governance violation rate = 0 critical violations
- hallucinated file/path rate <= 5%
- average latency is meaningfully better than Qwen 14B or quality is meaningfully better than Llama 8B

## Rollback Plan

If Hermes underperforms:

1. Remove Hermes from routing-table defaults.
2. Keep model capability entry as experimental.
3. Create a follow-up bead for prompt/template improvements.
4. Restore previous routing order.

## Open Questions

1. Which Hermes tag should be standardized locally: `hermes3:8b`, `nous-hermes2`, or another installed model?
2. Should task type be added to routing beyond C-level, e.g. `ops`, `coding`, `docs`, `governance`?
3. Should Hermes be benchmarked through Ollama only, or also through LM Studio?
4. Should Hermes be allowed in remote desktop routes on the future RTX 4090 rig?

## Final Recommendation

Proceed with a controlled evaluation. Add Hermes as an experimental local C1/C2 operational worker, validate it against Llama and Qwen, and only then promote it to default local agent-ops routing.
