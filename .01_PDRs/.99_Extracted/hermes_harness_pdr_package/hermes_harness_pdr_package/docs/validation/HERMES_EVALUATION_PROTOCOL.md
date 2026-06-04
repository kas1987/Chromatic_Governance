# Hermes Evaluation Protocol

## Purpose

Evaluate whether Hermes should become the default local operational worker model for Chromatic Harness v2.

## Models Compared

- `hermes3:8b`
- `llama3.1:8b`
- `qwen2.5-coder:14b`

## Task Classes

| Task Class | Count | Complexity |
|---|---:|---|
| Bead triage summary | 20 | C1 |
| Handoff compression | 20 | C1 |
| Mission packet generation | 20 | C2 |
| Governance checklist validation | 20 | C2 |
| Documentation cleanup | 20 | C2 |

Total: 100 tasks per model.

## Metrics

| Metric | Target |
|---|---:|
| C1 success rate | >= 90% |
| C2 operational success rate | >= 80% |
| Malformed structured output | <= 5% |
| Hallucinated file/path references | <= 5% |
| Critical governance violations | 0 |
| Retry rate | <= 15% |

## Required Result Fields

Use:

```text
schemas/hermes_evaluation_result.schema.json
```

## Review Decision

| Result | Action |
|---|---|
| Meets all targets | Promote to default local C1/C2 ops worker |
| Misses minor target | Keep experimental, adjust prompts/templates |
| Governance violation | Remove from routing defaults |
| Hallucination > 5% | Keep docs only, block routing promotion |

## Evidence Requirements

Every benchmark run must preserve:

- prompt/task input
- model ID
- output
- pass/fail score
- failure reason
- latency estimate if available
- evaluator notes
